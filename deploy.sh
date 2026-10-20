#!/bin/sh
# Build the site and upload the public files (pages + the assets they use) to Cloudflare.
# Branch main -> https://bitcheque.org, branch dev -> https://dev.bitcheque.org.
set -e; cd "$(dirname "$0")"
B=$(git branch --show-current)
case "$B" in main) ENV="";; dev) ENV="--env dev";; *) echo "deploy from main or dev (on '$B')"; exit 1;; esac
python3 build.py >/dev/null
rm -rf dist; mkdir dist
cp index.html explorer.html onboard.html learn.html paper.html terms.html status.html top.html bitcheque-print.html dist/
# only what the pages use: no scripts, notes, drafts or old samples from assets/
mkdir -p dist/assets/fonts dist/assets/engr dist/assets/brand
cp assets/site.css assets/site.js assets/bip39-en.js assets/book.js assets/bitcheque.wasm dist/assets/
cp assets/fonts/fonts.css assets/fonts/*.woff2 dist/assets/fonts/
cp assets/engr/*.webp dist/assets/engr/
cp assets/brand/app-icon.svg assets/brand/icon-32.png assets/brand/icon-180.png dist/assets/brand/
cp _headers dist/
[ "$1" = "--dist" ] && exit 0   # ./deploy.sh --dist: build dist/ only, to serve it locally
# the deploy tool is pinned: package.json names one exact wrangler and package-lock.json its checksum (npm ci refuses
# anything else), and --no-install never fetches a different one
npm ci --no-audit --no-fund >/dev/null
npx --no-install wrangler deploy $ENV
