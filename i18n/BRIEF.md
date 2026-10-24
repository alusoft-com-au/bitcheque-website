# Translating the Bitcheque site

Bitcheque is an experimental research blockchain: a paper "cheque book" of hash-based one-time signatures.
You sign a cheque by copying words off printed paper, and the chain checks SHA-256 preimages. The site
(src/*.html, src/site.js) is English in the markup with Traditional Chinese alongside. We are adding:

| code | language | register |
|---|---|---|
| hans | Simplified Chinese (mainland usage and vocabulary, not a character swap of the Traditional text) | 你 |
| es | Spanish (neutral international) | tú |
| pt | Brazilian Portuguese | você |
| fr | French | vous |
| de | German | du (as ethereum.org does) |
| it | Italian | tu |
| ja | Japanese | です／ます |
| ko | Korean | 합니다／세요 polite style, consistent |
| ru | Russian | вы (lowercase) |
| tr | Turkish | siz |
| id | Indonesian | Anda |
| vi | Vietnamese | bạn |

## Your files
- Input: `i18n/source.json`, a list of `{en, zh, kind, page}`. `en` is the source of truth; `zh` is a
  human-reviewed Traditional Chinese version, useful to confirm meaning. `page` says where the string is.
- Output: `i18n/<code>.json`, a single JSON object `{ "<en exactly as in source>": "<translation>", ... }`
  with every source string as a key (keys must match `en` byte for byte). Write it with a small Python
  script (json.dump(..., ensure_ascii=False, indent=1)) so escaping is right.
- Check: `python3 i18n_check.py <code>` must report 0 problems.

## Hard rules
1. Keep every HTML tag and attribute exactly (`<b>`, `<br>`, `<a href=...>`, `<span class="icon">arrow_forward</span>`,
   `<code>`, `<kbd>` …). Translate only human-readable text between tags. Text inside `<span class="icon">…</span>`
   is an icon name: never translate it. Content of `<code>`, `<kbd>`, commands, URLs, file names, hex, RPC
   paths (/height, /account/1) and CLI flags stay as they are. Keep entities (&amp; &nbsp; &lt; …).
2. `kind` "`" strings are JS template literals: every `${...}` must appear verbatim (you may reorder them for
   grammar). `kind` "'" strings must not contain a newline.
3. Keep all numbers, amounts, block counts, digits and units of numbers exactly (you may localise the
   decimal/thousands separators only if the English writes them as words, never inside code).
4. Never translate: Bitcheque, SHA-256, BIP-39, ALUSOFT PTY LTD, ABN, MIT, SeedSigner, Rust, HTTP, RPC, JSON.
5. No money language. Do not use words for pay/payment/payee/purchase/wallet-balance-as-money; the site
   deliberately says "send", "transfer", "coins". Never "test coins", never call the network "testnet".
   Coins are just "coins" (es monedas, pt moedas, fr pièces, de Coins, it monete, ja コイン, ko 코인, ru монеты,
   tr coin, id koin, vi coin, hans 币).
6. Do not add or remove meaning. Do not add disclaimers, emoji or exclamation marks. Keep the plain, calm,
   short tone of the English. Headlines stay punchy; keep a trailing full stop if the English has one.
7. Terms of use / legal-ish wording (gate dialog, banner, cookie note, "no promise of value", "experimental
   research project", "at your own risk") must be precise and complete.

## Glossary (use consistently)
- cheque book: the printed book of 11 cheques (0–10). es talonario de cheques; pt talão de cheques; fr carnet de chèques;
  de Scheckheft; it libretto degli assegni; ja 小切手帳; ko 수표책; ru чековая книжка; tr çek defteri; id buku cek; vi sổ séc; hans 支票簿.
- cheque: one cheque (es cheque, pt cheque, fr chèque, de Scheck, it assegno, ja 小切手, ko 수표, ru чек, tr çek, id cek, vi séc, hans 支票).
- cheque piece(s): one on-chain transaction per column; 18 per cheque (fr pièce de chèque → prefer "fragment de chèque";
  de Scheckstück; es fragmento de cheque; pt fragmento de cheque; it frammento di assegno; ja 小切手の断片; ko 수표 조각;
  ru фрагмент чека; tr çek parçası; id kepingan cek; vi mảnh séc; hans 支票碎片).
- column / row / box (cell): the printed grid; each box holds 12 words.
- Part A / Part B: keep the letters A and B. Part A = recipient columns, Part B = amount columns.
- seed: the 24 BIP-39 words (es semilla, pt semente, fr graine (phrase de récupération only if English says so), de Seed,
  it seed, ja シード, ko 시드, ru сид-фраза, tr tohum, id seed, vi hạt giống (cụm từ hạt giống), hans 种子).
- honesty check: cheque 0 sent for zero coins to prove the book prints correctly.
- check digit: 12th digit of an account number. account number: 12 digits, e.g. 00000000420-3.
- amount / exponent (Exp) / fee / fee tier: amount is 4 significant digits × 10^exponent.
- registration / register: putting a book's hashes on chain. renewal. batch.
- block, block height, mempool (keep "mempool" in Latin languages if natural, ja メモリプール, ko 멤풀, ru мемпул,
  hans 交易池), node, miner, mining, reward, halving, confirmations, explorer (block explorer), fork, tip (chain tip).
- reprint, sweep (send everything to a new book), preimage, hash.
- quantum-safe / hash-based signatures / elliptic curves.

## Fragments and plurals
Short strings are often pieces of a sentence built in code (e.g. `'in'` + N + `'blocks'`, or `'Word'` `#3` `''`
which in Chinese is 第 #3 個字). Before translating any short or odd string, grep the page source for it
(`grep -n "T('in'" src/explorer.html`) and translate so the assembled sentence reads naturally in your
language. The check rejects empty strings: if your grammar needs nothing there, use the shortest natural
wording that still reads well once assembled, or move the meaning into a neighbouring fragment.

These are used with a count through `bcP(n, one, many)`: confirmation/confirmations, block/blocks,
transaction/transactions, cheque piece/cheque pieces, registration/registrations, batch/batches,
renewal/renewals, box/boxes, ordinary cheque/ordinary cheques. They always follow a number ("3 blocks"). "ordinary cheque" means cheques 1–9 used for normal transfers, as opposed to the last cheque kept for the sweep.
- Russian: give the "many" string as `few|many` forms, e.g. "blocks" → "блока|блоков"; "one" is the singular
  (used for 1, 21, 31 …). The `|` is allowed only here.
- Turkish, Indonesian, Vietnamese, Japanese, Korean, Chinese: nouns after numbers are not pluralised, so
  "many" usually equals "one".
- Others: normal plural.

The string "51" is a placeholder example account number: keep it "51".
