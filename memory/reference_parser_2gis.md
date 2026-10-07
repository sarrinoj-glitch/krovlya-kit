---
name: reference-parser-2gis
description: Working 2GIS scraper command at ~/Downloads/parser2gis-env/bin/parser-2gis — anti-bot tweaks
metadata: 
  node_type: memory
  type: reference
  modified: 2026-10-04T11:57:35.918Z
---

User has `parser-2gis 1.2.1` installed in a venv at `~/Downloads/parser2gis-env/`.

**Working CLI invocation** (verified produces non-empty output as of 2026-05):
```bash
~/Downloads/parser2gis-env/bin/parser-2gis \
  -i "https://2gis.ru/moscow/search/<QUERY>" \
  -o ~/Desktop/<NAME>.json \
  -f json \
  --chrome.headless no \
  --chrome.disable-images no \
  --chrome.start-maximized yes \
  --parser.max-records 500 \
  --parser.delay_between_clicks 500
```

**Critical gotchas:**
- `--chrome.headless yes` → 2GIS anti-bot timeout, 0 records written.
- `--chrome.disable-images yes` (the default) → same anti-bot trigger.
- CSV format hits a cleanup bug in post-processing that wipes data on error. **Use JSON.**
- Output JSON has a UTF-8 BOM — load with `encoding='utf-8-sig'` in Python.

- If the venv is missing (it was on 2026-10-04): `python3 -m venv ~/Downloads/parser2gis-env && ~/Downloads/parser2gis-env/bin/pip install ~/Downloads/parser-2gis-1.2.1` — source folder is still in Downloads.
- Record `id` = `<stable>_<per-request hash>`; the same firm repeats across queries/pages. Dedup on `id.split("_")[0]` and on phone, not on raw id.
- A rubric is finite: "кровельные работы" in the Krasnodar project gave ~150 unique firms for the whole region (only ~80 in Krasnodar city + suburbs). Text queries also return other regions — filter by `adm_div[type=region]`; city is `adm_div[type=city|settlement]`.
- `whatsapp` contact value is a `wa.me/7XXXXXXXXXX?text=...` URL — extract the number with a regex.

**Sample output structure:** records have `name`, `name_ex.{primary,legal_name}`,
`contact_groups[].contacts[]` with `type` ∈ {phone, website, whatsapp, telegram}, `rubrics[]`,
`reviews.{general_rating, general_review_count}`, `dates.created_at`, `address.components[]`.

For cold-call CSV format: extract name + first phone + website + has-site flag + reviews count.
Priority bucket: no-site → A (highest call priority), site + reviews<30 → B, well-reviewed → C.

