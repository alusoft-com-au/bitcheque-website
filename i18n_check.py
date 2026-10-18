#!/usr/bin/env python3
"""Mechanical checks on i18n/<lang>.json against i18n/source.json.  Usage: python3 i18n_check.py <lang> [...]
Every source string must be translated, and each translation must keep the same HTML tags, ${...}
placeholders, entities, numbers and protected words as the English."""
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(D, "i18n", "source.json")))
PROTECT = ["Bitcheque", "SHA-256", "BIP-39", "ALUSOFT PTY LTD", "MIT"]
CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")

def tags(s): return sorted(re.sub(r"\s+", " ", t) for t in re.findall(r"<[^>]+>", s))
def ph(s): return sorted(re.findall(r"\$\{(?:[^{}]|\{[^{}]*\})*\}", s))
def ents(s): return sorted(re.findall(r"&[a-z#0-9]+;", s))
def nums(s):
    s = re.sub(r"<[^>]+>|\$\{(?:[^{}]|\{[^{}]*\})*\}", " ", s)
    s = re.sub(r"(\d+)\s*(?:million|百万|millions|millones|milhões|milioni|Millionen|миллиона?|milyon|juta|triệu)", lambda m: str(int(m.group(1)) * 10**6), s)
    s = re.sub(r"(\d+)\s*万", lambda m: str(int(m.group(1)) * 10**4), s)
    s = re.sub(r"(\d{1,3}(?:,\d{3})+|\d{4,})\s*만", lambda m: str(int(m.group(1).replace(",", "")) * 10**4), s)   # 2,100만 (not 256만 = "only 256")
    s = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}\b)", "", s)     # 1 500 written with spaces
    return sorted(re.findall(r"\d+(?:[.,]\d+)*", s))
def normnum(n): return re.sub(r"[.,\s  ]", "", n)

def check(lang):
    p = os.path.join(D, "i18n", lang + ".json")
    tr = json.load(open(p))
    bad = []
    for item in SRC:
        en = item["en"]
        if en not in tr: bad.append(("missing", en, "")); continue
        v = tr[en]
        if not isinstance(v, str) or not v.strip(): bad.append(("empty", en, v)); continue
        if tags(v) != tags(en): bad.append(("html tags differ", en, v))
        parts = re.split(r"\|(?![^{]*\})", v) if lang == "ru" and "|" not in en else [v]   # Russian few|many forms
        if any(ph(x) != ph(en) for x in parts): bad.append(("${} placeholders differ", en, v))
        if ents(v) != ents(en) and not (lang in ("ja", "ko", "hans") and set(ents(v)) <= set(ents(en))): bad.append(("entities differ", en, v))
        if sorted(map(normnum, nums(v))) != sorted(map(normnum, nums(en))): bad.append(("numbers differ", en, v))
        for w in PROTECT:
            if w in en and w not in v: bad.append((f"lost '{w}'", en, v))
        if lang not in ("ja", "ko", "hans") and CJK.search(v) and not CJK.search(en): bad.append(("CJK in translation", en, v))
        if "|" in v and "|" not in en and lang != "ru": bad.append(("'|' only allowed in Russian plural forms", en, v))
        if item["kind"] == "'" and "\n" in v: bad.append(("newline in single-quoted JS string", en, v))
    extra = set(tr) - {i["en"] for i in SRC}
    for e in extra: bad.append(("extra key (not in source)", e, ""))
    return bad

if __name__ == "__main__":
    rc = 0
    for lang in sys.argv[1:]:
        b = check(lang)
        print(f"{lang}: {len(SRC) - sum(1 for x in b if x[0]=='missing')}/{len(SRC)} translated, {len(b)} problems")
        for kind, en, v in b[:400]: print(f"  [{kind}] {en[:110]!r} -> {str(v)[:110]!r}")
        rc |= bool(b)
    sys.exit(rc)
