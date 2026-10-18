#!/bin/sh
# Build the site and upload the public files (pages + assets only) to Cloudflare Pages.
set -e; cd "$(dirname "$0")"
python3 build.py >/dev/null
rm -rf dist; mkdir dist
cp index.html explorer.html onboard.html learn.html paper.html terms.html status.html top.html sample-cheque-book.html dist/
cp -r assets dist/
npx -y wrangler@4 pages deploy dist --project-name bitcheque --branch main --commit-dirty=true
