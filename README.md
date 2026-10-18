# Bitcheque website

Static site: `index.html` (home), `onboard.html` (guided cheque-book creation, practice mode),
`explorer.html` (block explorer). Sources live in `src/`; shared head, nav and footer are filled in by
`python3 build.py`. Styles and the English/中文 toggle are in `assets/`.

Run locally:

    python3 -m http.server 8090              # then open http://127.0.0.1:8090/

The node, the design specification and the browser wallet's Rust source are in
[bitcheque-node](https://github.com/alusoft-com-au/bitcheque-node). `assets/bitcheque.wasm` is built from its
`wallet-wasm/` crate; with a node checkout beside this one, `build.py` copies in a newer build automatically:

    cd ../bitcheque-node/wallet-wasm && cargo build --release --target wasm32-unknown-unknown

The explorer and the home page's network panel read from a node's RPC at 127.0.0.1:8732 and fall back
to labelled example data when none is running. Onboarding steps can be linked directly, e.g.
`onboard.html#seedA` or `onboard.html#restore`.

Images: every illustration is drawn by code in banknote "dot-and-lash" engraving (parallel lines that
follow each surface, swell in shadow and break into dashes and dots in the light). `engrave_lib.py` is the
engine (numpy only); `scenes.py` holds one scene per illustration (`python3 scenes.py [name]`), and
`draw_wallets.py` draws the cold wallets for the first homepage section. Output: black ink on transparency
in `assets/engr/`, rendered at display size so the lines stay crisp. Brand files and the emblem generator
are in `assets/brand/`. Type: Plus Jakarta Sans + Chiron Hei HK, Geist Mono for numbers.
