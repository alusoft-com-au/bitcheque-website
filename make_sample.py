#!/usr/bin/env python3
"""Sample print-out of a cheque book, generated from the PUBLIC practice seed used on the site.
One seed, printed as two parts in separate print runs: part A = recipient columns P1-P12,
part B = amount D1-D4, exponent E, fee F.
Writes sample-cheque-book.html (A4 landscape, one cheque per page per part). Never use these words."""
import hashlib, os
D = os.path.dirname(os.path.abspath(__file__))
W = open(os.path.join(D, "assets", "bip39-english.txt")).read().split()
SEED_A = "orbit lantern velvet harbor ginger meadow cobalt falcon ribbon tunnel sketch delta walnut ember quartz motor saddle pepper glacier needle canvas spiral oyster lotus"
COLS = [f"P{i}" for i in range(1, 13)] + ["D1", "D2", "D3", "D4", "E", "F"]
seed = lambda words: hashlib.sha256(words.encode()).digest()        # sample only; the wallet uses BIP-39 PBKDF2
key = lambda s, n: hashlib.sha256(b"bitcheque/key" + s + n.to_bytes(2, "little")).digest()
cell = lambda s, n, c, r: hashlib.sha256(b"bitcheque/cell" + key(s, n) + bytes([c, r])).digest()[:16]
def bip39(b):
    h = hashlib.sha256(b).digest(); bits = bin(int.from_bytes(b, "big"))[2:].zfill(128) + bin(h[0] >> 4)[2:].zfill(4)
    return [W[int(bits[i * 11:i * 11 + 11], 2)] for i in range(12)]
