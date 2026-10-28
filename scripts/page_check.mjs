#!/usr/bin/env node
// Live-page checks after scrolling the whole page.
// Usage: node page_check.mjs <url> [--mobile] [--images] [--broken] [--animations] [--hover-test SELECTOR]
//   --images      uploaded images: file, natural size, rendered size, object-fit; total image bytes
//   --broken      images that failed to load (ignores lazy images inside hidden elements) + HTTP >= 400
//   --animations  elements still .elementor-invisible, animated elements whose animationName is none,
//                 horizontal overflow (px)
//   --hover-test  computed transform/filter of SELECTOR before and during mouse hover (desktop pointer emulated)
// With no flag, runs --broken and --animations.
import { launch, sleep } from './cdp.mjs';

const args = process.argv.slice(2);
const url = args[0];
if (!url) { console.error('usage: page_check.mjs <url> [--mobile] [--images] [--broken] [--animations] [--hover-test SEL]'); process.exit(1); }
const mobile = args.includes('--mobile');
const hoverSel = args.includes('--hover-test') ? args[args.indexOf('--hover-test') + 1] : null;
let flags = ['--images', '--broken', '--animations'].filter(f => args.includes(f));
if (!flags.length && !hoverSel) flags = ['--broken', '--animations'];

const b = await launch({ width: mobile ? 390 : 1440, mobile, hover: !!hoverSel });
const bytes = {}, failed = [];
await b.send('Network.enable');
await b.send('Network.setCacheDisabled', { cacheDisabled: true });
const reqs = {};
b.on(d => {
  if (d.method === 'Network.responseReceived') {
    reqs[d.params.requestId] = d.params.response.url;
    if (d.params.response.status >= 400) failed.push(`${d.params.response.status} ${d.params.response.url}`);
  }
  if (d.method === 'Network.loadingFinished' && /\/uploads\//.test(reqs[d.params.requestId] || '')) bytes[reqs[d.params.requestId]] = d.params.encodedDataLength;
});
await b.goto(url);
const before = await b.ev(`document.querySelectorAll('.elementor-invisible').length`);
let overflow = 0;
for (let i = 0; i < 60; i++) {
  const r = await b.ev(`(()=>{scrollBy(0,250);return [document.documentElement.scrollWidth-innerWidth, scrollY+innerHeight>=document.body.scrollHeight]})()`);
  overflow = Math.max(overflow, r[0]); await sleep(140); if (r[1]) break;
}
await sleep(2500);
console.log(`${url} @ ${mobile ? 'mobile 390' : 'desktop 1440'}`);

if (flags.includes('--images')) {
  const rows = await b.ev(`JSON.stringify([...document.images].filter(i=>i.currentSrc.includes('/uploads/')).map(i=>{const r=i.getBoundingClientRect();
    return [i.currentSrc.split('/uploads/')[1], i.naturalWidth+'x'+i.naturalHeight, Math.round(r.width)+'x'+Math.round(r.height), getComputedStyle(i).objectFit]}))`);
  const seen = new Set();
  for (const [f, n, r, of] of JSON.parse(rows)) { const k = f + r; if (seen.has(k)) continue; seen.add(k); console.log(`  ${f.padEnd(60)} natural ${n.padEnd(10)} rendered ${r.padEnd(9)} ${of}`); }
  const tot = Object.values(bytes).reduce((a, v) => a + v, 0);
  console.log(`  image bytes from /uploads/: ${Math.round(tot / 1024)} KB in ${Object.keys(bytes).length} files`);
}
if (flags.includes('--broken')) {
  const broken = await b.ev(`JSON.stringify([...document.images].filter(i=>i.currentSrc && (!i.complete||i.naturalWidth===0) && i.offsetParent!==null).map(i=>i.currentSrc))`);
  console.log('  broken visible images:', broken);
  console.log('  HTTP >= 400:', JSON.stringify(failed.filter(u => !u.includes(url.split('?')[0]))));
}
if (flags.includes('--animations')) {
  const r = await b.ev(`JSON.stringify({stuck:[...document.querySelectorAll('.elementor-invisible')].map(e=>e.dataset.id),
    noKeyframes:[...document.querySelectorAll('.animated')].filter(e=>getComputedStyle(e).animationName==='none').map(e=>e.dataset.id).slice(0,10),
    animated:document.querySelectorAll('.animated').length})`);
  const a = JSON.parse(r);
  console.log(`  animated: ${a.animated} (invisible before scrolling: ${before}) | stuck: ${JSON.stringify(a.stuck)} | animationName none: ${JSON.stringify(a.noKeyframes)} | horizontal overflow: ${overflow}px`);
  if (a.noKeyframes.length) console.log('  -> animation CSS not enqueued (see gotchas: Element Caching)');
}
if (hoverSel) {
  const st = `(()=>{const e=document.querySelector(${JSON.stringify(hoverSel)});const c=getComputedStyle(e);return c.transform+' | '+c.filter+' | '+c.backgroundColor+' | '+c.color})()`;
  await b.ev(`document.querySelector(${JSON.stringify(hoverSel)}).scrollIntoView({block:'center'})`); await sleep(400);
  console.log('  normal:', await b.ev(st));
  const box = JSON.parse(await b.ev(`JSON.stringify(document.querySelector(${JSON.stringify(hoverSel)}).getBoundingClientRect())`));
  await b.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: box.x + box.width / 2, y: box.y + box.height / 2 }); await sleep(500);
  console.log('  hover: ', await b.ev(st));
}
b.close();
