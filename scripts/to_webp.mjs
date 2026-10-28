#!/usr/bin/env node
// Resize / crop / convert images to WebP in headless Chromium (no ImageMagick or sharp needed).
// Usage: node to_webp.mjs spec.json
// spec.json: [{"src":"orig/car.png","out":"out/aluguel-carro-cidade.webp","w":1040,"q":0.85},
//             {"src":"orig/city.jpg","out":"out/franquia-cidade-uf.webp","w":720,"ratio":1.8,"fy":0.5,"q":0.8}]
//   w      target width (never upscales beyond the source/crop width)
//   ratio  crop to width/height ratio before resizing (centered horizontally)
//   fy     vertical focus 0..1 when cropping height (0 = top, 0.5 = center, 1 = bottom)
//   crop   explicit [sx, sy, sw, sh] instead of ratio
//   q      quality 0..1 (photos 0.8, product cut-outs 0.85, logos 0.95). Transparency is preserved.
// Always look at the outputs: a centered crop can cut the subject.
import { readFileSync, writeFileSync } from 'node:fs';
import { launch } from './cdp.mjs';

const spec = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const b = await launch({ width: 800, height: 600 });
for (const s of spec) {
  const mime = /\.png$/i.test(s.src) ? 'image/png' : /\.webp$/i.test(s.src) ? 'image/webp' : 'image/jpeg';
  const data = `data:${mime};base64,` + readFileSync(s.src).toString('base64');
  const r = await b.ev(`new Promise(res=>{const i=new Image();i.onload=()=>{
    let [sx,sy,sw,sh]=${JSON.stringify(s.crop || null)}||[0,0,i.naturalWidth,i.naturalHeight];
    const R=${s.ratio || 0};
    if(R){ if(sw/sh>R){const nw=Math.round(sh*R);sx+=Math.round((sw-nw)/2);sw=nw;} else {const nh=Math.round(sw/R);sy+=Math.round((sh-nh)*${s.fy ?? 0.5});sh=nh;} }
    const w=Math.min(${s.w},sw), h=Math.round(w*sh/sw);
    let c=document.createElement('canvas');c.width=sw;c.height=sh;c.getContext('2d').drawImage(i,sx,sy,sw,sh,0,0,sw,sh);
    while(c.width/2>w){const n=document.createElement('canvas');n.width=Math.round(c.width/2);n.height=Math.round(c.height/2);
      const x=n.getContext('2d');x.imageSmoothingQuality='high';x.drawImage(c,0,0,n.width,n.height);c=n;}
    const f=document.createElement('canvas');f.width=w;f.height=h;const fx=f.getContext('2d');fx.imageSmoothingQuality='high';fx.drawImage(c,0,0,w,h);
    res([f.toDataURL('image/webp',${s.q ?? 0.82}),w,h,i.naturalWidth+'x'+i.naturalHeight])};i.src=${JSON.stringify(data)}})`);
  const [url, w, h, orig] = r;
  const buf = Buffer.from(url.split(',')[1], 'base64');
  writeFileSync(s.out, buf);
  console.log(`${s.out}  ${orig} -> ${w}x${h}  ${Math.round(readFileSync(s.src).length / 1024)} KB -> ${Math.round(buf.length / 1024)} KB`);
}
b.close();
