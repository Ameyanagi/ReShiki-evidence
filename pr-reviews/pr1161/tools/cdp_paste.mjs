// node cdp_paste.mjs <browser-exe> <probe.html> <port> <userdir>  -> prints JSON paste report
import { spawn } from 'node:child_process';
const [exe, page, port, dir, shot] = process.argv.slice(2);
const url = 'file:///' + page.replace(/\\/g, '/').replace(/^\//, '');
const child = spawn(exe, [`--remote-debugging-port=${port}`, `--user-data-dir=${dir}`, '--no-first-run', '--no-default-browser-check', '--disable-features=msEdgeStartupBoost', url], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 60 && !target; i++) {
  await sleep(500);
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page' && t.url.includes('probe')); } catch {}
}
if (!target) { console.log(JSON.stringify({ error: 'no page' })); child.kill(); process.exit(1); }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const pending = new Map();
ws.addEventListener('message', (m) => { const d = JSON.parse(m.data); if (pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } });
const send = (method, params = {}) => new Promise((r) => { const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
for (let i = 0; i < 60; i++) { const r = await send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true }); if (r.result?.result?.value === 'complete') break; await sleep(250); }
await sleep(1500);
await send('Page.bringToFront');
await send('Runtime.evaluate', { expression: "document.getElementById('ed').focus()" });
const mac = process.platform === 'darwin';
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'v', code: 'KeyV', windowsVirtualKeyCode: 86, modifiers: mac ? 4 : 2, commands: ['paste'] });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'v', code: 'KeyV', windowsVirtualKeyCode: 86, modifiers: mac ? 4 : 2 });
let result;
const t0 = Date.now(); for (let i = 0; i < 100; i++) { await sleep(300); result = (await send('Runtime.evaluate', { expression: 'JSON.stringify(window.__result)', returnByValue: true })).result?.result?.value; if (result && result !== 'null') break; }
if (shot) { await sleep(300); const png = await send('Page.captureScreenshot', { format: 'png' }); if (png.result) (await import('node:fs')).writeFileSync(shot, Buffer.from(png.result.data, 'base64')); }
const version = (await (await fetch(`http://127.0.0.1:${port}/json/version`)).json()).Browser;
console.log(JSON.stringify({ browser: version, waitedMs: Date.now() - t0, result: result && result !== 'null' ? JSON.parse(result) : 'no paste event' }, null, 1));
await send('Browser.close').catch(() => {});
ws.close(); setTimeout(() => { try { child.kill(); } catch {} process.exit(0); }, 1000);