LOGO = open(os.path.join(D, "assets", "brand", "emblem-black.svg")).read().replace('<svg ', '<svg class="lg" ')
def page(part, n):
    sd, cols = seed(SEED_A), (range(0, 12) if part == "A" else range(12, 18))
    title = "Part A · recipient" if part == "A" else "Part B · amount, exponent, fee"
    head = "".join(f'<th>{COLS[c]}{" ✓" if c == 11 else ""}</th>' for c in cols)
    rows = ""
    for r in range(10):
        rows += f"<tr><th class='rw'>{r}</th>"
        for c in cols:
            ws = bip39(cell(sd, n, c, r))
            lines = "".join(f"<span>{ws[i]} {ws[i+1]}</span>" for i in range(0, 12, 2))
            rows += f"<td><div class='pos'>{COLS[c]}·{r}</div><div class='ws'>{lines}</div></td>"
        rows += "</tr>"
    groups = ("<th></th><th colspan='12'>RECIPIENT ACCOUNT · 11 digits + check digit</th>" if part == "A"
              else "<th></th><th colspan='4'>AMOUNT · 4 digits</th><th>EXP</th><th>FEE</th>")
    return f"""<section class="pg p{part}">
  <header><div class="brand">{LOGO}<b>Bitcheque</b></div>
    <div class="ttl"><b>{title}</b><span>Cheque {n} of 0–10{' · honesty check' if n == 0 else ' · LAST CHEQUE: sweep to a new book only' if n == 10 else ''}</span></div>
    <div class="acct">Account <span class="blank"></span></div>
    <div class="stamp">{'LAST CHEQUE · SWEEP ONLY' if n == 10 else 'SAMPLE · PUBLIC PRACTICE SEED'}</div></header>
  <table><thead><tr>{groups}</tr><tr><th></th>{head}</tr></thead><tbody>{rows}</tbody></table>
  <footer>{'<span><b>This is the last cheque in the book.</b> Use it only to sweep the whole balance to a new book: amount 0000, exponent 9. Spent on anything else, whatever is left in this account can never move again.</span>' if n == 10 else ''}<span>Print part {part} as its own print run on a clean, offline computer with a USB printer{' · print part B separately' if part == 'A' else ' · printed separately from part A'}. Keep the two parts apart.</span>
    <span>To sign: find the row of each digit in its column and copy all 12 words of that box. Tear off or cross out used cheques.</span></footer>
</section>"""
CSS = """
@page{size:A4 landscape;margin:8mm}
*{box-sizing:border-box}body{margin:0;font-family:"Plus Jakarta Sans",system-ui,sans-serif;color:#02050A;background:#E9ECF1}
.pg{width:281mm;height:194mm;margin:8mm auto;background:#FFFDF7;padding:7mm 8mm;position:relative;break-after:page;box-shadow:0 2px 12px rgba(0,0,0,.12);display:flex;flex-direction:column}
.pg:before{content:"";position:absolute;inset:3mm;border:.4mm solid #02050A;border-radius:2mm;pointer-events:none}
@media print{body{background:none}.pg{margin:0;box-shadow:none}}
header{display:flex;align-items:center;gap:6mm;margin-bottom:3mm}
.brand{display:flex;align-items:center;gap:2mm;font-size:4.6mm}.lg{width:6mm;height:6mm}
.ttl{display:flex;flex-direction:column}.ttl b{font-size:4.4mm}.ttl span{font-size:2.8mm;color:#555}
.acct{font-size:2.8mm;color:#555;display:flex;align-items:center;gap:2mm}.blank{display:inline-block;width:38mm;border-bottom:.3mm solid #02050A;height:4mm}
.stamp{margin-left:auto;font:700 2.6mm "Geist Mono",monospace;letter-spacing:.3mm;color:#D9601F;border:.4mm solid #D9601F;border-radius:1mm;padding:1mm 2mm}
table{border-collapse:collapse;table-layout:fixed}
.pA table{width:100%}.pB table{width:50%}
thead th{font:700 2.4mm "Geist Mono",monospace;letter-spacing:.2mm;padding:.8mm 0;text-align:center}
thead tr:first-child th{border-bottom:.35mm solid #02050A;text-align:left}
th.rw{width:5mm;font:600 2.8mm "Geist Mono",monospace;color:#666}
td{border:.25mm dashed #9aa0a8;padding:.5mm .8mm;vertical-align:top;height:14.8mm;overflow:hidden}
.pos{font:700 1.85mm "Geist Mono",monospace;color:#D9601F;margin-bottom:.2mm}
.ws{display:flex;flex-direction:column;font:500 1.72mm/1.12 "Geist Mono",monospace}.ws span{white-space:nowrap;overflow:hidden;text-overflow:clip}
footer{display:flex;flex-direction:column;gap:.6mm;margin-top:2.5mm;font-size:2.5mm;color:#444}
.cover{width:281mm;margin:8mm auto;background:#fff;padding:10mm;font-size:3.6mm;break-after:page}
.cover h1{font-size:8mm;margin:0 0 3mm}.cover li{margin:1.5mm 0}
"""
def main():
    pages = [page("A", n) for n in range(11)] + [page("B", n) for n in range(11)]
    cover = """<section class="cover"><h1>Sample cheque book</h1>
<p>This is a <b>sample</b> made from the public practice seed shown on the Bitcheque site. Anyone can recreate it, so it is for practice only.</p>
<ol><li>One 24-word seed makes the whole book. It is printed as two parts in <b>separate print runs</b>.</li>
<li><b>Part A</b> (pages 1–11) holds the recipient columns P1–P12 of cheques 0–10.</li>
<li><b>Part B</b> (pages 12–22) holds the amount D1–D4, exponent E and fee F columns.</li>
<li>For a real book, print on a clean, offline computer with a USB-only printer, print part A and part B separately, keep the two parts apart, and switch everything off afterwards.</li>
<li>Each box is one cell: its position (for example P3·5) and its 12 words. To sign, copy the 12 words of the box that matches each digit.</li></ol></section>"""
    html = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sample cheque book</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&family=Geist+Mono:wght@500;700&display=swap">
<style>{CSS}</style><body>{cover}{''.join(pages)}</body></html>"""
    open(os.path.join(D, "sample-cheque-book.html"), "w").write(html)
    print("pages:", len(pages) + 1)
if __name__ == "__main__":
    main()
