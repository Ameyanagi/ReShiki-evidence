// node browser_write.mjs <browser-exe> <port> <userdir> <variant-dir>
// Serves a localhost page and writes one ClipboardItem the way ReShiki's browser editor does, from the
// files in <variant-dir> (text_html, image_png, image_svg+xml, text_plain; each optional), then exits.
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const [exe, port, dir, variant] = process.argv.slice(2);
const types = { 'text_html': 'text/html', 'image_png': 'image/png', 'image_svg+xml': 'image/svg+xml', 'text_plain': 'text/plain' };
const order = ['text_html', 'image_png', 'image_svg+xml', 'text_plain'].filter((f) => fs.existsSync(path.join(variant, f)));
const page = `<!doctype html><title>write</title><script>
window.go = async () => { const o = {}; for (const f of ${JSON.stringify(order)}) { const t = ${JSON.stringify(types)}[f]; if (t === 'image/svg+xml' && !ClipboardItem.supports(t)) continue; o[t] = (await fetch('/p/' + encodeURIComponent(f))).blob().then((b) => new Blob([b], { type: t })); } await navigator.clipboard.write([new ClipboardItem(o)]); return Object.keys(o).join(', '); };
</script>`;
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/p/')) { res.end(fs.readFileSync(path.join(variant, decodeURIComponent(req.url.slice(3))))); return; }
  res.setHeader('content-type', 'text/html'); res.end(page);
}).listen(9420, '127.0.0.1');
const child = spawn(exe, [`--remote-debugging-port=${port}`, `--user-data-dir=${dir}`, '--no-first-run', '--no-default-browser-check', '--disable-features=msEdgeStartupBoost', 'http://127.0.0.1:9420/'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 60 && !target; i++) { await sleep(500); try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page' && t.url.includes('9420')); } catch {} }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const pending = new Map();
ws.addEventListener('message', (m) => { const d = JSON.parse(m.data); if (pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } });
const send = (method, params = {}) => new Promise((r) => { const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
const bver = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
const bws = new WebSocket(bver.webSocketDebuggerUrl); await new Promise((r) => bws.addEventListener('open', r));
bws.send(JSON.stringify({ id: 1, method: 'Browser.grantPermissions', params: { origin: 'http://127.0.0.1:9420', permissions: ['clipboardReadWrite', 'clipboardSanitizedWrite'] } }));
await sleep(500);
for (let i = 0; i < 40; i++) { const t = await send('Runtime.evaluate', { expression: 'typeof go', returnByValue: true }); if (t.result?.result?.value === 'function') break; await sleep(250); }
await send('Page.bringToFront');
const r = await send('Runtime.evaluate', { expression: 'go()', awaitPromise: true, userGesture: true, returnByValue: true });
console.log(JSON.stringify({ browser: bver.Browser, wrote: r.result?.result?.value ?? r.result?.exceptionDetails?.exception?.description }));
await sleep(1000);
await send('Browser.close').catch(() => {});
ws.close(); bws.close(); server.close(); setTimeout(() => { try { child.kill(); } catch {} process.exit(0); }, 1500);
