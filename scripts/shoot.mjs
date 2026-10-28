#!/usr/bin/env node
// Full-page screenshot with lazy content loaded and entrance animations finished.
// Usage: node shoot.mjs <url> <out.png> [--mobile] [--width 1440] [--freeze-interval 2200] [--hide "#selector,.other"]
//   --mobile            390px wide, mobile emulation
//   --freeze-interval   disables setInterval calls with that delay (stops carousels/rotators for stable diffs)
//   --hide              CSS selectors removed before the capture (floating chat buttons, cookie bars)
// Fixed headers are switched to absolute so they appear once at the top.
import { writeFileSync } from 'node:fs';
import { launch, sleep } from './cdp.mjs';

const args = process.argv.slice(2);
const [url, out] = args;
if (!url || !out) { console.error('usage: shoot.mjs <url> <out.png> [--mobile] [--width N] [--freeze-interval MS] [--hide SEL]'); process.exit(1); }
const opt = k => { const i = args.indexOf(k); return i > -1 ? args[i + 1] : undefined; };
const mobile = args.includes('--mobile');
const width = +(opt('--width') || (mobile ? 390 : 1440));
const freeze = opt('--freeze-interval');
const hide = opt('--hide');

const b = await launch({ width, mobile });
if (freeze) await b.send('Page.addScriptToEvaluateOnNewDocument', {
  source: `const _si=window.setInterval;window.setInterval=function(f,ms){return ms===${+freeze}?0:_si.apply(this,arguments)};` });
await b.goto(url);
await b.scrollAll();
await sleep(2500);
await b.ev(`(()=>{${hide ? `document.querySelectorAll(${JSON.stringify(hide)}).forEach(e=>e.remove());` : ''}
  [...document.querySelectorAll('.e-con,.elementor-location-header')].filter(e=>getComputedStyle(e).position==='fixed').forEach(e=>e.style.position='absolute');
  scrollTo(0,0)})()`);
await sleep(800);
const H = await b.ev('document.documentElement.scrollHeight');
const r = await b.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: 0, width, height: H, scale: 1 } });
writeFileSync(out, Buffer.from(r.result.data, 'base64'));
console.log(out, `${width}x${H}`);
b.close();
