// Bitcheque book printing: part A and part B of cheques first..last as printable HTML files, and the public
// registration file for them. Shared by the website's onboarding and the offline print page (this repo);
// the website copies this file into its assets. Needs window.BIP39 and the wallet's WebAssembly module
// (bitcheque-node/wallet-wasm: the node's own Rust, so registrations are built by the code that checks them).
//
// A book is 256 cheques from one seed. Cheque 0 is the honesty check, sent with the first registration and never
// printed; any of 1..255 can be printed, now or later, and they are registered 16 at a time.
// key[N] = SHA256("bitcheque/key" || seed || N as u16 LE), cell = SHA256("bitcheque/cell" || key[N] || col || row)[..16],
// cell -> 12 BIP-39 words and a QR code "<cheque>.<col>.<row>:<32 hex digits>" (col 0-17), so a scanner can refuse
// a box from the wrong place. Books printed before this carry the bare 32 hex digits, which scanners still accept.
(function(){
const BOOK=256, BATCH=16;
const enc=new TextEncoder(), cat=(...a)=>{const o=new Uint8Array(a.reduce((n,x)=>n+x.length,0));let i=0;for(const x of a){o.set(x,i);i+=x.length}return o};
const hex=b=>[...b].map(x=>x.toString(16).padStart(2,'0')).join('');
const sha=async b=>new Uint8Array(await crypto.subtle.digest('SHA-256',b));
const POOL=()=>window.BIP39;
async function words12(b){const h=await sha(b);let bits='';for(const x of b)bits+=x.toString(2).padStart(8,'0');bits+=(h[0]>>4).toString(2).padStart(4,'0');
  return [...Array(12)].map((_,i)=>POOL()[parseInt(bits.slice(i*11,i*11+11),2)])}
// 24 words -> the 32-byte seed, or null when a word is unknown or the checksum is wrong
async function seedFromWords(text){const w=text.trim().toLowerCase().split(/\s+/).filter(Boolean);if(w.length!==24)return null;
  let bits='';for(const x of w){const i=POOL().indexOf(x);if(i<0)return null;bits+=i.toString(2).padStart(11,'0')}
  const ent=new Uint8Array(32).map((_,i)=>parseInt(bits.slice(i*8,i*8+8),2));
  return (await sha(ent))[0]===parseInt(bits.slice(256),2)?ent:null}
// wallet wasm calls: inputs go in through `io`; read memory only after the call (it may grow and move)
function wrun(x,fn,input,raw){const p=x.io_reserve(input.length);new Uint8Array(x.memory.buffer,p,input.length).set(input);const n=x[fn]();if(!n)throw new Error(fn);
  const o=new Uint8Array(x.memory.buffer,x.io_ptr(),n).slice();return raw?o:new TextDecoder().decode(o)}
const inst=async mod=>(await WebAssembly.instantiate(mod,{})).exports;
// the lookup code: the start of the account id (public), printed on the sheets and scanned to find the number once it is final
const fmtCode=c=>c.toUpperCase().match(/.{1,4}/g).join('-');
const findURL=(c,base)=>new URL('explorer.html#code='+fmtCode(c),base||'https://bitcheque.org/').href;
function qrSvg(x,text,dark='#02050A'){const m=wrun(x,'qr',enc.encode(text),true),n=m[0],q=4;let d='';
  for(let y=0;y<n;y++)for(let i=0;i<n;i++)if(m[1+y*n+i])d+=`M${i+q} ${y+q}h1v1h-1z`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${n+2*q} ${n+2*q}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fff"/><path fill="${dark}" d="${d}"/></svg>`}
const u16=v=>[v&255,v>>8];

const COLN=[...Array(12)].map((_,i)=>'P'+(i+1)).concat(['D1','D2','D3','D4','E','F']);
const LOGO_SVG='<svg class="lg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path fill="#02050A" fill-rule="evenodd" d="M33.750 60.750 L60.237 34.263 Q62.500 32.000 60.237 29.737 L34.263 3.763 Q32.000 1.500 29.737 3.763 L3.763 29.737 Q1.500 32.000 3.763 34.263 L30.250 60.750 L30.250 33.864 A6.6 6.6 0 1 1 33.750 33.864 Z"/></svg>';
const SHEET_CSS=`@page{size:A4 landscape;margin:8mm}*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#02050A;background:#E9ECF1}
.bar{max-width:281mm;margin:8mm auto 0;padding:4mm 5mm;background:#02050A;color:#fff;border-radius:2mm;display:flex;gap:4mm;align-items:center;font-size:3.4mm}.bar b{color:#FF9341}.bar kbd{margin-left:auto;white-space:nowrap;font:600 3.4mm system-ui;color:#FF9341}
.pg{width:281mm;height:194mm;margin:8mm auto;background:#FFFDF7;padding:5mm 8mm 4mm;overflow:hidden;position:relative;break-after:page;box-shadow:0 2px 12px rgba(0,0,0,.12);display:flex;flex-direction:column}
.pg:before{content:"";position:absolute;inset:2.5mm;border:.4mm solid #02050A;border-radius:2mm;pointer-events:none}
@media print{body{background:none}.bar{display:none}.pg{margin:0;box-shadow:none}}
header{display:flex;align-items:center;gap:6mm;margin-bottom:1.5mm}.brand{display:flex;align-items:center;gap:2mm;font-size:4.6mm}.lg{width:6mm;height:6mm}
.ttl{display:flex;flex-direction:column}.ttl b{font-size:4.4mm}.ttl span{font-size:2.8mm;color:#555}
.acct{font-size:2.8mm;color:#555;display:flex;align-items:center;gap:2mm}.blank{display:inline-block;width:38mm;border-bottom:.3mm solid #02050A;height:4mm}
.lk{margin-left:auto;display:flex;align-items:center;gap:2mm;font-size:2.4mm;color:#555}.lk svg{width:18mm;height:18mm}.lk b{display:block;font:700 3mm ui-monospace,Menlo,Consolas,monospace;color:#02050A;letter-spacing:.2mm}
.stamp{font:700 2.6mm ui-monospace,Menlo,Consolas,monospace;letter-spacing:.3mm;color:#D9601F;border:.4mm solid #D9601F;border-radius:1mm;padding:1mm 2mm}
table{border-collapse:collapse;table-layout:fixed}.pA table{width:100%}.pB table{width:50%}
thead th{font:700 2.4mm ui-monospace,Menlo,Consolas,monospace;letter-spacing:.2mm;padding:.4mm 0;text-align:center}thead tr:first-child th{border-bottom:.35mm solid #02050A;text-align:left}
th.rw{width:5mm;font:600 2.8mm ui-monospace,Menlo,Consolas,monospace;color:#666}
td{border:.25mm dashed #9aa0a8;padding:0;vertical-align:top}td>.in{height:14.5mm;padding:.5mm .8mm;overflow:hidden;box-sizing:border-box}
.pos{font:700 1.85mm ui-monospace,Menlo,Consolas,monospace;color:#D9601F;margin-bottom:.2mm}
.cno{display:flex;flex-direction:column;align-items:center;justify-content:center;border:.6mm solid #02050A;border-radius:1.6mm;padding:.6mm 3mm;min-width:16mm}.cno span{font:700 2mm ui-monospace,Menlo,Consolas,monospace;letter-spacing:.4mm}.cno b{font:800 9mm/1 system-ui,-apple-system,"Segoe UI",sans-serif}
td.qc{text-align:center}td.cut .pos{color:#9aa0a8}.tpl td.cut{border-style:solid;border-color:#c9ced6}.qc .pos{text-align:left}.qc .cq{width:11.2mm;height:11.2mm;display:block;margin:.1mm auto 0}
.ws{display:flex;flex-direction:column;min-width:0;font:500 1.72mm/1.12 ui-monospace,Menlo,Consolas,monospace}.ws span{white-space:nowrap;overflow:hidden}
footer{display:flex;flex-direction:column;gap:.4mm;margin-top:1.2mm;font-size:2.4mm;color:#444}`;

const pages=(first,last)=>2*(last-first+1)+1;   // a word page and a QR page per cheque, then the cutting template

// One part of cheques first..last as a complete HTML file. `base` is the site the lookup QR code points to.
async function sheet({part,seed,first,last,mod,base}){const x=await inst(mod),cols=part==='A'?[...Array(12).keys()]:[12,13,14,15,16,17];let out='';
  const code=wrun(x,'lookup_code',seed),qr=qrSvg(x,findURL(code,base));
  // each cell also as a QR code: its position and its 16 bytes as 32 hex digits, at the highest error correction so
  // the position (cheque · column · row) can also be printed in the middle and a cut-out box still says where it came from
  const cellQR=(b,pos,label)=>{const m=wrun(x,'qr_h',enc.encode(pos+':'+hex(b).toUpperCase()),true),n=m[0],c=n/2+2;let d='';
    for(let y=0;y<n;y++)for(let i=0;i<n;){if(!m[1+y*n+i]){i++;continue}let k=i;while(k<n&&m[1+y*n+k])k++;d+=`M${i+2} ${y+2}h${k-i}v1h${i-k}z`;i=k}
    return `<svg class="cq" viewBox="0 0 ${n+4} ${n+4}" shape-rendering="crispEdges"><path d="${d}"/><rect x="${c-6.5}" y="${c-3.5}" width="13" height="7" fill="#fff"/><text x="${c}" y="${c+1.45}" text-anchor="middle" textLength="11.6" lengthAdjust="spacingAndGlyphs" font-size="4.3" font-weight="800" font-family="ui-monospace,Menlo,Consolas,monospace" shape-rendering="geometricPrecision">${label}</text></svg>`};
  const groups=part==='A'?`<th></th><th colspan="12">RECIPIENT ACCOUNT · 11 digits + check digit</th>`:`<th></th><th colspan="4">AMOUNT · 4 digits</th><th>EXP</th><th>FEE</th>`;
  const partName=part==='A'?'Part A · recipient':'Part B · amount, exponent, fee';
  const head=`<div class="acct">Account <span class="blank"></span></div><div class="lk">${qr}<span>Find your account number<b>${fmtCode(code)}</b></span></div>`;
  for(let n=Math.max(1,first);n<=last;n++){const key=   // cheque 0 is the honesty check: sent from the seed with the registration, never printed
    await sha(cat(enc.encode('bitcheque/key'),seed,new Uint8Array(u16(n))));let rows='',qrows='';
    // the sheets are drawn here in JavaScript, so each cheque is checked against the wallet's own code (the node's
    // Rust, which builds the registration): one cell per column, the row turning with the cheque number so that ten
    // cheques in a row cover every row. `cells` gives them from the cheque's key alone
    const dg=[...Array(18)].map((_,c)=>(n+c)%10),io=Uint8Array.from([...seed,...u16(n),...dg]);
    const ref=wrun(x,'cells',io).split('\n');
    if(ref.length!==18||ref.some(h=>!/^[0-9a-f]{32}$/.test(h)))throw new Error(`cheque ${n}: the wallet gave no cells. Nothing was saved`);
    for(let r=0;r<10;r++){rows+=`<tr><th class="rw">${r}</th>`;
      qrows+=`<tr><th class="rw">${r}</th>`;
      for(const c of cols){const cell=(await sha(cat(enc.encode('bitcheque/cell'),key,new Uint8Array([c,r])))).slice(0,16),w=await words12(cell);
        if(dg[c]===r&&hex(cell)!==ref[c])throw new Error(`cheque ${n}, box ${COLN[c]}·${r} differs from the wallet's own cell. Nothing was saved`);
        rows+=`<td><div class="in"><div class="pos">${COLN[c]}·${r}</div><div class="ws">${[0,2,4,6,8,10].map(i=>`<span>${w[i]} ${w[i+1]}</span>`).join('')}</div></div></td>`;
        qrows+=`<td class="qc"><div class="in"><div class="pos">${COLN[c]}·${r}</div>${cellQR(cell,`${n}.${c}.${r}`,`${n}·${COLN[c]}·${r}`)}</div></td>`}
      rows+='</tr>';qrows+='</tr>'}
    const lastOne=n===BOOK-1;
    const page=(qrPage,body)=>`<section class="pg p${part}${qrPage?' pq':''}"><header><div class="cno"><span>CHEQUE</span><b>${n}</b></div><div class="brand">${LOGO_SVG}<b>Bitcheque</b></div>
<div class="ttl"><b>${partName}${qrPage?' · QR codes':''}</b><span>Cheque ${n} of 1–${BOOK-1}${lastOne?' · LAST CHEQUE: sweep to a new book only':''}</span></div>
${head}<div class="stamp">${lastOne?'LAST CHEQUE · SWEEP ONLY':'KEEP SECRET'}</div></header>
<table><thead><tr>${groups}</tr><tr><th></th>${cols.map(c=>`<th>${COLN[c]}${c===11?' ✓':''}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table>
<footer>${lastOne?'<span><b>This is the last cheque in the book.</b> Use it only to sweep the whole balance to a new book: amount 0000, exponent 9. Spent on anything else, whatever is left in this account can never move again.</span>':''}<span>Part ${part} of 2. Printed separately from part ${part==='A'?'B':'A'}. Keep the two parts in different places.</span>${qrPage?'<span><b>The same boxes as the word page before it, as QR codes.</b> Scan one box at a time through the cutting template; never photograph the whole page.</span>':'<span><b>To sign:</b> find the row of each digit in its column, then copy that box\'s 12 words or scan its QR code on the next page. Cross out each cheque once used.</span>'}</footer></section>`;
    out+=page(false,rows)+page(true,qrows)}   // each word page is followed by its QR twin
  // last page: an empty grid laid out exactly like the QR pages. Cut holes where the boxes you need are, lay it
  // over a QR page, and a camera sees only those boxes. It holds no secret.
  const blank=[...Array(10)].map((_,r)=>`<tr><th class="rw">${r}</th>${cols.map(c=>`<td class="qc cut"><div class="in"><div class="pos">${COLN[c]}·${r}</div></div></td>`).join('')}</tr>`).join('');
  out+=`<section class="pg p${part} pq tpl"><header><div class="cno"><span>CUT</span><b>✂</b></div><div class="brand">${LOGO_SVG}<b>Bitcheque</b></div>
<div class="ttl"><b>${partName} · cutting template</b><span>For any cheque in this part</span></div>
${head}<div class="stamp">NO SECRETS</div></header>
<table><thead><tr>${groups}</tr><tr><th></th>${cols.map(c=>`<th>${COLN[c]}${c===11?' ✓':''}</th>`).join('')}</tr></thead><tbody>${blank}</tbody></table>
<footer><span><b>A mask for scanning.</b> Cut out the boxes your cheque needs, lay this sheet over that cheque's QR page so the edges line up, and scan through the holes one box at a time. The camera never sees the other boxes.</span><span>Print it on the same printer and paper as the QR pages so the boxes line up.</span></footer></section>`;
  // no script, no network and no translation service: a browser's page translator would send every word to a server
  return `<!doctype html><html lang="en" translate="no" class="notranslate"><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:"><meta name="google" content="notranslate"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bitcheque part ${part} · cheques ${Math.max(1,first)}–${last}</title><style>${SHEET_CSS}</style><body>
<div class="bar"><span><b>Secret.</b> This file holds part ${part} of cheques ${Math.max(1,first)} to ${last} of your cheque book. Print it, then delete the file and empty the trash.</span><kbd>Print: Ctrl+P · ⌘P</kbd></div>${out}</body></html>`}

// The public registration file for cheques first..last: the unmined registrations of every 16-cheque batch they
// touch, and (with the batch holding cheque 0) cheque 0, zero coins to nobody. Only public hashes; never the seed.
// A batch the chain already has is refused as a duplicate when sent, which counts as done.
async function registration({seed,first,last,mod}){const x=await inst(mod);
  const r={bitcheque:'registration',v:2,code:wrun(x,'lookup_code',seed),first,last,txs:wrun(x,'reg_txs',Uint8Array.from([...seed,...u16(first),...u16(last)])).split('\n')};
  if(first<BATCH)r.honesty=wrun(x,'honesty',seed).split('\n');
  return r}
const regName=r=>`bitcheque-registration-${fmtCode(r.code)}${r.first>=BATCH?`-${r.first}-${r.last}`:''}.json`;

function save(name,text,type){const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');
  a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)}

window.BCBook={BOOK,BATCH,sheet,registration,regName,pages,seedFromWords,fmtCode,save,
  lookupCode:async(seed,mod)=>wrun(await inst(mod),'lookup_code',seed)};
})();
