"""Site translations beyond English and Traditional Chinese.

English stays in the markup and Traditional Chinese in data-zh / T(en, zh) as before. At build time every
translated string is looked up by its English source in i18n/<lang>.json and injected:
  HTML  <x data-zh="..">English</x>      ->  <x data-zh=".." data-l-es="..">English</x>
  JS    T('English', '中文')              ->  T('English', '中文', {es: "..", ...})
Template-literal strings keep their ${...} placeholders, which every translation must carry over verbatim."""
import html, json, os, re
from html.parser import HTMLParser

D = os.path.dirname(os.path.abspath(__file__))
LANGS = ["hans", "es", "pt", "fr", "de", "it", "ja", "ko", "ru", "tr", "id", "vi"]

# ---------- JS string literals ----------
def js_literal_end(s, i):
    """s[i] is a quote; return the index just past the closing quote (handles escapes and ${...} nesting)."""
    q = s[i]; j = i + 1
    while j < len(s):
        c = s[j]
        if c == "\\": j += 2; continue
        if c == q: return j + 1
        if q == "`" and s.startswith("${", j):
            j = js_expr_end(s, j + 2); continue
        if q != "`" and c == "\n": raise ValueError("newline in string at %d" % i)
        j += 1
    raise ValueError("unterminated string at %d" % i)

def js_expr_end(s, j):
    """Inside ${ ... }: return index just past the matching }."""
    depth = 1
    while j < len(s):
        c = s[j]
        if c in "'\"`": j = js_literal_end(s, j); continue
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: return j + 1
        j += 1
    raise ValueError("unterminated ${")

CALL = re.compile(r"(?<![\w$.])(?:window\.)?(?:bc)?T\(")

def js_calls(s):
    """Yield (call_start, en_span, zh_span, close_index) for T('en','zh') / bcT(...) with literal arguments."""
    for m in CALL.finditer(s):
        i = m.end()
        while i < len(s) and s[i] in " \n": i += 1
        if i >= len(s) or s[i] not in "'\"`": continue
        try:
            a = js_literal_end(s, i); j = a
            while s[j] in " \n": j += 1
            if s[j] != ",": continue
            j += 1
            while s[j] in " \n": j += 1
            if s[j] not in "'\"`": continue
            b = js_literal_end(s, j); k = b
            while s[k] in " \n": k += 1
            if s[k] not in "),": continue                 # "," only when the build already added translations
        except (ValueError, IndexError):
            continue
        yield m.start(), (i, a), (j, b), k

def js_value(lit):
    """The text a translator sees: the literal's body with JS escapes for quotes undone (placeholders kept)."""
    body = lit[1:-1]
    return re.sub(r"\\([\\'\"`])", r"\1", body)

def js_quote(text, kind):
    if kind == "`":
        out = []; i = 0
        while i < len(text):                               # escape backticks and backslashes outside ${...}
            if text.startswith("${", i):
                e = js_expr_end(text, i + 2); out.append(text[i:e]); i = e; continue
            c = text[i]; out.append("\\" + c if c in "`\\" else c); i += 1
        return "`" + "".join(out) + "`"
    return json.dumps(text, ensure_ascii=False)

# ---------- HTML data-zh elements ----------
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

class Finder(HTMLParser):
    def __init__(s, text):
        super().__init__(convert_charrefs=False)
        s.text = text; s.stack = []; s.found = []
        s.lines = [0]
        for m in re.finditer("\n", text): s.lines.append(m.end())
    def off(s):
        l, c = s.getpos(); return s.lines[l - 1] + c
    def handle_starttag(s, tag, attrs):
        a = s.off(); e = a + len(s.get_starttag_text())
        if tag in VOID:
            if any(k == "data-zh-ph" for k, _ in attrs): s.found.append(("ph", a, e, None, None))
            return
        s.stack.append((tag, a, e, dict(attrs)))
    def handle_startendtag(s, tag, attrs):
        a = s.off(); e = a + len(s.get_starttag_text())
        if any(k == "data-zh-ph" for k, _ in attrs): s.found.append(("ph", a, e, None, None))
    def handle_endtag(s, tag):
        if tag in VOID: return
        for k in range(len(s.stack) - 1, -1, -1):
            if s.stack[k][0] == tag:
                t, a, e, attrs = s.stack[k]; del s.stack[k:]
                if "data-zh" in attrs: s.found.append(("el", a, e, s.off(), attrs))
                if "data-zh-ph" in attrs: s.found.append(("ph", a, e, None, None))
                return

