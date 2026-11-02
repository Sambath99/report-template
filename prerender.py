#!/usr/bin/env python3
"""Pre-render report.html so it shows all numbers, tables and charts even when
JavaScript is blocked (iPhone Telegram / Files preview).
Usage: python prerender.py report.html report_static.html
Needs: pip install playwright && python -m playwright install chromium
In a normal browser the file works exactly like before (tabs, sorting, filters)."""
import sys, os
from playwright.sync_api import sync_playwright

src, dst = os.path.abspath(sys.argv[1]), sys.argv[2]
TABS = ["overview", "content", "time", "likes", "posts", "todo"]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 430, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + src)
    pg.wait_for_timeout(400)
    cap = {}
    for t in TABS:
        pg.click(".tabs button[data-tab=%s]" % t)
        pg.wait_for_timeout(350)
        cap[t] = pg.evaluate("t => document.querySelector('.panel[data-tab=' + t + ']').innerHTML", t)
    pg.evaluate("""cap => {
      document.querySelectorAll('.panel').forEach(p => { p.innerHTML = cap[p.dataset.tab]; p.hidden = false; });
      document.querySelectorAll('.filters button[data-fmt]').forEach(b => { if (b.dataset.fmt) b.remove(); });
      const ns = document.createElement('noscript');
      ns.innerHTML = '<style>.cr .tabs{display:none}</style>';
      document.head.appendChild(ns);
    }""", cap)
    html = "<!doctype html>\n" + pg.evaluate("document.documentElement.outerHTML")
    b.close()
if errs:
    print("page errors:", errs[:3])
open(dst, "w", encoding="utf-8").write(html)
print("Wrote", dst, len(html), "bytes")
