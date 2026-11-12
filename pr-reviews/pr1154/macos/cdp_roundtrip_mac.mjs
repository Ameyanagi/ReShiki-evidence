// node cdp_roundtrip.mjs <browser-exe> <probe.html> <port> <userdir> : paste into a contenteditable, then select it and copy it back out.
import { spawn } from 'node:child_process';
const [exe, page, port, dir] = process.argv.slice(2);
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
const key = async (k, code, vk, cmd) => {
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: k, code, windowsVirtualKeyCode: vk, modifiers: 4, commands: [cmd] });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: k, code, windowsVirtualKeyCode: vk, modifiers: 4 });
};
await send('Page.bringToFront');
await send('Runtime.evaluate', { expression: "document.getElementById('ed').focus()" });
await key('v', 'KeyV', 86, 'paste');
let result;
for (let i = 0; i < 60; i++) { await sleep(300); result = (await send('Runtime.evaluate', { expression: 'JSON.stringify(window.__result)', returnByValue: true })).result?.result?.value; if (result && result !== 'null') break; }
const img = (await send('Runtime.evaluate', { expression: "(() => { const i = document.querySelector('#ed img'); if (!i) return null; const s = i.src; return { scheme: s.slice(0, s.indexOf(':')), length: s.length, reshiki: i.hasAttribute('data-reshiki'), payloadInSrc: s.startsWith('data:image/png;base64,') ? atob(s.slice(22)).includes('dev.reshiki.drawing') : null }; })()", returnByValue: true })).result?.result?.value;
await send('Runtime.evaluate', { expression: "(() => { const r = document.createRange(); r.selectNodeContents(document.getElementById('ed')); const s = getSelection(); s.removeAllRanges(); s.addRange(r); })()" });
await key('c', 'KeyC', 67, 'copy');
await sleep(1500);
const version = (await (await fetch(`http://127.0.0.1:${port}/json/version`)).json()).Browser;
console.log(JSON.stringify({ browser: version, pasted: result && result !== 'null' ? JSON.parse(result) : 'no paste event', insertedImg: img }));
await send('Browser.close').catch(() => {});
ws.close(); setTimeout(() => { try { child.kill(); } catch {} process.exit(0); }, 1000);
