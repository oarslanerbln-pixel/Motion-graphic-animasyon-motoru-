"""Design .dc.html artboard -> standalone HTML (local @fontsource fonts) for deterministic rendering."""
import sys, re, json, os
src, out = sys.argv[1], sys.argv[2]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts"))
h = open(src, encoding="utf-8").read()
body = h[h.index("<x-dc>")+6 : h.index("</x-dc>")]
body = body.replace("<helmet>", "").replace("</helmet>", "")
body = re.sub(r'<link[^>]+fonts\.googleapis[^>]+>', "", body)
m = re.search(r"data-props='([^']*)'", h)
props = json.loads(m.group(1)) if m else {}
for k, v in props.items():
    if isinstance(v, dict) and "default" in v:
        body = body.replace("{{%s}}" % k, str(v["default"]))
css = []
for fam, files in {"unbounded": ["400.css", "600.css", "800.css"], "manrope": ["500.css", "700.css"],
                   "instrument-serif": ["400.css", "400-italic.css"]}.items():
    d = os.path.join(ROOT, "fontsource-" + fam)
    for fn in files:
        p = os.path.join(d, fn)
        if os.path.exists(p):
            c = open(p, encoding="utf-8").read().replace("url(./files/", "url(file://" + d + "/files/")
            css.append(c)
html = ('<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>' + "\n".join(css) +
        "\nhtml,body{margin:0;background:#000}</style></head><body>" + body + "</body></html>")
open(out, "w", encoding="utf-8").write(html)
