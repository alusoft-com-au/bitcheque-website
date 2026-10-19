#!/usr/bin/env python3
"""Assemble web/*.html from src/*.html, filling <!--HEAD-->, <!--NAV:page--> and <!--FOOT-->."""
import os, re
D = os.path.dirname(os.path.abspath(__file__))
head = open(os.path.join(D, "assets/head.txt")).read()
import hashlib, json
import i18n
TR = i18n.load(); MISSING = set()
# the browser wallet (bitcheque-node/wallet-wasm, the node's own Rust compiled to WebAssembly) is copied in
# when a node checkout beside this repo (../block or ../bitcheque-node) has a newer build
_w = next((p for p in (os.path.join(D, "..", r, "wallet-wasm/target/wasm32-unknown-unknown/release/bitcheque_web.wasm") for r in ("block", "bitcheque-node")) if os.path.exists(p)), "")
if os.path.exists(_w) and (not os.path.exists(os.path.join(D, "assets/bitcheque.wasm")) or os.path.getmtime(_w) > os.path.getmtime(os.path.join(D, "assets/bitcheque.wasm"))):
    open(os.path.join(D, "assets/bitcheque.wasm"), "wb").write(open(_w, "rb").read())
# the print code (assets/book.js) and the offline print page (bitcheque-print.html, offered for download) come from a
# bitcheque-print checkout beside this repo when it has newer copies; both are committed here so the site builds alone
for _src, _dst in (("src/book.js", "assets/book.js"), ("bitcheque-print.html", "bitcheque-print.html")):
    _p = os.path.join(D, "..", "bitcheque-print", _src)
    if os.path.exists(_p) and (not os.path.exists(os.path.join(D, _dst)) or os.path.getmtime(_p) > os.path.getmtime(os.path.join(D, _dst))):
        open(os.path.join(D, _dst), "wb").write(open(_p, "rb").read())
# site.js is generated from src/site.js so its T(...) calls get their translations too
open(os.path.join(D, "assets/site.js"), "w").write(i18n.inject_js(open(os.path.join(D, "src/site.js")).read(), TR, MISSING))
def _v(f): return hashlib.sha256(open(os.path.join(D, f), "rb").read()).hexdigest()[:8]
for f in ("assets/site.css", "assets/site.js"):
    head = head.replace(f'"{f}"', f'"{f}?v={_v(f)}"')
