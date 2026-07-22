---
name: refresh-body-measurements
description: Download the latest Brandon tab from the configured Google Sheet, replace data/Body Measurements - Brandon.csv, and regenerate all body-measurement charts. Use when the user asks to refresh Brandon's measurements, sync the Google Sheet data, or recreate the project graphs.
---

# Refresh Body Measurements

Run the bundled workflow from the repository root:

```bash
bash .codex/skills/refresh-body-measurements/scripts/refresh_brandon.sh
```

The script downloads Google Sheet tab `2119120537`, validates the
`Measurement,Unit,Type,Date` schema, replaces only
`data/Body Measurements - Brandon.csv`, and runs `generate_graphs.py` in an
isolated temporary Python environment.

Report the updated CSV row count and the number of regenerated PNGs under
`out/Brandon/`. Do not modify workbook or workout CSVs.

If Google returns HTTP 401, ask the user to make the sheet accessible to
anyone with the link (or provide an authenticated export); do not overwrite
the existing data file. If dependencies are absent, allow the script to
install them only in its temporary environment.
