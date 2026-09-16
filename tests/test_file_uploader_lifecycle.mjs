import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm, symlink, mkdir, readFile, open } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PassThrough, Writable, Readable } from 'node:stream';
import { spawn } from 'node:child_process';
import { setTimeout as delay } from 'node:timers/promises';
import { serve, uploadFile } from '../plugins/ennoia/mcp/file-uploader.mjs';

const plugin = fileURLToPath(new URL('../plugins/ennoia/', import.meta.url));
const script = join(plugin, 'mcp/file-uploader.mjs');
const list = { jsonrpc: '2.0', id: 1, method: 'tools/list' };
async function temp(t) {
  const dir = await mkdtemp(join(tmpdir(), 'ennoia-lifecycle-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  return dir;
}
async function launch(args, options = {}) {
  const child = spawn(process.execPath, args, { stdio: ['pipe', 'pipe', 'pipe'], ...options });
  let stdout = '', stderr = '';
  child.stdout.on('data', chunk => stdout += chunk);
  child.stderr.on('data', chunk => stderr += chunk);
  child.stdin.end(JSON.stringify(list) + '\n');
  const code = await new Promise(resolve => child.on('close', resolve));
  return { code, stdout, stderr };
}

for (const kind of ['file', 'parent']) test(`symlink ${kind} entry starts stdio server`, async t => {
  const dir = await temp(t);
  const link = join(dir, 'linked');
  await symlink(kind === 'file' ? script : plugin, link);
  const result = await launch([kind === 'file' ? link : join(link, 'mcp/file-uploader.mjs')]);
  assert.equal(result.code, 0);
  assert.equal(result.stderr, '');
  assert.equal(JSON.parse(result.stdout).result.tools[0].name, 'upload_ennoia_rag_file');
});

for (const host of ['claude', 'codex']) test(`generated launch resolves ${host} plugin root`, async t => {
  const dir = await temp(t);
  await mkdir(join(dir, 'mcp'));
  await writeFile(join(dir, 'mcp/file-uploader.mjs'), 'process.stdout.write("WRONG_PROJECT_SCRIPT");');
  const config = JSON.parse(await readFile(join(plugin, '.mcp.json'))).mcpServers['ennoia-file-uploader'];
  assert.equal(config.command, 'node'); assert.equal(config.cwd, '.');
  const env = { ...process.env };
  delete env.CLAUDE_PLUGIN_ROOT;
  if (host === 'claude') env.CLAUDE_PLUGIN_ROOT = plugin;
  const result = await launch(config.args, { cwd: host === 'claude' ? dir : plugin, env });
  assert.equal(result.code, 0);
  assert.equal(result.stderr, '');
  assert.equal(JSON.parse(result.stdout).result.tools[0].name, 'upload_ennoia_rag_file');
});

async function fixture(t) {
  const dir = await temp(t);
  const local_path = join(dir, 'large.pdf');
  const bytes = Buffer.alloc(4 * 1024 * 1024, 37);
  await writeFile(local_path, bytes);
  return { local_path, upload_url: 'https://mcp.ennoia.so/rag/uploads/test-id', headers: {
    'X-Ennoia-Upload-Token': 'test-token', 'Content-Type': 'application/pdf', 'Content-Length': String(bytes.length),
  } };
}
function slowNetwork() {
  let release, req, bytes = 0, calls = 0;
  let start;
  const started = new Promise(resolve => start = resolve);
  const request = (url, options, onResponse) => {
    calls++;
    req = new Writable({
      autoDestroy: false, highWaterMark: 1,
      write(chunk, encoding, callback) {
        bytes += chunk.length;
        if (!release) { release = callback; start(); } else callback();
      },
      final(callback) {
        callback();
        const response = Readable.from(['{}']); response.statusCode = 200; onResponse(response);
      },
    });
    return req;
  };
  return { request, started, release: () => release?.(), stop: () => req?.destroy(new Error('test cleanup')), get req() { return req; }, get bytes() { return bytes; }, get calls() { return calls; } };
}
function observedFiles() {
  const files = [], sources = [];
  let bytesRead = 0;
  const openFile = async (...args) => {
    const file = await open(...args); files.push(file);
    const read = file.read.bind(file);
    file.read = async (...readArgs) => { const result = await read(...readArgs); bytesRead += result.bytesRead; return result; };
    const readFile = file.readFile.bind(file);
    file.readFile = async (...readArgs) => { const result = await readFile(...readArgs); bytesRead += result.length; return result; };
    const create = file.createReadStream.bind(file);
    file.createReadStream = options => { const source = create(options); sources.push(source); return source; };
    return file;
  };
  return { openFile, files, sources, get bytesRead() { return bytesRead; } };
}
async function until(condition, message) {
  for (let i = 0; i < 50 && !condition(); i++) await delay(5);
  assert.ok(condition(), message);
}
function client(t, network, observed) {
  const input = new PassThrough(); const replies = [];
  const output = new Writable({ write(chunk, encoding, callback) { replies.push(JSON.parse(chunk.toString())); callback(); } });
  const serving = serve(input, output, { request: network.request, openFile: observed.openFile });
  t.after(async () => { input.end(); network.stop(); await serving; });
  const send = message => input.write(JSON.stringify({ jsonrpc: '2.0', ...message }) + '\n');
  return { input, replies, serving, send };
}

test('ping precedes slow upload completion and excess uploads are rejected without work', async t => {
  const network = slowNetwork(), observed = observedFiles(), c = client(t, network, observed);
  const args = await fixture(t);
  c.send({ id: 1, method: 'tools/call', params: { name: 'upload_ennoia_rag_file', arguments: args } });
  await until(() => network.bytes > 0, 'upload must start before ping');
  c.send({ id: 2, method: 'ping' });
  c.send({ id: 3, method: 'tools/call', params: { name: 'upload_ennoia_rag_file', arguments: args } });
  await until(() => c.replies.some(x => x.id === 2), 'ping must respond before network release');
  assert.ok(!c.replies.some(x => x.id === 1));
  await until(() => c.replies.some(x => x.id === 3), 'busy response must be immediate');
  assert.equal(c.replies.find(x => x.id === 3).result.content[0].text, 'UPLOAD_BUSY');
  assert.equal(network.calls, 1);
  network.release();
  await until(() => c.replies.some(x => x.id === 1), 'upload completes after release');
  assert.equal(c.replies.find(x => x.id === 1).result.structuredContent.uploaded, true);
});

test('request cancellation stops bytes and closes request, source, and fd', async t => {
  const network = slowNetwork(), observed = observedFiles(), c = client(t, network, observed);
  c.send({ id: 'upload', method: 'tools/call', params: { name: 'upload_ennoia_rag_file', arguments: await fixture(t) } });
  await until(() => network.bytes > 0, 'upload must start');
  c.send({ method: 'notifications/cancelled', params: { requestId: 'unrelated' } });
  assert.equal(network.req.destroyed, false);
  c.send({ method: 'notifications/cancelled', params: { requestId: 'upload' } });
  await until(() => network.req.destroyed && observed.files.every(x => x.fd === -1), 'cancel must close all resources');
  assert.ok(observed.sources.every(x => x.destroyed));
  const sent = network.bytes; network.release(); await delay(20);
  assert.equal(network.bytes, sent);
  assert.ok(!c.replies.some(x => x.id === 'upload'), 'cancelled request has no response');
  c.send({ id: 4, method: 'ping' });
  await until(() => c.replies.some(x => x.id === 4), 'server remains responsive');
});

test('stdin close cancels active upload and waits for fd cleanup', async t => {
  const network = slowNetwork(), observed = observedFiles(), c = client(t, network, observed);
  c.send({ id: 1, method: 'tools/call', params: { name: 'upload_ennoia_rag_file', arguments: await fixture(t) } });
  await until(() => network.bytes > 0, 'upload must start');
  c.input.end();
  await Promise.race([c.serving, delay(300).then(() => { throw new Error('stdin cleanup timed out'); })]);
  assert.ok(network.req.destroyed);
  assert.ok(observed.sources.every(x => x.destroyed));
  assert.ok(observed.files.every(x => x.fd === -1));
});

test('disk reads obey network backpressure before release', async t => {
  const network = slowNetwork(), observed = observedFiles();
  const args = await fixture(t);
  const upload = uploadFile(args, network.request, { openFile: observed.openFile });
  t.after(async () => { network.stop(); await upload.catch(() => {}); });
  await network.started;
  await delay(30);
  assert.ok(observed.bytesRead > 0, 'observe actual fd reads');
  assert.ok(observed.bytesRead < Number(args.headers['Content-Length']) / 4, 'blocked network must bound disk read-ahead');
  const bounded = observed.bytesRead;
  await delay(30);
  assert.equal(observed.bytesRead, bounded, 'disk stops reading while network stays blocked');
  network.release();
  await upload;
  assert.equal(observed.bytesRead, Number(args.headers['Content-Length']));
  assert.ok(observed.files.every(x => x.fd === -1));
});
