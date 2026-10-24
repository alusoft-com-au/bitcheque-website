# Bitcheque website

Static site: `index.html` (home), `onboard.html` (guided cheque-book creation), `explorer.html` (block explorer),
`learn.html`, `status.html`, `top.html`, `paper.html`, `terms.html`. Sources live in `src/`; shared head, nav and footer
are filled in by `python3 build.py`. Styles are in `assets/`; the language menu (14 languages) is `src/site.js` with
`i18n/`.
`build.py` also writes `_headers` (security headers for Cloudflare, with a content security policy that allows the
pages' own inline scripts by hash), checks `bitcheque-print.html` against `../bitcheque-print/SHA256SUMS`, refreshes
`i18n/source.json` and fails when `i18n_check.py` finds a missing or broken translation.

Run locally:

    python3 -m http.server 8090              # then open http://127.0.0.1:8090/

The node, the design specification and the browser wallet's Rust source are in
[bitcheque-node](https://github.com/alusoft-com-au/bitcheque-node). `assets/bitcheque.wasm` is built from its
`wallet-wasm/` crate, reproducibly (see bitcheque-print's README), and must be byte for byte the wasm inside
`bitcheque-print.html`, whose checksum bitcheque-print publishes: `build.py` stops if they differ. After a new
bitcheque-print release, `python3 build.py --take-wasm` copies the print page from `../bitcheque-print`, then the wasm
and `assets/book.js` out of it; `build.py` also stops if `assets/book.js` is not the print code inside the page.

The pages read from the research network's nodes (the `NODES` list in `build.py`), or a local node's RPC; the explorer
falls back to labelled example data when none answers. Onboarding steps can be linked directly, e.g.
`onboard.html#seedA` or `onboard.html#more`.

Images: every illustration is drawn by code in banknote "dot-and-lash" engraving (parallel lines that
follow each surface, swell in shadow and break into dashes and dots in the light). `engrave_lib.py` is the
engine (numpy only); `scenes.py` holds one scene per illustration (`python3 scenes.py [name]`), and
`draw_wallets.py` draws the cold wallets for the first homepage section. Output: black ink on transparency
in `assets/engr/`, rendered at display size so the lines stay crisp. Brand files and the emblem generator
are in `assets/brand/`. Type: Plus Jakarta Sans + Chiron Hei HK, Geist Mono for numbers, all
self-hosted in `assets/fonts/` (Chiron Hei HK and Noto Sans JP only as the slices that hold the site's own text).

Deploy (Cloudflare, static assets only): `./deploy.sh` builds `dist/` (the pages and the assets they use, nothing else) and
uploads it (`./deploy.sh --dist` builds `dist/` only). Branch `main` goes to https://bitcheque.org, branch `dev` to https://dev.bitcheque.org.