def html_items(text):
    f = Finder(text); f.feed(text); f.close()
    out = []
    for kind, a, e, close, attrs in f.found:
        tag = text[a:e]
        if kind == "el":
            zh = html.unescape(re.search(r'\sdata-zh="([^"]*)"', tag).group(1))
            out.append(("el", e, text[e:close], zh))
        else:
            en = re.search(r'\splaceholder="([^"]*)"', tag); zh = re.search(r'\sdata-zh-ph="([^"]*)"', tag)
            if en and zh: out.append(("ph", e, html.unescape(en.group(1)), html.unescape(zh.group(1))))
    return out

def script_spans(text):
    return [(m.start(1), m.end(1)) for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", text, re.S)]

# ---------- extract / inject ----------
def extract(text):
    """All (kind, en, zh) items in a rendered page: kind is 'html', 'ph', or the JS quote char."""
    items = [("html" if k == "el" else "ph", en, zh) for k, _, en, zh in html_items(text)]
    for a, b in script_spans(text):
        for _, (ea, eb), (za, zb), _ in js_calls(text[a:b]):
            lit = text[a + ea:a + eb]
            items.append((lit[0], js_value(lit), js_value(text[a + za:a + zb])))
    return items

def load():
    T = {}
    for l in LANGS:
        p = os.path.join(D, "i18n", l + ".json")
        T[l] = json.load(open(p)) if os.path.exists(p) else {}
    return T

def inject(text, T, missing):
    edits = []                                             # (start, end, replacement), applied back to front
    for kind, e, en, zh in html_items(text):
        attr = "data-l-" if kind == "el" else "data-ph-"
        extra = ""
        for l in LANGS:
            v = T[l].get(en)
            if v is None: missing.add((l, en)); continue
            extra += f' {attr}{l}="{html.escape(v, quote=True)}"'
        if extra:
            tag_end = e - 1 if text[e - 2] != "/" else e - 2
            edits.append((tag_end, tag_end, extra))
    for a, b in script_spans(text):
        edits += js_edits(text[a:b], T, missing, a)
    for st, en_, rep in sorted(edits, reverse=True):
        text = text[:st] + rep + text[en_:]
    return text

def inject_js(src, T, missing):
    for st, en_, rep in sorted(js_edits(src, T, missing, 0), reverse=True):
        src = src[:st] + rep + src[en_:]
    return src

def js_edits(s, T, missing, a):
    edits = []
    if True:
        for _, (ea, eb), _, k in js_calls(s):
            if s[k] != ")": continue
            lit = s[ea:eb]; en = js_value(lit)
            parts = []
            for l in LANGS:
                v = T[l].get(en)
                if v is None: missing.add((l, en)); continue
                parts.append(f"{l}:{js_quote(v, lit[0] if lit[0] == '`' else '')}")
            if parts: edits.append((a + k, a + k, ",{" + ",".join(parts) + "}"))
    return edits

if __name__ == "__main__":                                 # dump the source strings for translators
    seen = {}
    for f in sorted(os.listdir(D)):
        if not f.endswith(".html") or f in ("brand-options.html",): continue
        for kind, en, zh in extract(open(os.path.join(D, f)).read()):
            if en.strip() and en not in seen: seen[en] = {"en": en, "zh": zh, "kind": kind, "page": f}
    for kind, en, zh in [(q, js_value(s_[ea:eb]), js_value(s_[za:zb])) for s_ in [open(os.path.join(D, "src", "site.js")).read()]
                         for _, (ea, eb), (za, zb), _ in js_calls(s_) for q in [s_[ea]]]:
        if en.strip() and en not in seen: seen[en] = {"en": en, "zh": zh, "kind": kind, "page": "site.js"}
    import ast
    nodes = ast.literal_eval(re.search(r"^NODES = (\[.*\])$", open(os.path.join(D, "build.py")).read(), re.M).group(1))
    for n, z, _ in nodes:
        if n not in seen: seen[n] = {"en": n, "zh": z, "kind": "data", "page": "nodes"}
    json.dump(list(seen.values()), open(os.path.join(D, "i18n", "source.json"), "w"), ensure_ascii=False, indent=1)
    print(len(seen), "strings")