LOGO = '<svg viewBox="0 0 64 64" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M33.750 60.750 L60.237 34.263 Q62.500 32.000 60.237 29.737 L34.263 3.763 Q32.000 1.500 29.737 3.763 L3.763 29.737 Q1.500 32.000 3.763 34.263 L30.250 60.750 L30.250 33.864 A6.6 6.6 0 1 1 33.750 33.864 Z"/></svg>'
# The public nodes the site talks to (bitcheque-node/edge, on Cloudflare); pages use whichever answers first
NODES = [("Asia-Pacific node", "亞太節點", "https://node-ap.bitcheque.org"), ("North America node", "北美節點", "https://node-us.bitcheque.org"), ("Europe node", "歐洲節點", "https://node-eu.bitcheque.org")]
NODES_JS = '<script>window.BC_NODES=' + json.dumps([{"name": n, "zh": z, "l": {l: TR[l][n] for l in i18n.LANGS if n in TR[l]}, "url": u} for n, z, u in NODES], ensure_ascii=False) + '</script>'
MENU = [  # (label, zh, [(title, zh, description, zh, href, icon)])
 ("Academy", "學院", [
   ("What is Bitcheque", "什麼是 Bitcheque", "A research project on hash-based signatures", "雜湊簽名的研究專案", "index.html#what", "help"),
   ("How it works", "運作方式", "The cheque, the book and transfers, in one page", "支票、簿子與轉帳，一頁看懂", "learn.html", "menu_book"),
   ("Research paper", "研究論文", "Working paper: design, analysis, references", "工作論文：設計、分析與參考文獻", "paper.html", "article"),
   ("Design specification", "設計規格", "Every rule and parameter, and why", "每條規則與參數，以及原因", "https://github.com/alusoft-com-au/bitcheque-node/blob/main/DESIGN.md", "description"),
   ("FAQ", "常見問題", "Quantum safety, lost books, printers", "抗量子、遺失簿子、印表機", "index.html#faq", "quiz")]),
 ("Use", "使用", [
   ("Create a cheque book", "建立支票簿", "A guided walk-through, from seed to account number", "從種子到帳號的逐步導覽", "onboard.html", "add_circle"),
   ("Print more cheques", "印更多支票", "More cheques for your book, or a reprint, from your seed", "用種子為簿子印更多支票或重印", "onboard.html#more", "library_add"),
   ("Try a cheque", "試開一張支票", "See which cells become your signature", "看看哪些格子成為你的簽名", "index.html#demo", "edit"),
   ("Cheque helper", "支票小工具", "Write, verify and send a cheque", "填寫、驗證並送出支票", "index.html#demo", "calculate")]),
 ("Build", "開發", [
   ("Run a node", "執行節點", "One command, no dependencies", "一行指令，零依賴", "index.html#build", "terminal"),
   ("RPC reference", "RPC 參考", "Plain-text HTTP for wallets", "給錢包用的純文字 HTTP", "index.html#build", "api"),
   ("Source and tests", "原始碼與測試", "About 2,500 lines of Rust", "約 2,500 行 Rust", "https://github.com/alusoft-com-au/bitcheque-node", "code")]),
 ("Network", "網路", [
   ("Explorer", "區塊瀏覽器", "Blocks, accounts and broadcasts", "區塊、帳戶與廣播", "explorer.html", "deployed_code"),
   ("Node status", "節點狀態", "Height, peers and sync of every node", "每個節點的高度、對等節點與同步", "status.html", "monitor_heart"),
   ("Top accounts", "資產排行", "The largest balances on the chain", "鏈上餘額最多的帳戶", "top.html", "leaderboard"),
   ("The network", "網路", "May change or be reset until widely adopted; no promise of value", "被廣泛採用前可能變更或重置；不保證價值", "index.html#build", "lan"),
   ("Genesis", "創世區塊", "Block 0 rewards nobody", "第 0 區塊不獎勵任何人", "https://github.com/alusoft-com-au/bitcheque-node/blob/main/DESIGN.md", "flag")]),
]
def nav(cur):
    items, panels = "", ""
    for i, (lab, zh, links) in enumerate(MENU):
        items += f'<button class="mi" type="button" aria-expanded="false" aria-controls="mp{i}" data-zh="{zh}">{lab}</button>'
        cards = "".join(f'<a class="ml" href="{h}"><span class="icon">{ic}</span><span><b data-zh="{tz}">{t}</b><small data-zh="{dz}">{d}</small></span></a>'
                        for t, tz, d, dz, h, ic in links)
        panels += f'<div class="mp" id="mp{i}" hidden><div class="wrap mpi"><div class="mph"><span class="eyebrow" data-zh="{zh}">{lab}</span></div><div class="mpl">{cards}</div></div></div>'
    return (f'<div class="tnbar" role="note"><div class="tn-in"><b class="tn-tag"><span class="tn-dot"></span><span data-zh="實驗性">Experimental</span></b><span class="tn-msg" data-zh="實驗性研究專案。在被廣泛採用之前，網路可能變更或重置。不保證任何價值。">Experimental research project. Until it is widely adopted, the network may change or be reset. No promise of value.</span><span class="tn-short" data-zh="實驗性 · 不提供保證">Experimental · no guarantees</span><a class="tn-link" href="terms.html"><span data-zh="使用條款">Terms of use</span><span class="icon">arrow_forward</span></a></div></div><header class="nav"><div class="wrap navi"><a class="logo" href="index.html" aria-label="Bitcheque home">{LOGO}<span>Bitcheque</span></a>'
            f'<nav class="menu" aria-label="Main">{items}<a class="mi mlink" href="explorer.html"{" aria-current=page" if cur == "explorer" else ""}><span class="icon">deployed_code</span><span data-zh="區塊瀏覽器">Explorer</span></a></nav>'
            f'<div class="end"><button class="srch" type="button" aria-label="Search"><span class="icon">search</span><span data-zh="搜尋">Search</span><kbd>Ctrl K</kbd></button>'
            f'<button class="langb lang-btn-x" type="button"><span class="icon">translate</span><span class="lang-cur">English</span></button>'
            f'<button class="chip-btn menu-btn" type="button" aria-label="Menu"><span class="icon">menu</span></button></div></div>{panels}'
            f'<div class="sbox" hidden><div class="wrap"><div class="sin"><span class="icon">search</span><input id="site-q" placeholder="Search pages and sections" data-zh-ph="搜尋頁面與段落" autocomplete="off"><kbd>Esc</kbd></div><div class="sres" id="site-res"></div></div></div></header>')
