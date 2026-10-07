---
name: reference-html-to-pdf
description: Working HTML→PDF pipeline on this Mac — headless Chrome plus the print-CSS rules that keep layouts from breaking
metadata: 
  node_type: memory
  type: reference
  modified: 2026-08-02T22:48:38.806Z
---

**Use headless Chrome, not a converter.** `weasyprint` and `wkhtmltopdf` are not installed here, and neither handles CSS Grid — layouts silently collapse. Chrome renders exactly what the browser shows.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=6000 \
  --print-to-pdf="out.pdf" "file://$PWD/page.html"
```

**Print CSS that actually matters**

- `@page { size: 1080px 1440px; margin: 0 }` — for fixed-size slides. For documents use `size: A4; margin: 15mm 13mm 18mm`
- `print-color-adjust: exact !important` (plus `-webkit-` prefix) on `*` — **without this Chrome strips every background colour**, so callout panels and tinted table rows come out white
- `break-inside: avoid` on tables, cards, callouts, figure boxes — stops blocks splitting across pages
- `thead { display: table-header-group }` — repeats headers on long tables
- `break-after: avoid` on headings and captions so they don't strand at a page bottom
- `orphans: 3; widows: 3` on `p, li`
- Force light tokens inside `@media print` — otherwise a dark-theme viewer exports a dark PDF
- For slide decks: each `<section>` gets `page-break-after: always` + fixed height

**Always verify visually.** `pdftoppm` (poppler) is installed:

```bash
pdftoppm -png -r 46 out.pdf prev/p     # render every page
pdfinfo out.pdf | grep -E "Pages|Page size"
```

Then tile the PNGs into one contact sheet with PIL and Read it — catches overflow, clipped text and broken grids in a single look. This caught real problems both times I've used it.
