// Node replies may be cached for a few seconds at Cloudflare's edge; the browser must not keep its own copy on top,
// or pages that poll (status, explorer, top accounts) would show the same numbers until a hard refresh. So every
// request to another origin (the nodes) skips the browser cache; the site's own files are untouched.
(function(){const f=window.fetch.bind(window);window.fetch=(u,o={})=>{let x;try{x=new URL(typeof u==='string'?u:u.url,location.href).origin!==location.origin}catch(e){x=false}return f(u,x?{cache:'no-store',...o}:o)}})();
// Node replies are plain text, and some pages place parts of them into the page. A node is user-selectable,
// so a hostile one must not be able to inject markup: HTML-special characters are dropped from every
// plain-text reply that comes from another origin. Real replies never contain them.
(()=>{const of=window.fetch.bind(window);window.fetch=async(u,o)=>{const r=await of(u,o);
  if(new URL(r.url||String(u),location.href).origin===location.origin||!/^text\/plain/i.test(r.headers.get('content-type')||''))return r;
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
  function apply(lang){
    document.querySelectorAll('[data-zh]').forEach(el=>{
      if(el.dataset.en===undefined) el.dataset.en=el.innerHTML;
      const v=lang==='en'?el.dataset.en:lang==='zh'?el.dataset.zh:el.dataset[key('l',lang)];
      el.innerHTML=v!=null?v:el.dataset.en;
    });
    document.querySelectorAll('[data-zh-ph]').forEach(el=>{
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
      res.innerHTML=hits.length?hits.map(a=>a.outerHTML).join(''):`<div class="none">${window.bcT('No results','沒有結果',{hans:"没有结果",es:"Sin resultados",pt:"Nenhum resultado",fr:"Aucun résultat",de:"Keine Ergebnisse",it:"Nessun risultato",ja:"結果がありません",ko:"결과 없음",ru:"Ничего не найдено",tr:"Sonuç yok",id:"Tidak ada hasil",vi:"Không có kết quả"})}</div>`};
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
    const items=[T('Bitcheque is an experimental research project, provided as is. It is not a product or a service, and nothing about it is guaranteed to keep working.','Bitcheque 是一個實驗性研究專案，按現狀提供。它不是產品或服務，也不保證任何功能持續運作。',{hans:"Bitcheque 是一个实验性研究项目，按“现状”提供。它不是产品或服务，也不保证任何部分能够持续运行。",es:"Bitcheque es un proyecto de investigación experimental, ofrecido tal cual. No es un producto ni un servicio, y no se garantiza que nada de él siga funcionando.",pt:"O Bitcheque é um projeto de pesquisa experimental, fornecido no estado em que se encontra. Não é um produto nem um serviço, e nada nele tem garantia de continuar funcionando.",fr:"Bitcheque est un projet de recherche expérimental, fourni en l’état. Ce n’est ni un produit ni un service, et il n’existe aucune garantie que quoi que ce soit continue de fonctionner.",de:"Bitcheque ist ein experimentelles Forschungsprojekt und wird ohne Gewähr bereitgestellt („as is“). Es ist kein Produkt und keine Dienstleistung, und es gibt keine Garantie, dass irgendetwas daran weiter funktioniert.",it:"Bitcheque è un progetto di ricerca sperimentale, fornito così com'è. Non è un prodotto né un servizio, e non c'è alcuna garanzia che qualsiasi sua parte continui a funzionare.",ja:"Bitcheque は実験的な研究プロジェクトであり、現状のまま提供されます。製品やサービスではなく、何かが動作し続けることは一切保証されません。",ko:"Bitcheque는 있는 그대로 제공되는 실험적 연구 프로젝트입니다. 제품이나 서비스가 아니며, 계속 작동한다는 보장은 전혀 없습니다.",ru:"Bitcheque — экспериментальный исследовательский проект, предоставляемый «как есть». Это не продукт и не услуга, и нет никаких гарантий, что что-либо в нём продолжит работать.",tr:"Bitcheque, olduğu gibi sunulan deneysel bir araştırma projesidir. Bir ürün veya hizmet değildir ve hiçbir yönünün çalışmaya devam edeceği garanti edilmez.",id:"Bitcheque adalah proyek riset eksperimental, disediakan apa adanya. Ini bukan produk atau layanan, dan tidak ada bagian darinya yang dijamin akan terus berfungsi.",vi:"Bitcheque là một dự án nghiên cứu thử nghiệm, được cung cấp nguyên trạng. Nó không phải là một sản phẩm hay một dịch vụ, và không có gì về nó được bảo đảm sẽ tiếp tục hoạt động."}),
      T('Nothing here is a promise of value, service or stability. If I buy, sell or trade coins with anyone, that is my own choice and my own risk; the project does not control it and takes no responsibility for it.','這裡沒有任何價值、服務或穩定性的承諾。若我與任何人買賣或交易幣，那是我自己的選擇與風險；本專案不控制也不負責。',{hans:"这里的任何内容都不构成对价值、服务或稳定性的承诺。如果我与任何人买卖或交易币，那是我自己的选择，风险由我自己承担；本项目不控制这些行为，也不为此承担任何责任。",es:"Nada de esto es una promesa de valor, servicio o estabilidad. Si compro, vendo o intercambio monedas con alguien, es mi propia decisión y mi propio riesgo; el proyecto no lo controla y no asume ninguna responsabilidad por ello.",pt:"Nada aqui é uma promessa de valor, de serviço ou de estabilidade. Se eu comprar, vender ou negociar moedas com alguém, é escolha minha e risco meu; o projeto não controla isso e não assume nenhuma responsabilidade por isso.",fr:"Rien ici ne constitue une promesse de valeur, de service ou de stabilité. Si j’achète, vends ou échange des pièces avec qui que ce soit, c’est mon propre choix et je le fais à mes propres risques ; le projet ne le contrôle pas et décline toute responsabilité à cet égard.",de:"Nichts hier verspricht Wert, eine Dienstleistung oder Stabilität. Wenn ich mit jemandem Coins kaufe, verkaufe oder handle, ist das meine eigene Entscheidung und mein eigenes Risiko; das Projekt kontrolliert das nicht und übernimmt dafür keine Verantwortung.",it:"Niente qui costituisce una promessa di valore, di servizio o di stabilità. Se compro, vendo o scambio monete con qualcuno, è una mia scelta e un mio rischio; il progetto non lo controlla e non se ne assume alcuna responsabilità.",ja:"ここにあるものは何ひとつ、価値、サービス、安定性を約束するものではありません。私が誰かとコインを売買または交換する場合、それは私自身の選択であり、私自身のリスクです。プロジェクトはそれを管理せず、一切の責任を負いません。",ko:"이곳의 어떤 것도 가치, 서비스, 안정성을 약속하지 않습니다. 제가 누군가와 코인을 사고팔거나 거래한다면 그것은 저 자신의 선택이자 저 자신의 위험이며, 프로젝트는 이를 통제하지 않고 이에 대해 어떠한 책임도 지지 않습니다.",ru:"Ничто здесь не является обещанием ценности, услуги или стабильности. Если я покупаю, продаю или обмениваю монеты с кем-либо, это мой собственный выбор и мой собственный риск; проект это не контролирует и не несёт за это никакой ответственности.",tr:"Buradaki hiçbir şey bir değer, hizmet veya istikrar vaadi değildir. Herhangi biriyle coin alır, satar veya takas edersem bu benim kendi tercihim ve kendi riskimdir; proje bunu kontrol etmez ve bunun için hiçbir sorumluluk kabul etmez.",id:"Tidak ada apa pun di sini yang menjanjikan nilai, layanan, atau stabilitas. Jika saya membeli, menjual, atau memperdagangkan koin dengan siapa pun, itu adalah pilihan saya sendiri dan risiko saya sendiri; proyek ini tidak mengendalikannya dan tidak bertanggung jawab atasnya.",vi:"Không có gì ở đây là lời hứa về giá trị, dịch vụ hay sự ổn định. Nếu tôi mua, bán hay trao đổi coin với bất kỳ ai, đó là lựa chọn của riêng tôi và rủi ro của riêng tôi; dự án không kiểm soát việc đó và không chịu trách nhiệm gì về việc đó."}),
      T('I use it at my own risk. Until it is widely adopted, the network may change or be reset at any time, and I will never enter a real wallet seed or password here.','我自行承擔使用風險。在被廣泛採用之前，網路可能隨時變更或重置，我也絕不會在這裡輸入真正的錢包種子或密碼。',{hans:"我自行承担使用风险。在被广泛采用之前，网络可能随时变更或重置，并且我绝不会在这里输入真实的钱包种子或密码。",es:"Lo uso bajo mi propio riesgo. Hasta que se adopte ampliamente, la red puede cambiar o reiniciarse en cualquier momento, y nunca introduciré aquí la semilla ni la contraseña de una cartera real.",pt:"Uso por minha conta e risco. Até que seja amplamente adotada, a rede pode mudar ou ser reiniciada a qualquer momento, e nunca vou digitar aqui uma semente ou senha de carteira real.",fr:"Je l’utilise à mes propres risques. Tant qu’il n’est pas largement adopté, le réseau peut changer ou être réinitialisé à tout moment, et je ne saisirai jamais ici la graine ou le mot de passe d’un vrai portefeuille.",de:"Ich nutze es auf eigenes Risiko. Bis zu einer breiten Nutzung kann sich das Netzwerk jederzeit ändern oder zurückgesetzt werden, und ich werde hier niemals einen echten Wallet-Seed oder ein echtes Passwort eingeben.",it:"Lo uso a mio rischio. Finché non sarà ampiamente adottata, la rete potrà cambiare o essere azzerata in qualsiasi momento, e non inserirò mai qui il seed o la password di un vero wallet.",ja:"私は自己責任で利用します。広く普及するまでは、ネットワークはいつでも変更またはリセットされる可能性があり、私はここに本物のウォレットのシードやパスワードを決して入力しません。",ko:"저는 제 책임하에 사용합니다. 널리 채택되기 전까지 네트워크는 언제든 변경되거나 초기화될 수 있으며, 저는 이곳에 실제 지갑 시드나 비밀번호를 절대 입력하지 않겠습니다.",ru:"Я использую его на свой страх и риск. Пока проект не получил широкого распространения, сеть может измениться или быть сброшена в любой момент, и я никогда не буду вводить здесь настоящую сид-фразу кошелька или пароль.",tr:"Kendi riskimle kullanıyorum. Yaygın olarak benimsenene kadar ağ her an değişebilir veya sıfırlanabilir ve buraya asla gerçek bir cüzdan tohumu veya parola girmeyeceğim.",id:"Saya menggunakannya atas risiko saya sendiri. Sampai diadopsi secara luas, jaringan dapat berubah atau disetel ulang kapan saja, dan saya tidak akan pernah memasukkan seed atau kata sandi dompet sungguhan di sini.",vi:"Tôi tự chịu rủi ro khi sử dụng. Cho đến khi được sử dụng rộng rãi, mạng lưới có thể thay đổi hoặc bị đặt lại bất cứ lúc nào, và tôi sẽ không bao giờ nhập hạt giống hay mật khẩu của ví thật vào đây."})];
    d.innerHTML=`<div class="tg-in"><span class="tg-tag">${T('Experimental','實驗性',{hans:"实验性",es:"Experimental",pt:"Experimental",fr:"Expérimental",de:"Experimentell",it:"Sperimentale",ja:"実験的",ko:"실험적",ru:"Эксперимент",tr:"Deneysel",id:"Eksperimental",vi:"Thử nghiệm"})}</span><h2 id="tg-h">${T('Before you enter','進入之前',{hans:"进入之前",es:"Antes de entrar",pt:"Antes de entrar",fr:"Avant d’entrer",de:"Bevor du fortfährst",it:"Prima di entrare",ja:"入る前に",ko:"들어가기 전에",ru:"Прежде чем войти",tr:"Girmeden önce",id:"Sebelum Anda masuk",vi:"Trước khi bạn vào"})}</h2>
      <p>${T('Bitcheque is an experimental research project by ALUSOFT PTY LTD. It is new, and its stability is not guaranteed. Please confirm you understand:','Bitcheque 是 ALUSOFT PTY LTD 的實驗性研究專案，尚新，不保證穩定。請確認你了解：',{hans:"Bitcheque 是 ALUSOFT PTY LTD 的实验性研究项目。它还很新，不保证其稳定性。请确认你了解以下内容：",es:"Bitcheque es un proyecto de investigación experimental de ALUSOFT PTY LTD. Es nuevo y su estabilidad no está garantizada. Por favor, confirma que entiendes lo siguiente:",pt:"O Bitcheque é um projeto de pesquisa experimental da ALUSOFT PTY LTD. Ele é novo, e sua estabilidade não é garantida. Por favor, confirme que você entende:",fr:"Bitcheque est un projet de recherche expérimental d’ALUSOFT PTY LTD. Il est nouveau, et sa stabilité n’est pas garantie. Veuillez confirmer que vous comprenez :",de:"Bitcheque ist ein experimentelles Forschungsprojekt von ALUSOFT PTY LTD. Es ist neu, und seine Stabilität ist nicht garantiert. Bitte bestätige, dass du Folgendes verstehst:",it:"Bitcheque è un progetto di ricerca sperimentale di ALUSOFT PTY LTD. È nuovo e la sua stabilità non è garantita. Conferma di aver capito:",ja:"Bitcheque は ALUSOFT PTY LTD による実験的な研究プロジェクトです。新しいプロジェクトであり、安定性は保証されていません。次の内容を理解したことを確認してください：",ko:"Bitcheque는 ALUSOFT PTY LTD의 실험적 연구 프로젝트입니다. 새로운 프로젝트이며 안정성은 보장되지 않습니다. 다음 내용을 이해했는지 확인해 주세요:",ru:"Bitcheque — экспериментальный исследовательский проект ALUSOFT PTY LTD. Он новый, и его стабильность не гарантируется. Пожалуйста, подтвердите, что вы понимаете:",tr:"Bitcheque, ALUSOFT PTY LTD tarafından yürütülen deneysel bir araştırma projesidir. Yenidir ve istikrarı garanti edilmez. Lütfen şunları anladığınızı onaylayın:",id:"Bitcheque adalah proyek riset eksperimental oleh ALUSOFT PTY LTD. Proyek ini masih baru, dan stabilitasnya tidak dijamin. Harap konfirmasi bahwa Anda memahami:",vi:"Bitcheque là một dự án nghiên cứu thử nghiệm của ALUSOFT PTY LTD. Dự án còn mới, và sự ổn định của nó không được bảo đảm. Vui lòng xác nhận bạn hiểu rằng:"})}</p>
      <div class="tg-list">${items.map((x,i)=>`<label><input type="checkbox" data-i="${i}"><span>${x}</span></label>`).join('')}</div>
      <div class="tg-go"><a href="terms.html">${T('Read the terms of use','閱讀使用條款',{hans:"阅读使用条款",es:"Leer los términos de uso",pt:"Ler os termos de uso",fr:"Lire les conditions d’utilisation",de:"Nutzungsbedingungen lesen",it:"Leggi le condizioni d'uso",ja:"利用規約を読む",ko:"이용 약관 읽기",ru:"Прочитать условия использования",tr:"Kullanım koşullarını okuyun",id:"Baca ketentuan penggunaan",vi:"Đọc điều khoản sử dụng"})}</a><button class="btn" type="button" disabled>${T('I understand, enter','我了解，進入',{hans:"我已了解，进入",es:"Lo entiendo, entrar",pt:"Entendo, entrar",fr:"Je comprends, entrer",de:"Verstanden, weiter",it:"Ho capito, entra",ja:"理解しました。入る",ko:"이해했습니다, 들어가기",ru:"Понимаю, войти",tr:"Anladım, siteye gir",id:"Saya mengerti, masuk",vi:"Tôi hiểu, vào trang"})}</button></div></div>`;
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
    const lbl=()=>{const t=window.bcT('Back to top','回到頂端',{hans:"返回顶部",es:"Volver arriba",pt:"Voltar ao topo",fr:"Retour en haut",de:"Nach oben",it:"Torna su",ja:"トップへ戻る",ko:"맨 위로",ru:"Наверх",tr:"Başa dön",id:"Kembali ke atas",vi:"Lên đầu trang"});b.setAttribute('aria-label',t);b.title=t};lbl();
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
    el.textContent=listed?window.bcT(`Node: ${host}`,`節點：${host}`,{hans:`节点：${host}`,es:`Nodo: ${host}`,pt:`Nó: ${host}`,fr:`Nœud : ${host}`,de:`Node: ${host}`,it:`Nodo: ${host}`,ja:`ノード：${host}`,ko:`노드: ${host}`,ru:`Узел: ${host}`,tr:`Düğüm: ${host}`,id:`Node: ${host}`,vi:`Nút: ${host}`}):window.bcT(`Node: ${host} · not one of this site's nodes. It decides what you see here, so use one you trust.`,`節點：${host} · 不是本站列出的節點。你在這裡看到的內容由它決定，請使用你信任的節點。`,{hans:`节点：${host} · 不是本站列出的节点。你在这里看到的内容由它决定，请使用你信任的节点。`,es:`Nodo: ${host} · no es uno de los nodos de este sitio. Decide lo que ves aquí, así que usa uno de confianza.`,pt:`Nó: ${host} · não é um dos nós deste site. Ele decide o que você vê aqui, então use um de confiança.`,fr:`Nœud : ${host} · ce n’est pas l’un des nœuds de ce site. C’est lui qui décide de ce que vous voyez ici : utilisez un nœud de confiance.`,de:`Node: ${host} · keiner der Nodes dieser Seite. Er bestimmt, was du hier siehst, also nutze einen, dem du vertraust.`,it:`Nodo: ${host} · non è uno dei nodi di questo sito. Decide lui cosa vedi qui, quindi usane uno di cui ti fidi.`,ja:`ノード：${host} · このサイトのノードではありません。ここに表示される内容はこのノードが決めるので、信頼できるノードを使ってください。`,ko:`노드: ${host} · 이 사이트의 노드가 아닙니다. 여기에 보이는 내용은 이 노드가 정하므로, 신뢰하는 노드를 사용하세요.`,ru:`Узел: ${host} · не из списка узлов этого сайта. Он решает, что вы здесь видите, поэтому используйте узел, которому доверяете.`,tr:`Düğüm: ${host} · bu sitenin düğümlerinden biri değil. Burada ne göreceğinize o karar verir, bu yüzden güvendiğiniz bir düğüm kullanın.`,id:`Node: ${host} · bukan salah satu node situs ini. Node inilah yang menentukan apa yang Anda lihat di sini, jadi gunakan node yang Anda percayai.`,vi:`Nút: ${host} · không phải một trong các nút của trang này. Nút này quyết định những gì bạn thấy ở đây, vì vậy hãy dùng nút bạn tin cậy.`})};
  document.addEventListener('langchange',()=>document.querySelectorAll('.nodenote').forEach(e=>window.bcNodeNote(e)));
  // cookie notice: there are no cookies or trackers to refuse, so it informs and is dismissed once
  function cookieBar(){let seen=false;try{seen=localStorage.getItem('bitcheque-cookies')==='v1'}catch(e){}if(seen)return;
    const b=document.createElement('div');b.className='cbar';b.setAttribute('role','region');
    const fill=()=>{b.setAttribute('aria-label',window.bcT('Cookie notice','Cookie 說明',{hans:"Cookie 说明",es:"Aviso sobre cookies",pt:"Aviso de cookies",fr:"Avis sur les cookies",de:"Cookie-Hinweis",it:"Informativa sui cookie",ja:"Cookie について",ko:"쿠키 안내",ru:"Уведомление о cookie",tr:"Çerez bildirimi",id:"Pemberitahuan cookie",vi:"Thông báo cookie"}));
      b.innerHTML=`<div class="cb-head"><span class="icon">cookie</span><b>${window.bcT('No cookies, no tracking','不用 Cookie，也不追蹤',{hans:"不使用 Cookie，不做跟踪",es:"Sin cookies ni rastreo",pt:"Sem cookies, sem rastreamento",fr:"Aucun cookie, aucun suivi",de:"Keine Cookies, kein Tracking",it:"Nessun cookie, nessun tracciamento",ja:"Cookie なし、トラッキングなし",ko:"쿠키 없음, 추적 없음",ru:"Без cookie и отслеживания",tr:"Çerez yok, izleme yok",id:"Tanpa cookie, tanpa pelacakan",vi:"Không cookie, không theo dõi"})}</b></div>
        <p>${window.bcT('This site sets no cookies and runs no analytics. Your language choice and project notice are saved only in your own browser. Fonts and icons load from Google Fonts, which sees your IP address.','本站不設定 Cookie，也不做任何分析。你的語言選擇和專案確認只存在你自己的瀏覽器。字型和圖示由 Google Fonts 載入，Google 會看到你的 IP 位址。',{hans:"本站不设置任何 Cookie，也不运行任何分析工具。你的语言选择和项目须知确认只保存在你自己的浏览器中。字体和图标从 Google Fonts 加载，Google Fonts 能看到你的 IP 地址。",es:"Este sitio no instala cookies ni usa herramientas de analítica. Tu elección de idioma y el aviso del proyecto se guardan solo en tu propio navegador. Las fuentes y los iconos se cargan desde Google Fonts, que ve tu dirección IP.",pt:"Este site não grava cookies nem usa ferramentas de análise. Sua escolha de idioma e o aviso do projeto ficam salvos apenas no seu próprio navegador. Fontes e ícones são carregados do Google Fonts, que vê seu endereço IP.",fr:"Ce site ne dépose aucun cookie et n’utilise aucun outil d’analyse. Votre choix de langue et l’avis sur le projet sont enregistrés uniquement dans votre propre navigateur. Les polices et les icônes se chargent depuis Google Fonts, qui voit votre adresse IP.",de:"Diese Website setzt keine Cookies und verwendet keine Analysedienste. Deine Sprachwahl und der Projekthinweis werden nur in deinem eigenen Browser gespeichert. Schriftarten und Icons werden von Google Fonts geladen, das deine IP-Adresse sieht.",it:"Questo sito non imposta cookie e non usa strumenti di analisi. La tua scelta della lingua e l'avviso sul progetto vengono salvati solo nel tuo browser. Font e icone vengono caricati da Google Fonts, che vede il tuo indirizzo IP.",ja:"このサイトは Cookie を設定せず、アクセス解析も行いません。言語の選択とプロジェクトのお知らせの確認状態は、あなた自身のブラウザにだけ保存されます。フォントとアイコンは Google Fonts から読み込まれ、Google Fonts にはあなたの IP アドレスが見えます。",ko:"이 사이트는 쿠키를 설정하지 않고 분석 도구도 실행하지 않습니다. 언어 선택과 프로젝트 안내 확인은 내 브라우저에만 저장됩니다. 글꼴과 아이콘은 Google Fonts에서 불러오며, Google Fonts는 IP 주소를 볼 수 있습니다.",ru:"Этот сайт не устанавливает cookie и не использует аналитику. Ваш выбор языка и подтверждение уведомления о проекте сохраняются только в вашем браузере. Шрифты и значки загружаются с Google Fonts, который видит ваш IP-адрес.",tr:"Bu site çerez kullanmaz ve analiz aracı çalıştırmaz. Dil tercihiniz ve proje bildirimi yalnızca kendi tarayıcınızda saklanır. Yazı tipleri ve simgeler Google Fonts'tan yüklenir; Google Fonts IP adresinizi görür.",id:"Situs ini tidak memasang cookie dan tidak menjalankan analitik. Pilihan bahasa dan konfirmasi pemberitahuan proyek Anda hanya disimpan di browser Anda sendiri. Font dan ikon dimuat dari Google Fonts, yang melihat alamat IP Anda.",vi:"Trang này không đặt cookie và không chạy công cụ phân tích nào. Lựa chọn ngôn ngữ và xác nhận thông báo dự án của bạn chỉ được lưu trong trình duyệt của riêng bạn. Phông chữ và biểu tượng được tải từ Google Fonts, nên dịch vụ này thấy địa chỉ IP của bạn."})}</p>
        <div class="cb-act"><a href="terms.html#t11">${window.bcT('Privacy details','隱私說明',{hans:"隐私详情",es:"Detalles de privacidad",pt:"Detalhes de privacidade",fr:"Détails sur la confidentialité",de:"Datenschutzdetails",it:"Dettagli sulla privacy",ja:"プライバシーの詳細",ko:"개인정보 상세",ru:"Подробнее о конфиденциальности",tr:"Gizlilik ayrıntıları",id:"Rincian privasi",vi:"Chi tiết quyền riêng tư"})}<span class="icon">arrow_forward</span></a><button type="button" class="cb-ok">${window.bcT('Got it','知道了',{hans:"知道了",es:"Entendido",pt:"Entendi",fr:"Compris",de:"Verstanden",it:"Ho capito",ja:"わかりました",ko:"확인",ru:"Понятно",tr:"Anladım",id:"Mengerti",vi:"Đã hiểu"})}</button></div>`;
      b.querySelector('.cb-ok').onclick=()=>{try{localStorage.setItem('bitcheque-cookies','v1')}catch(e){}b.remove();document.documentElement.style.removeProperty('--cbh')}};
    fill();new MutationObserver(fill).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    document.body.appendChild(b);const h=()=>document.documentElement.style.setProperty('--cbh',matchMedia('(max-width:600px)').matches?b.offsetHeight+16+'px':'0px');h();if(window.ResizeObserver)new ResizeObserver(h).observe(b)}
  document.addEventListener('DOMContentLoaded',cookieBar);
})();