FOOT = f'''<footer class="fstub"><div class="perf" aria-hidden="true"><span class="icon">content_cut</span></div>
<div class="wrap fs-in">
  <div class="fs-top">
    <div class="fs-say"><p class="fs-k" data-zh="存根 · 保留此聯">Counterfoil · keep this part</p><h2 data-zh="雜湊簽名，<br>親手簽署。">Hash-based signatures,<br>hand-signed.</h2>
      <div class="fs-act"><a class="btn fs-cta" href="onboard.html"><span data-zh="建立你的支票簿">Make your cheque book</span><span class="icon">arrow_forward</span></a><div class="fs-soc"><a href="#" aria-label="Bitcheque on X" title="X"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231Zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77Z"/></svg></a><a href="#" aria-label="Bitcheque on Telegram" title="Telegram"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M22.26 3.06c.4-.17.84.17.76.6l-3.1 16.3c-.1.55-.73.8-1.18.47l-4.98-3.68-2.6 2.5a.6.6 0 0 1-1.01-.38l-.22-3.86 8.57-7.8c.22-.2-.04-.54-.29-.38L7.6 13.4l-4.57-1.5c-.6-.2-.63-1.03-.05-1.27L22.26 3.06Z"/></svg></a><a href="#" aria-label="Bitcheque on Reddit" title="Reddit"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M15.6 2.6a1.6 1.6 0 1 1-1.5 2.1l-2.6-.55-.8 3.86c2 .1 3.8.7 5.1 1.64a2 2 0 1 1 2.6 2.97c.03.2.05.4.05.6 0 3.2-3.6 5.8-8.1 5.8s-8.1-2.6-8.1-5.8c0-.2.02-.4.05-.6A2 2 0 1 1 4.9 9.65c1.3-.93 3-1.52 4.95-1.63l.95-4.5a.45.45 0 0 1 .53-.35l3.05.64a1.6 1.6 0 0 1 1.22-1.2ZM8.8 11.2a1.4 1.4 0 1 0 0 2.8 1.4 1.4 0 0 0 0-2.8Zm6.4 0a1.4 1.4 0 1 0 0 2.8 1.4 1.4 0 0 0 0-2.8Zm-6.33 4.3a.45.45 0 0 0-.32.77c.85.85 2.2 1.18 3.45 1.18s2.6-.33 3.45-1.18a.45.45 0 1 0-.64-.64c-.6.6-1.67.92-2.81.92s-2.2-.32-2.81-.92a.45.45 0 0 0-.32-.13Z"/></svg></a><a href="#" aria-label="Bitcheque on GitHub" title="GitHub"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.26 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z"/></svg></a></div></div></div>
    <nav class="fs-cols" aria-label="Footer">
      <div><h4 data-zh="使用">Use</h4><a href="onboard.html" data-zh="建立支票簿">Create a cheque book</a><a href="onboard.html#more" data-zh="印更多支票">Print more cheques</a><a href="index.html#demo" data-zh="開一張支票">Write a cheque</a></div>
      <div><h4 data-zh="學院">Academy</h4><a href="learn.html" data-zh="運作方式">How it works</a><a href="https://github.com/alusoft-com-au/bitcheque-node/blob/main/DESIGN.md" data-zh="設計規格">Design specification</a><a href="index.html#faq" data-zh="常見問題">FAQ</a></div>
      <div><h4 data-zh="網路">Network</h4><a href="explorer.html" data-zh="區塊瀏覽器">Explorer</a><a href="index.html#build" data-zh="執行節點">Run a node</a><a href="sample-cheque-book.html" data-zh="範例支票簿">Sample cheque book</a><a href="terms.html" data-zh="使用條款">Terms of use</a></div>
    </nav>
  </div>
  <div class="fs-chq" aria-label="Bitcheque">
    <img class="fs-ros" src="assets/engr/rosette.webp" alt="" loading="lazy">
    <div class="fs-face"><div class="fs-meta mono"><span><i data-zh="編號">No.</i> 000001</span><span><i data-zh="欄">Columns</i> 18</span><span><i data-zh="年份">Series</i> 2026</span></div>
      <div class="fs-name">{LOGO}<span>Bitcheque</span></div>
      <p class="fs-tag" data-zh="以雜湊簽名的紙本支票簿，由你親手抄寫。">A paper cheque book signed with hashes, copied out by hand.</p></div>
    <div class="fs-sign"><svg viewBox="0 0 340 112" aria-hidden="true"><path class="fs-ink" pathLength="1" d="M30 88 C38 62 46 34 56 18 C60 12 62 20 58 34 C53 54 46 74 42 90 C52 58 86 34 96 44 C104 52 86 62 66 62 C92 60 108 70 98 84 C88 96 60 94 54 84 M104 78 C110 66 116 58 118 60 C120 64 114 78 118 80 C124 82 130 60 138 40 C134 58 130 76 136 80 C142 82 150 68 158 66 C150 62 146 80 154 82 C162 84 170 68 176 50 C178 44 180 40 182 38 C178 56 172 76 172 82 C176 70 184 62 190 64 C196 66 190 80 196 82 C202 82 206 70 212 68 C206 66 202 80 210 82 C220 84 226 66 238 66 C230 66 226 82 236 82 C242 82 246 72 246 66 C246 78 244 96 240 106 C238 96 248 82 256 80 C262 78 260 82 262 84 C266 78 268 70 272 68 C270 78 274 84 282 80 C288 76 290 70 292 66 C288 74 290 84 300 80 C306 78 310 70 312 66 C306 70 304 82 314 82"/></svg><span class="fs-line"></span><span class="fs-sl" data-zh="簽名 · 手寫">Signature · by hand</span></div>
  </div>
  <div class="fs-gui" aria-hidden="true"></div>
  <div class="fs-micr mono"><span data-zh="⑆ 實驗性研究專案">⑆ EXPERIMENTAL RESEARCH PROJECT</span><span data-zh="⑆ 不保證價值 ⑆ 無代幣發售">⑆ NO PROMISE OF VALUE ⑆ NO TOKEN SALE</span><span data-zh="⑆ MIT 授權 ⑆ 2026 ⑆">⑆ MIT LICENCE ⑆ 2026 ⑆</span></div>
  <div class="fs-co"><span data-zh="ALUSOFT PTY LTD 的實驗性專案">An experimental project by</span> <a href="https://alusoft.com.au" rel="noopener">ALUSOFT PTY LTD</a> · <a href="https://alusoft.com.au" rel="noopener">alusoft.com.au</a> · ABN 21 654 141 296 · <a href="terms.html" data-zh="使用條款">Terms of use</a><br><span class="fs-note" data-zh="ALUSOFT PTY LTD 維護本網站、軟體與 Bitcheque 名稱。網路本身是公開的：由自行選擇運行節點的獨立參與者維持，沒有任何人（包括我們）控制或保證它。">ALUSOFT PTY LTD maintains this website, the software and the Bitcheque name. The network itself is open: it is run by independent participants who choose to operate nodes, and no one, including us, controls or guarantees it.</span></div>
</div></footer>'''
for f in os.listdir(os.path.join(D, "src")):
    if not f.endswith(".html"): continue
    t = open(os.path.join(D, "src", f)).read()
    t = t.replace("<!--HEAD-->", head + NODES_JS).replace("<!--FOOT-->", FOOT).replace("<!--LOGO-->", LOGO)
    t = re.sub(r"<!--NAV:(\w+)-->", lambda m: nav(m.group(1)), t)
    t = i18n.inject(t, TR, MISSING)
    open(os.path.join(D, f), "w").write(t)
    print("built", f, len(t))
if MISSING:
    print(f"untranslated: {len(MISSING)} (language, string) pairs; run python3 i18n.py to refresh i18n/source.json")
