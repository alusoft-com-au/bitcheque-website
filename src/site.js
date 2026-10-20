// Node replies may be cached for a few seconds at Cloudflare's edge; the browser must not keep its own copy on top,
// or pages that poll (status, explorer, top accounts) would show the same numbers until a hard refresh. So every
// request to another origin (the nodes) skips the browser cache; the site's own files are untouched.
(function(){const f=window.fetch.bind(window);window.fetch=(u,o={})=>{let x;try{x=new URL(typeof u==='string'?u:u.url,location.href).origin!==location.origin}catch(e){x=false}return f(u,x?{cache:'no-store',...o}:o)}})();
// Node replies are plain text, and some pages place parts of them into the page. A node is user-selectable,
// so a hostile one must not be able to inject markup: HTML-special characters are dropped from every reply
// that comes from another origin, whatever content type it claims. Real replies never contain them.
// Pages also escape node values where they build markup (bcEsc), so neither safeguard stands alone.
window.bcEsc=s=>String(s??'').replace(/[&<>"'`]/g,c=>'&#'+c.charCodeAt(0)+';');
(()=>{const of=window.fetch.bind(window);window.fetch=async(u,o)=>{const r=await of(u,o);
  if(new URL(r.url||String(u),location.href).origin===location.origin||[101,204,205,304].includes(r.status))return r;
  const t=(await r.text()).replace(/[<>&"'`]/g,'');return new Response(t,{status:r.status,statusText:r.statusText,headers:r.headers})}})();
// Shared: language switch (English in markup, Traditional Chinese in data-zh, the other languages in
// data-l-<code> injected by build.py from i18n/<code>.json), mobile menu.
(function(){
  const root=document.documentElement;
  // [code, native name, English name, html lang]
  const LANGS=[['en','English','English','en'],['zh','繁體中文','Chinese (Traditional)','zh-Hant'],['hans','简体中文','Chinese (Simplified)','zh-Hans'],
    ['es','Español','Spanish','es'],['pt','Português','Portuguese','pt-BR'],['fr','Français','French','fr'],['de','Deutsch','German','de'],
    ['it','Italiano','Italian','it'],['ja','日本語','Japanese','ja'],['ko','한국어','Korean','ko'],['ru','Русский','Russian','ru'],
    ['tr','Türkçe','Turkish','tr'],['id','Bahasa Indonesia','Indonesian','id'],['vi','Tiếng Việt','Vietnamese','vi']];
  const NAMES=Object.fromEntries(LANGS.map(l=>[l[0],l[1]])), HTML=Object.fromEntries(LANGS.map(l=>[l[0],l[3]]));
  const key=(p,l)=>p+l[0].toUpperCase()+l.slice(1);          // data-l-es -> dataset.lEs
  let first=true;
  function apply(lang){
    // the markup is English: an English first load has nothing to rewrite (thousands of elements on the home page)
    const rewrite=!(first&&lang==='en');first=false;
    if(rewrite)document.querySelectorAll('[data-zh]').forEach(el=>{
      if(el.dataset.en===undefined) el.dataset.en=el.innerHTML;
      const v=lang==='en'?el.dataset.en:lang==='zh'?el.dataset.zh:el.dataset[key('l',lang)];
      el.innerHTML=v!=null?v:el.dataset.en;
    });
    if(rewrite)document.querySelectorAll('[data-zh-ph]').forEach(el=>{
      if(el.dataset.enPh===undefined) el.dataset.enPh=el.placeholder;
      const v=lang==='en'?el.dataset.enPh:lang==='zh'?el.dataset.zhPh:el.dataset[key('ph',lang)];
      el.placeholder=v!=null?v:el.dataset.enPh;
    });
    root.lang=HTML[lang]||'en';
    root.dataset.lang=lang;
    document.querySelectorAll('.lang-btn').forEach(b=>b.textContent=NAMES[lang]);
    document.querySelectorAll('.lang-cur').forEach(b=>b.textContent=NAMES[lang]);
    try{localStorage.setItem('bitcheque-lang',lang)}catch(e){}
    document.dispatchEvent(new CustomEvent('langchange',{detail:lang}));
  }
  function guess(){
    for(const raw of (navigator.languages||[navigator.language||''])){
      const n=raw.toLowerCase();
      if(n.startsWith('zh')) return /hans|cn|sg|my/.test(n)?'hans':'zh';
      const b=n.split('-')[0]; if(b in NAMES) return b;
      if(b==='in') return 'id';
    }
    return 'en';
  }
  let lang='en';
  try{lang=localStorage.getItem('bitcheque-lang')||guess()}catch(e){lang=guess()}
  if(!(lang in NAMES)) lang='en';
  window.bcLangs=LANGS;
  window.bcLang=()=>root.dataset.lang||'en';
  // T(en, zh, {es:.., ...}): the build adds the third argument
  window.bcT=(en,zh,o)=>{const l=window.bcLang();return l==='en'?en:l==='zh'?zh:(o&&o[l]!=null?o[l]:en)};
  // counted words: one and many are already-translated strings; a translation may give extra forms as "few|many"
  // account numbers read like a card number: groups of four from the left
  window.bcAcct=n=>String(n).replace(/(\d{4})(?=\d)/g,'$1 ');
  window.bcP=(n,one,many)=>{const l=window.bcLang();if(l==='en'||l==='zh'||l==='hans')return n===1?one:many;
    let c='other';try{c=new Intl.PluralRules(HTML[l]).select(n)}catch(e){}
    const f=String(many).split('|');return c==='one'?one:c==='few'?f[0]:f[f.length-1]};
  // language menu: any .lang-btn / .lang-btn-x / .lang-icon opens it
  function menu(btn){
    let m=document.getElementById('langmenu');
    if(m){m.remove();return}
    m=document.createElement('div');m.id='langmenu';m.setAttribute('role','menu');
    m.innerHTML=LANGS.map(([k,v,e])=>`<button role="menuitemradio" aria-checked="${k===window.bcLang()}" data-l="${k}" lang="${HTML[k]}"><span><b>${v}</b><small>${e}</small></span>${k===window.bcLang()?'<span class="icon">check</span>':''}</button>`).join('');
    document.body.appendChild(m);
    const r=btn.getBoundingClientRect();m.style.top=(r.bottom+window.scrollY+8)+'px';m.style.left=Math.max(16,Math.min(r.right-m.offsetWidth,innerWidth-m.offsetWidth-16))+'px';
    m.addEventListener('click',e=>{const b=e.target.closest('[data-l]');if(b){apply(b.dataset.l);m.remove()}});
    setTimeout(()=>document.addEventListener('click',function c(e){if(!m.contains(e.target)){m.remove();document.removeEventListener('click',c)}}),0);
  }
  window.bcApplyLang=()=>apply(window.bcLang());
  document.addEventListener('DOMContentLoaded',()=>{
    apply(lang);
    document.querySelectorAll('.lang-btn,.lang-btn-x,.lang-icon').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();menu(b)}));
    initNav();
  });
  // ethereum.org-style menu: click or hover a trigger to open its panel; Esc and outside clicks close.
  function initNav(){
    const nav=document.querySelector('.nav'); if(!nav) return;
    const items=[...nav.querySelectorAll('.mi[aria-controls]')], sbox=nav.querySelector('.sbox'), q=nav.querySelector('#site-q'), res=nav.querySelector('#site-res');
    const close=()=>{items.forEach(b=>{b.setAttribute('aria-expanded','false');document.getElementById(b.getAttribute('aria-controls')).hidden=true});if(sbox)sbox.hidden=true};
    const open=b=>{const was=b.getAttribute('aria-expanded')==='true';close();if(!was){b.setAttribute('aria-expanded','true');document.getElementById(b.getAttribute('aria-controls')).hidden=false}};
    let t; items.forEach(b=>{b.addEventListener('click',()=>open(b));
      b.addEventListener('mouseenter',()=>{if(matchMedia('(hover:hover)').matches&&b.getAttribute('aria-expanded')!=='true'){clearTimeout(t);t=setTimeout(()=>open(b),120)}})});
    nav.addEventListener('mouseleave',()=>{clearTimeout(t);if(matchMedia('(hover:hover)').matches&&sbox.hidden)close()});
    document.addEventListener('click',e=>{if(!nav.contains(e.target))close()});
    const links=[...nav.querySelectorAll('.ml')];
    const render=()=>{const s=q.value.trim().toLowerCase();const hits=links.filter(a=>!s||a.textContent.toLowerCase().includes(s));
      res.innerHTML=hits.length?hits.map(a=>a.outerHTML).join(''):`<div class="none">${window.bcT('No results','沒有結果')}</div>`};
    const openSearch=()=>{close();sbox.hidden=false;q.value='';render();q.focus()};
    nav.querySelector('.srch').addEventListener('click',openSearch);
    q.addEventListener('input',render);
    document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch()}if(e.key==='Escape')close()});
    const mb=nav.querySelector('.menu-btn');mb.addEventListener('click',()=>{const o=nav.classList.toggle('open');document.documentElement.style.overflow=o?'hidden':'';mb.querySelector('.icon').textContent=o?'close':'menu';mb.setAttribute('aria-expanded',o)});
  }
  // keep the sticky header exactly under the sticky project banner, whatever its height
  function tnh(){const b=document.querySelector('.tnbar');if(!b)return;const set=()=>document.documentElement.style.setProperty('--tnh',b.offsetHeight+'px');set();if(window.ResizeObserver)new ResizeObserver(set).observe(b)}
  document.addEventListener('DOMContentLoaded',tnh);
  // project acknowledgement: shown until all three statements are ticked (stored per browser)
  function gate(){
    if(/\/terms(\.html)?\/?$/.test(location.pathname)) return;   // also /terms (the host drops .html)
    let ok=false;try{ok=localStorage.getItem('bitcheque-notice-ack')==='v2'}catch(e){}
    if(ok) return;
    const T=(en,zh,o)=>window.bcT(en,zh,o);
    const d=document.createElement('dialog');d.className='tgate';d.setAttribute('aria-labelledby','tg-h');
    const items=[T('Bitcheque is an experimental research project, provided as is. It is not a product or a service, and nothing about it is guaranteed to keep working.','Bitcheque 是一個實驗性研究專案，按現狀提供。它不是產品或服務，也不保證任何功能持續運作。'),
      T('Nothing here is a promise of value, service or stability. If I buy, sell or trade coins with anyone, that is my own choice and my own risk; the project does not control it and takes no responsibility for it.','這裡沒有任何價值、服務或穩定性的承諾。若我與任何人買賣或交易幣，那是我自己的選擇與風險；本專案不控制也不負責。'),
      T('I use it at my own risk. Until it is widely adopted, the network may change or be reset at any time, and I will never enter a real wallet seed or password here.','我自行承擔使用風險。在被廣泛採用之前，網路可能隨時變更或重置，我也絕不會在這裡輸入真正的錢包種子或密碼。')];
    d.innerHTML=`<div class="tg-in"><span class="tg-tag">${T('Experimental','實驗性')}</span><h2 id="tg-h">${T('Before you enter','進入之前')}</h2>
      <p>${T('Bitcheque is an experimental research project by ALUSOFT PTY LTD. It is new, and its stability is not guaranteed. Please confirm you understand:','Bitcheque 是 ALUSOFT PTY LTD 的實驗性研究專案，尚新，不保證穩定。請確認你了解：')}</p>
      <div class="tg-list">${items.map((x,i)=>`<label><input type="checkbox" data-i="${i}"><span>${x}</span></label>`).join('')}</div>
      <div class="tg-go"><a href="terms.html">${T('Read the terms of use','閱讀使用條款')}</a><button class="btn" type="button" disabled>${T('I understand, enter','我了解，進入')}</button></div></div>`;
    document.body.appendChild(d);
    d.addEventListener('cancel',e=>e.preventDefault());           // Esc cannot skip it
    const boxes=[...d.querySelectorAll('input')], go=d.querySelector('.btn');
    boxes.forEach(b=>b.addEventListener('change',()=>{b.closest('label').classList.toggle('on',b.checked);go.disabled=!boxes.every(x=>x.checked)}));
    go.addEventListener('click',()=>{try{localStorage.setItem('bitcheque-notice-ack','v2')}catch(e){}d.close();d.remove()});
    d.showModal();
  }
  document.addEventListener('DOMContentLoaded',()=>setTimeout(gate,0));
  // footer: the signature writes itself the first time the footer scrolls into view
  document.addEventListener('DOMContentLoaded',()=>{const c=document.querySelector('.fs-chq');if(!c||!('IntersectionObserver' in window))return;
    const o=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){c.classList.add('draw');o.disconnect()}},{threshold:.4});o.observe(c)});
  // back to top: appears after a screen of scrolling
  // back to top: a ring that fills as you scroll down the page; on hover the arrow flies up and a new one rises in
  function toTop(){const b=document.createElement('button');b.className='totop';b.type='button';
    b.innerHTML='<svg class="tt-ring" viewBox="0 0 52 52" aria-hidden="true"><circle class="tt-track" cx="26" cy="26" r="24"/><circle class="tt-fill" cx="26" cy="26" r="24" pathLength="100"/></svg><span class="tt-arrows"><span class="icon">arrow_upward</span><span class="icon">arrow_upward</span></span>';
    const lbl=()=>{const t=window.bcT('Back to top','回到頂端');b.setAttribute('aria-label',t);b.title=t};lbl();
    new MutationObserver(lbl).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    b.addEventListener('click',()=>window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
    const fill=b.querySelector('.tt-fill');
    const on=()=>{const max=document.documentElement.scrollHeight-innerHeight;b.classList.toggle('show',scrollY>innerHeight*.8);fill.style.strokeDashoffset=100-(max>0?Math.min(100,scrollY/max*100):0)};
    addEventListener('scroll',on,{passive:true});addEventListener('resize',on);on();document.body.appendChild(b)}
  document.addEventListener('DOMContentLoaded',toTop);
  // the node a page should talk to: the visitor's choice, else whichever listed node answers first (usually the nearest; checked once)
  let nodeProbe=null;
  window.bcNode=function(){
    try{const s=localStorage.getItem('bitcheque-rpc');if(s)return Promise.resolve(s.replace(/\/$/,''))}catch(e){}
    const list=(window.BC_NODES||[]).map(n=>n.url.replace(/\/$/,''));if(!list.length)return Promise.resolve('http://127.0.0.1:18451');
    if(!nodeProbe)nodeProbe=Promise.any(list.map(async u=>{const r=await fetch(u+'/height',{signal:AbortSignal.timeout(4000)});if(!r.ok)throw 0;return u})).catch(()=>list[0]);
    return nodeProbe};
  // say which node a page is using: a node decides what you see, so one the site does not list is flagged
  window.bcNodeNote=async el=>{if(!el)return;const u=await window.bcNode(),host=u.replace(/^https?:\/\//,'');
    const listed=(window.BC_NODES||[]).some(n=>n.url.replace(/\/$/,'')===u);el.classList.add('nodenote');el.classList.toggle('custom',!listed);
    el.textContent=listed?window.bcT(`Node: ${host}`,`節點：${host}`):window.bcT(`Node: ${host} · not one of this site's nodes. It decides what you see here, so use one you trust.`,`節點：${host} · 不是本站列出的節點。你在這裡看到的內容由它決定，請使用你信任的節點。`)};
  document.addEventListener('langchange',()=>document.querySelectorAll('.nodenote').forEach(e=>window.bcNodeNote(e)));
  // cookie notice: there are no cookies or trackers to refuse, so it informs and is dismissed once
  function cookieBar(){let seen=false;try{seen=localStorage.getItem('bitcheque-cookies')==='v1'}catch(e){}if(seen)return;
    const b=document.createElement('div');b.className='cbar';b.setAttribute('role','region');
    const fill=()=>{b.setAttribute('aria-label',window.bcT('Cookie notice','Cookie 說明'));
      b.innerHTML=`<div class="cb-head"><span class="icon">cookie</span><b>${window.bcT('No cookies, no tracking','不用 Cookie，也不追蹤')}</b></div>
        <p>${window.bcT('This site sets no cookies and runs no analytics. Your language choice and project notice are saved only in your own browser. Fonts and icons come from this site itself, not from a third party.','本站不設定 Cookie，也不做任何分析。你的語言選擇和專案確認只存在你自己的瀏覽器。字型和圖示由本站自行提供，不經第三方。')}</p>
        <div class="cb-act"><a href="terms.html#t11">${window.bcT('Privacy details','隱私說明')}<span class="icon">arrow_forward</span></a><button type="button" class="cb-ok">${window.bcT('Got it','知道了')}</button></div>`;
      b.querySelector('.cb-ok').onclick=()=>{try{localStorage.setItem('bitcheque-cookies','v1')}catch(e){}b.remove();document.documentElement.style.removeProperty('--cbh')}};
    fill();new MutationObserver(fill).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    document.body.appendChild(b);const h=()=>document.documentElement.style.setProperty('--cbh',matchMedia('(max-width:600px)').matches?b.offsetHeight+16+'px':'0px');h();if(window.ResizeObserver)new ResizeObserver(h).observe(b)}
  document.addEventListener('DOMContentLoaded',cookieBar);
})();
