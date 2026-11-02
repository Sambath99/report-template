# Report template

A simple, phone-friendly report page with tabs and many chart types (donut, bars, columns, line, stacked columns, dot chart, tables). Put your data in, run one command, and open `report.html`.

Tabs: Overview, Content, Time, Likes and shares, All posts, What to do (Stop / Keep / Improve).

## Use it in 3 steps

1. Click **Use this template** on GitHub (or download the files).
2. Put your rows in `data.csv`. One row per post (or sale, class, product). Columns:

   | Column | Example | Meaning |
   |---|---|---|
   | dt | `2026-10-24 08:00` | Date and local time |
   | hour | `8` | Hour of the day, 0 to 23 |
   | day | `Sat` | Day of the week |
   | format | `Video` | Video, Photo, Text post (any names work) |
   | category | `Resource lists` | Your own content groups, 5 to 10 groups work best |
   | topic | `5 free websites` | Short plain description |
   | views | `1200` | Views |
   | reach | `800` | People reached (use 0 if unknown) |
   | reactions | `30` | Likes, loves, and so on |
   | comments | `2` | Comments |
   | shares | `5` | Shares |

   `example_fake_data.csv` shows the format with made-up numbers. Do not publish it as a real report.
3. Edit `config.json` (title, subtitle, and your own Stop / Keep / Improve lines), then run:

   ```
   python build_report.py
   ```

   Open `report.html` in a browser. Add `--inline-d3` to put the chart library inside the file, so it works with no internet (use this when you send the file by Telegram or email).

Try it first with the fake data: `python build_report.py --data example_fake_data.csv`

## Writing the advice

Look at the charts, then write 3 or 4 short lines for each of Stop, Keep, Improve in `config.json`. Use `**bold**` for the main words and put a real number in every line, for example: `**Promo videos after 9 PM.** A typical one gets only 262 views.`

## Notes

- Dates in `dt` must look like `YYYY-MM-DD HH:MM`. Weeks are 1-7, 8-14, 15-21, 22-28, 29-31 of the month.
- The report uses the typical post (median), not the average, so one huge post does not hide the rest.
- "Good / Weak / Very low" compares each group with the typical post of the whole month.
- Stories: set `"stories": {"checked": "2026-10-31 18:05", "live_stories": 0}` in `config.json` to show a stories tile. Leave it `null` to hide it.
- If you use Claude, ask it to use the `report-artifact-making` skill and this template: it pulls the data, checks the counts, fills `data.csv` and `config.json`, and builds the file.

## Make the file open on iPhone (pre-render step)

iPhone previews (Telegram, Files, Mail) block JavaScript, so a plain report.html shows empty dashes there. Run prerender.py once after building and the file shows all numbers, tables and charts even with JavaScript off. In a normal browser it still works with tabs, sorting and filters.

```
pip install playwright
python -m playwright install chromium
python prerender.py report.html report_static.html
```

Send report_static.html to your phone.
