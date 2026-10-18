#!/bin/sh
# Build the site and upload the public files (pages + assets only) to Cloudflare.
# Branch main -> https://bitcheque.org, branch dev -> https://dev.bitcheque.org.
set -e; cd "$(dirname "$0")"
B=$(git branch --show-current)
case "$B" in main) ENV="";; dev) ENV="--env dev";; *) echo "deploy from main or dev (on '$B')"; exit 1;; esac
python3 build.py >/dev/null
rm -rf dist; mkdir dist
cp index.html explorer.html onboard.html learn.html paper.html terms.html status.html top.html sample-cheque-book.html dist/
cp -r assets dist/
npx -y wrangler@4 deploy $ENV
