// Minimal Chrome DevTools Protocol helper shared by the browser scripts (Node >= 22, no dependencies).
import { spawn } from 'node:child_process';
import { existsSync, readdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir, homedir } from 'node:os';
import { join } from 'node:path';

export const sleep = ms => new Promise(r => setTimeout(r, ms));

export function chromePath() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const base = join(homedir(), '.cache', 'ms-playwright');
  if (existsSync(base)) {
    for (const d of readdirSync(base).filter(d => d.startsWith('chromium-')).sort().reverse()) {
      for (const p of ['chrome-linux64/chrome', 'chrome-linux/chrome', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium']) {
        if (existsSync(join(base, d, p))) return join(base, d, p);
      }
    }
  }
  throw new Error('Chromium not found: set CHROME_PATH (or `npx playwright install chromium`).');
}

/**
 * Launch headless Chromium with an isolated profile (a shared profile makes the new process hand off
 * to an existing instance and exit). Options: width, height, mobile, hover (emulate a mouse), timeout.
 */
export async function launch({ width = 1440, height = 900, mobile = false, hover = false, timeout = 120000 } = {}) {
  const port = 9300 + Math.floor(Math.random() * 600);
  const profile = mkdtempSync(join(tmpdir(), 'cdp-'));
  const args = ['--headless=new', '--no-sandbox', '--hide-scrollbars', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`];
  if (hover) args.push('--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4');
  const proc = spawn(chromePath(), [...args, 'about:blank'], { stdio: 'ignore' });
  const kill = () => { try { proc.kill('SIGKILL'); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };
  const timer = setTimeout(() => { console.error('timeout'); kill(); process.exit(2); }, timeout);
  let targets;
  for (let i = 0; i < 100 && !targets; i++) {
    try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); } catch { await sleep(150); }
  }
  if (!targets) { kill(); throw new Error('Chromium did not start'); }
  const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => (ws.onopen = r));
  let id = 0; const pending = new Map(); const listeners = [];
  ws.onmessage = m => {
    const d = JSON.parse(m.data);
    if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
    else if (d.method) listeners.forEach(fn => fn(d));
  };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 300));
    return r.result.result.value;
  };
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile });
  return {
    send, ev, on: fn => listeners.push(fn),
    async goto(url, wait = 7000) { await send('Page.navigate', { url }); await sleep(wait); },
    async scrollAll(step = 250, pause = 140) {
      await ev(`(async()=>{for(let y=0;y<document.body.scrollHeight;y+=${step}){scrollTo(0,y);await new Promise(r=>setTimeout(r,${pause}));}})()`);
    },
    close() { clearTimeout(timer); kill(); },
  };
}
