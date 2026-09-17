import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm, symlink, mkdir, truncate } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Readable, Writable } from 'node:stream';
import { spawn } from 'node:child_process';
import { uploadFile, uploadTool } from '../plugins/ennoia/mcp/file-uploader.mjs';

const server = new URL('../plugins/ennoia/mcp/file-uploader.mjs', import.meta.url);
const url = 'https://mcp.ennoia.so/rag/uploads/opaque-id_123';
const token = 'secret-upload-token';
async function fixture(t, name = 'document.pdf', bytes = Buffer.alloc(160000, 42)) {
  const dir = await mkdtemp(join(tmpdir(), 'ennoia-upload-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const local_path = join(dir, name);
  await writeFile(local_path, bytes);
  return { local_path, upload_url: url, headers: {
    'X-Ennoia-Upload-Token': token, 'Content-Type': 'application/pdf', 'Content-Length': String(bytes.length),
  } };
}
function transport({ status = 200, body = '{"ok":true,"data":{"file_seq":7}}', failure, early = false } = {}) {
  const calls = [];
  const request = (target, options, onResponse) => {
    const call = { target, options, chunks: [] };
    calls.push(call);
    const respond = () => {
      if (failure) { req.destroy(new Error(failure)); return; }
      const response = Readable.from([Buffer.from(body)]);
      response.statusCode = status;
      response.headers = { location: 'https://evil.example/steal' };
      onResponse(response);
    };
    const req = new Writable({
      autoDestroy: false,
      write(chunk, encoding, callback) { call.chunks.push(Buffer.from(chunk)); setImmediate(callback); },
      final(callback) { callback(); if (!early) setImmediate(respond); },
    });
    req.setTimeout = () => req;
    if (early) setImmediate(respond);
    return req;
  };
  return { request, calls };
}

test('stdio initializes, ignores notification, lists exact tool and returns safe tool errors', async () => {
  const child = spawn(process.execPath, [server.pathname], { stdio: ['pipe', 'pipe', 'pipe'] });
  let output = '', errors = '';
  child.stdout.on('data', chunk => output += chunk);
  child.stderr.on('data', chunk => errors += chunk);
  const messages = [
    { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'test', version: '1' } } },
    { jsonrpc: '2.0', method: 'notifications/initialized' },
    { jsonrpc: '2.0', id: 2, method: 'tools/list' },
    { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'upload_ennoia_rag_file', arguments: { local_path: '/missing.pdf', upload_url: url, headers: {} } } },
    { jsonrpc: '2.0', id: 4, method: 'tools/call', params: { name: 'unknown', arguments: {} } },
  ];
  child.stdin.end(messages.map(x => JSON.stringify(x)).join('\n') + '\n');
  assert.equal(await new Promise(resolve => child.on('close', resolve)), 0);
  assert.equal(errors, '');
  const replies = output.trim().split('\n').map(JSON.parse);
  assert.equal(replies.length, 4);
  assert.equal(replies[0].result.protocolVersion, '2025-03-26');
  assert.deepEqual(replies[0].result.capabilities, { tools: {} });
  assert.deepEqual(replies[0].result.serverInfo, { name: 'ennoia-file-uploader', version: '1.4.2' });
  const [tool] = replies[1].result.tools;
  assert.equal(tool.name, 'upload_ennoia_rag_file');
  assert.deepEqual(tool.inputSchema.required, ['local_path', 'upload_url', 'headers']);
  assert.deepEqual(Object.keys(tool.inputSchema.properties), ['local_path', 'upload_url', 'headers']);
  assert.match(tool.description, /device host/);
  assert.match(tool.description, /웹 업로드/);
  const uploadError = replies.find(reply => reply.id === 3).result;
  assert.equal(uploadError.isError, true);
  assert.equal(uploadError.structuredContent.code, 'HEADERS_INVALID');
  assert.match(uploadError.structuredContent.next_action, /prepare_rag_document_upload/);
  assert.equal(uploadError.content[0].text, JSON.stringify(uploadError.structuredContent));
  assert.equal(replies.find(reply => reply.id === 4).error.code, -32602);
});

