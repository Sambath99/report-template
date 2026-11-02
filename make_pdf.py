#!/usr/bin/env python3
"""Make a designed A4 PDF from report.html (all tabs stacked, charts included).
Usage: python make_pdf.py report.html report.pdf
Needs: pip install playwright && python -m playwright install chromium"""
import sys, os
from playwright.sync_api import sync_playwright

src, dst = os.path.abspath(sys.argv[1]), sys.argv[2]
TABS = [("overview", "Overview"), ("content", "Content"), ("time", "Time"),
        ("likes", "Likes and shares"), ("posts", "All posts"), ("todo", "What to do")]
PRINT_CSS = """
@page { size: A4; margin: 12mm 11mm; }
html, body { background: #fff !important; }
body { padding: 0 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.cr { max-width: none !important; display: block !important; }
.cr > * + * { margin-top: 14px; }
.cr .panel { display: block !important; }
.cr .panel > * + * { margin-top: 12px; }
.cr .tabs { display: none !important; }
.cr .ptitle { font-family: var(--font-anthropic-serif); font-weight: 400; font-size: 1.5rem; margin: 6px 0 0; padding-bottom: 6px; border-bottom: 2px solid var(--color-fg); break-after: avoid; }
.cr .panel + .panel .ptitle { margin-top: 18px; }
.cr .panel.pbreak .ptitle { margin-top: 0; }
.cr .pbreak { break-before: page; }
.cr .card, .cr .tile, .cr .chart, .cr tr, .cr .hb { break-inside: avoid; }
.cr h2, .cr h3 { break-after: avoid; }
.cr .tall { max-height: none !important; overflow: visible !important; }
.cr .scroll { overflow: visible !important; }
.cr table { font-size: 0.72rem; }
.cr th, .cr td { white-space: normal !important; padding: 0.3rem 0.4rem; }
.cr th { position: static !important; }
.cr td.topic { min-width: 0; }
.cr .filters, .cr .cr-q, .cr th button.s::after { display: none !important; }
.cr th button.s { font-weight: 500; }
.cr .card { padding: 0.9rem 1rem; }
.cr .grid2 { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
.cr .tiles { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; }
.cr .tile .v { font-size: 1.9rem !important; }
.cr .hb { grid-template-columns: minmax(5rem, 34%) 1fr auto; }
.cr footer.pf { color: var(--color-fg-muted); font-size: .75rem; border-top: 1px solid var(--color-border-line); padding-top: 6px; }
"""
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 760, "height": 1000}, color_scheme="light")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + src)
    pg.wait_for_timeout(400)
    cap = {}
    for t, _ in TABS:
        pg.click(".tabs button[data-tab=%s]" % t)
        pg.wait_for_timeout(350)
        cap[t] = pg.evaluate("t => document.querySelector('.panel[data-tab=' + t + ']').innerHTML", t)
    pg.add_style_tag(content=PRINT_CSS)
    pg.evaluate("""([cap, tabs]) => {
      tabs.forEach(([t, label], i) => {
        const p = document.querySelector('.panel[data-tab=' + t + ']');
        p.innerHTML = '<h2 class="ptitle">' + label + '</h2>' + cap[t];
        p.hidden = false;
        if (t === 'posts' || t === 'todo') p.classList.add('pbreak');
      });
      document.querySelectorAll('.filters button[data-fmt]').forEach(b => { if (b.dataset.fmt) b.remove(); });
      const f = document.createElement('footer'); f.className = 'pf';
      f.textContent = 'Typical post = median views, so one huge post does not hide the rest.';
      document.querySelector('.cr').appendChild(f);
    }""", [cap, TABS])
    pg.emulate_media(media="print", color_scheme="light")
    pg.wait_for_timeout(300)
    pg.pdf(path=dst, format="A4", print_background=True, margin={"top": "12mm", "bottom": "12mm", "left": "11mm", "right": "11mm"},
           display_header_footer=True, header_template="<span></span>",
           footer_template='<div style="width:100%;font-size:8px;color:#888;text-align:center;font-family:sans-serif"><span class="pageNumber"></span> / <span class="totalPages"></span></div>')
    b.close()
if errs:
    print("page errors:", errs[:3])
print("Wrote", dst, os.path.getsize(dst), "bytes")
