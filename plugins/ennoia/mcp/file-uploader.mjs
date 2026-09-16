#!/usr/bin/env node
// 로컬 파일 byte는 JSON-RPC를 거치지 않고 HTTPS PUT stream으로 전송한다.
import { constants } from 'node:fs';
import { lstat, open, realpath } from 'node:fs/promises';
import { extname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { request as httpsRequest } from 'node:https';
import { Transform } from 'node:stream';
import { pipeline } from 'node:stream/promises';

const MAX_FILE_SIZE = 104857600;
const MAX_RESPONSE_SIZE = 65536;
const MAX_RPC_SIZE = 65536;
const UPLOAD_TIMEOUT_MS = 120000;
const EXTENSIONS = new Set(['.csv', '.txt', '.md', '.pdf', '.docx', '.pptx', '.xlsx', '.xls', '.zip']);
const HOSTS = new Set(['mcp.ennoia.so', 'dev-mcp-server.ennoia.so']);
const REQUIRED_HEADERS = new Set(['content-length', 'content-type', 'x-ennoia-upload-token']);
class UploadError extends Error {}
const fail = code => { throw new UploadError(code); };

export const uploadTool = {
  name: 'upload_ennoia_rag_file',
  description: 'prepare_rag_document_upload가 반환한 upload_url과 exact headers로 로컬 파일을 PUT합니다. local_path만 지정하고 파일 byte/base64는 MCP JSON에 넣지 않습니다. 성공 후 collection_code/file_seq로 처리 상태를 확인하세요.',
  inputSchema: {
    type: 'object', additionalProperties: false,
    properties: {
      local_path: { type: 'string', description: '사용자가 업로드를 요청한 로컬 파일 경로' },
      upload_url: { type: 'string', description: 'prepare_rag_document_upload 응답의 upload_url' },
      headers: { type: 'object', additionalProperties: { type: 'string' }, description: 'prepare 응답의 headers를 수정 없이 전달' },
    },
    required: ['local_path', 'upload_url', 'headers'],
  },
  annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
};

function validateArguments(args) {
  if (!args || typeof args !== 'object' || Array.isArray(args)
      || Object.keys(args).some(key => !['local_path', 'upload_url', 'headers'].includes(key))
      || typeof args.local_path !== 'string' || !args.local_path || args.local_path.includes('\0')) fail('ARGUMENTS_INVALID');
  if (typeof args.upload_url !== 'string') fail('UPLOAD_URL_INVALID');
  let url;
  try { url = new URL(args.upload_url); } catch { fail('UPLOAD_URL_INVALID'); }
  // URL parser의 경로 정규화, escape, query를 통한 allowlist 우회를 차단한다.
  if (url.protocol !== 'https:' || !HOSTS.has(url.hostname) || url.port || url.username || url.password
      || url.search || url.hash || !/^\/rag\/uploads\/[A-Za-z0-9_-]{1,128}$/.test(url.pathname)
      || args.upload_url !== url.href) fail('UPLOAD_URL_INVALID');
  if (!EXTENSIONS.has(extname(args.local_path).toLowerCase())) fail('FILE_TYPE_UNSUPPORTED');
  if (!args.headers || typeof args.headers !== 'object' || Array.isArray(args.headers)) fail('HEADERS_INVALID');
  const names = new Set();
  let length;
  for (const [key, value] of Object.entries(args.headers)) {
    const name = key.toLowerCase();
    if (!REQUIRED_HEADERS.has(name) || names.has(name) || typeof value !== 'string'
        || !value || /[^\x20-\x7e]|,/.test(value)) fail('HEADERS_INVALID');
    names.add(name);
    if (name === 'content-length') length = value;
  }
  if (names.size !== REQUIRED_HEADERS.size || !/^[1-9][0-9]*$/.test(length)) fail('HEADERS_INVALID');
  return { url, length };
}

async function readResponse(response) {
  if (response.statusCode >= 300 && response.statusCode < 400) {
    response.destroy(); fail('REDIRECT_REJECTED');
  }
  if (!(response.statusCode >= 200 && response.statusCode < 300)) {
    response.destroy(); fail(`UPLOAD_HTTP_${response.statusCode || 0}`);
  }
  let size = 0;
  const chunks = [];
  for await (const chunk of response) {
    size += chunk.length;
    if (size > MAX_RESPONSE_SIZE) { response.destroy(); fail('RESPONSE_TOO_LARGE'); }
    chunks.push(chunk);
  }
  // 응답 본문은 token/URL이 반사될 수 있으므로 안전한 식별자만 반환한다.
  const result = { uploaded: true, status_code: response.statusCode };
  try {
    const data = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    const seq = data?.data?.file_seq ?? data?.file_seq;
    if (Number.isSafeInteger(seq) && seq > 0) result.file_seq = seq;
  } catch { /* 비 JSON 성공 응답은 HTTP 전송 성공만 기록한다. */ }
  return result;
}

export async function uploadFile(args, request = httpsRequest, { signal, openFile = open } = {}) {
  const { url, length } = validateArguments(args);
  const checkCancellation = () => { if (signal?.aborted) fail('UPLOAD_CANCELLED'); };
  let file;
  try {
    checkCancellation();
    const before = await lstat(args.local_path);
    if (!before.isFile() || before.isSymbolicLink()) fail('FILE_INVALID');
    checkCancellation();
    // NOFOLLOW와 fd 검증으로 lstat/open 사이의 symlink 교체도 거부한다.
    file = await openFile(args.local_path, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
    const stat = await file.stat();
    checkCancellation();
    if (!stat.isFile() || stat.dev !== before.dev || stat.ino !== before.ino) fail('FILE_INVALID');
    if (stat.size < 1 || stat.size > MAX_FILE_SIZE) fail('FILE_SIZE_INVALID');
    if (length !== String(stat.size)) fail('CONTENT_LENGTH_MISMATCH');
    let req, source, incoming, timer, transfer, rejectResponse;
    const abortTransfer = code => {
      rejectResponse?.(new UploadError(code));
      source?.destroy(); req?.destroy(); incoming?.destroy();
    };
    const cancel = () => abortTransfer('UPLOAD_CANCELLED');
    try {
      const response = new Promise((resolveResponse, reject) => {
        rejectResponse = reject;
        req = request(url, { method: 'PUT', headers: args.headers }, received => {
          incoming = received;
          readResponse(incoming).then(resolveResponse, reject);
        });
        req.once('error', () => reject(new UploadError('UPLOAD_NETWORK_ERROR')));
        timer = setTimeout(() => abortTransfer('UPLOAD_TIMEOUT'), UPLOAD_TIMEOUT_MS);
      });
      let sent = 0;
      const counter = new Transform({
        transform(chunk, encoding, callback) { sent += chunk.length; callback(null, chunk); },
        flush(callback) { callback(sent === stat.size ? null : new UploadError('FILE_SIZE_CHANGED')); },
      });
      source = file.createReadStream({ autoClose: false, start: 0, end: stat.size - 1 });
      transfer = pipeline(source, counter, req);
      const completed = Promise.all([response, transfer]);
      signal?.addEventListener('abort', cancel, { once: true });
      if (signal?.aborted) cancel();
      const [result] = await completed;
      checkCancellation();
      if ((await file.stat()).size !== stat.size) fail('FILE_SIZE_CHANGED');
      return result;
    } catch (error) {
      checkCancellation();
      if (error instanceof UploadError) throw error;
      fail('UPLOAD_NETWORK_ERROR');
    } finally {
      signal?.removeEventListener('abort', cancel);
      clearTimeout(timer);
      source?.destroy(); req?.destroy(); incoming?.destroy();
      // fd close 전에 진행 중인 read와 pipeline 정리를 기다린다.
      await transfer?.catch(() => {});
    }
  } catch (error) {
    checkCancellation();
    if (error instanceof UploadError) throw error;
    fail('FILE_INVALID');
  } finally {
    await file?.close().catch(() => {});
  }
}

async function handleRpc(message, upload = uploadFile) {
  const id = message?.id ?? null;
  const error = (code, text) => ({ jsonrpc: '2.0', id, error: { code, message: text } });
  if (!message || Array.isArray(message) || message.jsonrpc !== '2.0' || typeof message.method !== 'string') return error(-32600, 'Invalid Request');
  if (!Object.hasOwn(message, 'id')) return undefined;
  const reply = result => ({ jsonrpc: '2.0', id, result });
  if (message.method === 'initialize') return reply({
    protocolVersion: ['2024-11-05', '2025-03-26', '2025-06-18'].includes(message.params?.protocolVersion) ? message.params.protocolVersion : '2025-06-18',
    capabilities: { tools: {} }, serverInfo: { name: 'ennoia-file-uploader', version: '1.4.0' },
  });
  if (message.method === 'ping') return reply({});
  if (message.method === 'tools/list') return reply({ tools: [uploadTool] });
  if (message.method !== 'tools/call') return error(-32601, 'Method not found');
  if (message.params?.name !== uploadTool.name) return error(-32602, 'Unknown tool');
  try {
    const result = await upload(message.params.arguments);
    return reply({ content: [{ type: 'text', text: JSON.stringify(result) }], structuredContent: result });
  } catch (err) {
    return reply({ isError: true, content: [{ type: 'text', text: err instanceof UploadError ? err.message : 'UPLOAD_FAILED' }] });
  }
}

export async function serve(input = process.stdin, output = process.stdout, { request = httpsRequest, openFile = open } = {}) {
  let pending = '', oversized = false, closed = false;
  // 업로드는 하나만 허용한다. Parser와 ping은 전송 완료를 기다리지 않는다.
  const active = new Map();
  const write = value => { if (value && !closed) output.write(JSON.stringify(value) + '\n'); };
  const shutdown = () => {
    closed = true;
    for (const job of active.values()) job.controller.abort();
  };
  const dispatch = message => {
    if (message?.jsonrpc === '2.0' && message.method === 'notifications/cancelled' && !Object.hasOwn(message, 'id')) {
      active.get(message.params?.requestId)?.controller.abort();
      return;
    }
    const isUpload = message?.jsonrpc === '2.0' && message.method === 'tools/call'
      && message.params?.name === uploadTool.name && Object.hasOwn(message, 'id');
    if (!isUpload) { void handleRpc(message).then(write); return; }
    if (active.size) {
      write({ jsonrpc: '2.0', id: message.id, result: { isError: true, content: [{ type: 'text', text: 'UPLOAD_BUSY' }] } });
      return;
    }
    const controller = new AbortController();
    const job = { controller, promise: undefined };
    active.set(message.id, job);
    job.promise = handleRpc(message, args => uploadFile(args, request, { signal: controller.signal, openFile }))
      .then(value => { if (!controller.signal.aborted) write(value); })
      .finally(() => active.delete(message.id));
  };
  input.setEncoding('utf8');
  input.on('end', shutdown); input.on('close', shutdown); input.on('error', shutdown);
  try {
    for await (const chunk of input) {
      for (const [index, part] of chunk.split('\n').entries()) {
        if (index > 0) {
          if (oversized) write({ jsonrpc: '2.0', id: null, error: { code: -32600, message: 'Request too large' } });
          else if (pending.trim()) {
            let message;
            try { message = JSON.parse(pending); }
            catch { write({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }); }
            if (message !== undefined) dispatch(message);
          }
          pending = ''; oversized = false;
        }
        if (!oversized) {
          pending += part;
          if (Buffer.byteLength(pending) > MAX_RPC_SIZE) { pending = ''; oversized = true; }
        }
      }
    }
  } finally {
    shutdown();
    await Promise.allSettled([...active.values()].map(job => job.promise));
    input.off('end', shutdown); input.off('close', shutdown); input.off('error', shutdown);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(await realpath(resolve(process.argv[1]))).href) {
  serve().catch(() => { process.exitCode = 1; });
}
