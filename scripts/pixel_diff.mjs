#!/usr/bin/env node
// Compare before/after screenshots.
//   node pixel_diff.mjs diff before.png after.png diff.png      -> % of changed pixels + 50px bands where changes start
//   node pixel_diff.mjs crop before.png after.png out.png x y w h [zoom]   -> stacked zoomed crops (before on top)
// A few px of page-height difference shifts everything below; find the first changed band, crop it, and
// look at it before deciding whether the change is real.
import { readFileSync, writeFileSync } from 'node:fs';
import { launch } from './cdp.mjs';

const [mode, a, b, out, ...rest] = process.argv.slice(2);
if (!['diff', 'crop'].includes(mode) || !out) { console.error('usage: see header'); process.exit(1); }
const uri = f => 'data:image/png;base64,' + readFileSync(f).toString('base64');
const br = await launch({ width: 800, height: 600 });
const load = `const L=s=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src=s});const A=await L(${JSON.stringify(uri(a))}),B=await L(${JSON.stringify(uri(b))});`;
let res;
if (mode === 'diff') {
  res = await br.ev(`(async()=>{${load}
    const w=Math.min(A.width,B.width),h=Math.min(A.height,B.height),c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
    x.drawImage(A,0,0);const da=x.getImageData(0,0,w,h).data;x.clearRect(0,0,w,h);x.drawImage(B,0,0);const img=x.getImageData(0,0,w,h),db=img.data;
    let n=0;const bands=new Set();
    for(let i=0;i<da.length;i+=4){const d=Math.abs(da[i]-db[i])+Math.abs(da[i+1]-db[i+1])+Math.abs(da[i+2]-db[i+2]);
      if(d>40){n++;db[i]=255;db[i+1]=0;db[i+2]=0;db[i+3]=255;bands.add(Math.floor(i/4/w/50)*50);}else db[i+3]=70;}
    x.putImageData(img,0,0);
    return {size:[A.width+'x'+A.height,B.width+'x'+B.height],changed:n,pct:+(n/(w*h)*100).toFixed(3),bands:[...bands].sort((p,q)=>p-q).slice(0,40),png:c.toDataURL('image/png')};})()`);
  console.log(`before ${res.size[0]} after ${res.size[1]} | changed ${res.changed} px (${res.pct}%)${res.bands.length ? ' | first bands y=' + res.bands.join(',') : ''}`);
} else {
  const [x, y, w, h, z = 1] = rest.map(Number);
  res = await br.ev(`(async()=>{${load}const Z=${z},c=document.createElement('canvas');c.width=${w}*Z;c.height=(${h}*2+6)*Z;
    const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle='#f00';g.fillRect(0,0,c.width,c.height);
    g.drawImage(A,${x},${y},${w},${h},0,0,${w}*Z,${h}*Z);g.drawImage(B,${x},${y},${w},${h},0,(${h}+6)*Z,${w}*Z,${h}*Z);return {png:c.toDataURL('image/png')};})()`);
  console.log('crop saved (before on top, after below the red line)');
}
writeFileSync(out, Buffer.from(res.png.split(',')[1], 'base64'));
br.close();
