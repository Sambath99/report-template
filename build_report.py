#!/usr/bin/env python3
"""Build report.html from template.html + data.csv + config.json.

Usage:
  python build_report.py                       # uses data.csv and config.json
  python build_report.py --data my.csv --config my.json --out my_report.html
  python build_report.py --inline-d3           # put the chart library inside the file (works offline)
"""
import argparse, csv, json, re, urllib.request

COLUMNS = ["dt", "hour", "day", "format", "category", "topic", "views", "reach", "reactions", "comments", "shares"]
D3_URL = "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"

ap = argparse.ArgumentParser()
ap.add_argument("--template", default="template.html")
ap.add_argument("--data", default="data.csv")
ap.add_argument("--config", default="config.json")
ap.add_argument("--out", default="report.html")
ap.add_argument("--inline-d3", action="store_true")
a = ap.parse_args()

rows = list(csv.DictReader(open(a.data, encoding="utf-8-sig")))
if not rows:
    raise SystemExit("data.csv has no rows. Fill it first (see README.md).")
missing = [c for c in COLUMNS if c not in rows[0]]
if missing:
    raise SystemExit("data.csv is missing columns: " + ", ".join(missing))
for r in rows:
    r["hour"] = int(r["hour"])
    for k in ("views", "reach", "reactions", "comments", "shares"):
        r[k] = int(float(r[k] or 0))
cfg = json.load(open(a.config, encoding="utf-8"))
payload = json.dumps({"config": cfg, "posts": [{c: r[c] for c in COLUMNS} for r in rows]}, ensure_ascii=False).replace("</", "<\\/")

html = open(a.template, encoding="utf-8").read()
html, n = re.subn(r"/\*DATA_START\*/.*?/\*DATA_END\*/", lambda m: "/*DATA_START*/" + payload + "/*DATA_END*/", html, flags=re.S)
if n != 1:
    raise SystemExit("template.html: data marker not found")
if cfg.get("title"):
    html = re.sub(r"<title>.*?</title>", "<title>" + cfg["title"].replace("<", "") + "</title>", html, count=1)
if a.inline_d3:
    js = urllib.request.urlopen(D3_URL, timeout=60).read().decode("utf-8")
    html = html.replace('<script src="%s"></script>' % D3_URL, "<script>" + js.replace("</script", "<\\/script") + "</script>")
open(a.out, "w", encoding="utf-8").write(html)
print("Wrote %s with %d rows" % (a.out, len(rows)))