test('tool description explains uploader host visibility and web fallback', () => {
  assert.match(uploadTool.description, /이 도구가 실행되는 device host/);
  assert.match(uploadTool.description, /채팅 첨부.*cloud path/);
  assert.match(uploadTool.description, /Ennoia 웹 업로드/);
});

test('streams actual disk chunks by PUT with exact headers and returns safe file identity', async t => {
  const args = await fixture(t);
  const network = transport();
  assert.deepEqual(await uploadFile(args, network.request), { uploaded: true, status_code: 200, file_seq: 7 });
  assert.equal(network.calls.length, 1);
  const call = network.calls[0];
  assert.equal(String(call.target), url);
  assert.equal(call.options.method, 'PUT');
  assert.deepEqual(call.options.headers, args.headers);
  assert.ok(call.chunks.length > 1, '파일 전체를 한 번에 메모리로 읽지 않음');
  assert.deepEqual(Buffer.concat(call.chunks), Buffer.alloc(160000, 42));
});

for (const invalid of [
  'http://mcp.ennoia.so/rag/uploads/x', 'https://evil.example/rag/uploads/x',
  'https://mcp.ennoia.so.evil.example/rag/uploads/x', 'https://mcp.ennoia.so:444/rag/uploads/x',
  'https://user:password@mcp.ennoia.so/rag/uploads/x', 'https://mcp.ennoia.so/mcp',
  'https://mcp.ennoia.so/rag/uploads/x/more', 'https://mcp.ennoia.so/rag/uploads/%2e%2e',
  'https://mcp.ennoia.so/rag/uploads/x?token=secret', 'https://mcp.ennoia.so/rag/uploads/x#fragment',
]) test(`rejects destination ${invalid}`, async t => {
  const args = await fixture(t); const network = transport();
  await assert.rejects(uploadFile({ ...args, upload_url: invalid }, network.request), /UPLOAD_URL_INVALID/);
  assert.equal(network.calls.length, 0);
});

test('accepts dev endpoint and all supported extensions', async t => {
  for (const suffix of ['csv', 'txt', 'md', 'pdf', 'docx', 'pptx', 'xlsx', 'xls', 'zip']) {
    const args = await fixture(t, `document.${suffix}`, Buffer.from('x'));
    args.upload_url = 'https://dev-mcp-server.ennoia.so/rag/uploads/x';
    assert.equal((await uploadFile(args, transport().request)).uploaded, true);
  }
});

test('rejects unsupported suffix, empty and oversized file before network', async t => {
  for (const [name, size, code] of [['x.exe', 1, 'FILE_TYPE_UNSUPPORTED'], ['x.pdf', 0, 'FILE_SIZE_INVALID'], ['big.pdf', 104857601, 'FILE_SIZE_INVALID']]) {
    const args = await fixture(t, name, Buffer.from('x'));
    await truncate(args.local_path, size);
    args.headers['Content-Length'] = String(Math.max(1, size));
    const network = transport();
    await assert.rejects(uploadFile(args, network.request), new RegExp(code));
    assert.equal(network.calls.length, 0);
  }
});

test('rejects symlink and non-regular directory', async t => {
  const args = await fixture(t); const network = transport();
  const link = args.local_path + '.pdf';
  await symlink(args.local_path, link);
  await assert.rejects(uploadFile({ ...args, local_path: link }, network.request), /FILE_NOT_REGULAR/);
  const directory = args.local_path + '-dir.pdf';
  await mkdir(directory);
  await assert.rejects(uploadFile({ ...args, local_path: directory }, network.request), /FILE_NOT_REGULAR/);
  assert.equal(network.calls.length, 0);
});

test('distinguishes a path missing from the uploader host', async t => {
  const args = await fixture(t);
  await rm(args.local_path);
  const network = transport();
  await assert.rejects(
    uploadFile(args, network.request),
    error => error.code === 'FILE_NOT_FOUND_ON_UPLOADER_HOST',
  );
  assert.equal(network.calls.length, 0);
});

test('rejects mismatch, missing, duplicate and unsafe headers', async t => {
  const args = await fixture(t); const network = transport();
  const variants = [
    { ...args.headers, 'Content-Length': '1' }, { ...args.headers, 'Content-Length': '0160000' },
    { ...args.headers, 'content-length': '160000' }, { ...args.headers, Authorization: 'Bearer secret' },
    { ...args.headers, Host: 'evil.example' }, { ...args.headers, 'Transfer-Encoding': 'chunked' },
    { ...args.headers, 'X-Ennoia-Upload-Token': 'bad\r\nvalue' }, {},
  ];
  for (const headers of variants) await assert.rejects(uploadFile({ ...args, headers }, network.request), /HEADERS_INVALID|CONTENT_LENGTH_MISMATCH/);
  assert.equal(network.calls.length, 0);
});

for (const status of [301, 302, 303, 307, 308]) test(`rejects redirect ${status} without forwarding token`, async t => {
  const network = transport({ status });
  await assert.rejects(uploadFile(await fixture(t), network.request), /REDIRECT_REJECTED/);
  assert.equal(network.calls.length, 1);
});

test('bounds response and suppresses upstream response secrets/errors', async t => {
  const args = await fixture(t);
  await assert.rejects(uploadFile(args, transport({ body: 'x'.repeat(65537) }).request), /RESPONSE_TOO_LARGE/);
  await assert.rejects(uploadFile(args, transport({ status: 500, body: token + url }).request), err => err.message === 'UPLOAD_HTTP_500');
  await assert.rejects(uploadFile(args, transport({ failure: token + url }).request), err => err.message === 'UPLOAD_NETWORK_ERROR');
  const result = await uploadFile(args, transport({ body: JSON.stringify({ data: { file_seq: 9, upload_url: url, token } }) }).request);
  assert.deepEqual(result, { uploaded: true, status_code: 200, file_seq: 9 });
});

test('handles early redirect while file stream is still active', async t => {
  const network = transport({ status: 307, early: true });
  await assert.rejects(uploadFile(await fixture(t), network.request), /REDIRECT_REJECTED/);
  assert.equal(network.calls.length, 1);
});

test('accepts exactly 100 MiB with bounded stream chunks', async t => {
  const args = await fixture(t, 'boundary.zip', Buffer.from('x'));
  await truncate(args.local_path, 104857600);
  args.headers['Content-Length'] = '104857600';
  let bytes = 0, largest = 0;
  const request = (target, options, onResponse) => new Writable({
    autoDestroy: false,
    write(chunk, encoding, callback) { bytes += chunk.length; largest = Math.max(largest, chunk.length); callback(); },
    final(callback) {
      callback();
      const response = Readable.from(['{}']); response.statusCode = 200; onResponse(response);
    },
  });
  assert.equal((await uploadFile(args, request)).uploaded, true);
  assert.equal(bytes, 104857600);
  assert.ok(largest <= 65536);
});

test('rejects byte payload arguments and sanitizes synchronous network errors', async t => {
  const args = await fixture(t);
  await assert.rejects(uploadFile({ ...args, file_data: 'secret-bytes' }, transport().request), /ARGUMENTS_INVALID/);
  await assert.rejects(uploadFile(args, () => { throw new Error(token + url); }), err => err.message === 'UPLOAD_NETWORK_ERROR');
});

test('stdio recovers after malformed and oversized newline messages without exposing content', async () => {
  const child = spawn(process.execPath, [server.pathname], { stdio: ['pipe', 'pipe', 'pipe'] });
  let output = '', errors = '';
  child.stdout.on('data', chunk => output += chunk);
  child.stderr.on('data', chunk => errors += chunk);
  child.stdin.end('{bad-json\n' + 'x'.repeat(65537) + '\n' + JSON.stringify({ jsonrpc: '2.0', id: 10, method: 'tools/list' }) + '\n');
  assert.equal(await new Promise(resolve => child.on('close', resolve)), 0);
  assert.equal(errors, '');
  const replies = output.trim().split('\n').map(JSON.parse);
  assert.equal(replies.length, 3);
  assert.equal(replies[0].error.code, -32700);
  assert.equal(replies[1].error.code, -32600);
  assert.equal(replies[2].result.tools[0].name, 'upload_ennoia_rag_file');
  assert.ok(output.length < 4000);
});
