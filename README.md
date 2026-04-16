# Body Measurements Data Analysis

Generates per-user graphs from body measurement CSV files in `data/`, split
across multiple timeframes (all-time, last 1 year, last 2 years).

## Quick start for a new user

1. Install deps: `pip install -r requirements.txt`.
2. Run as-is against the shipped example to confirm things work:
   ```bash
   python generate_graphs.py
   ```
   You should see graphs under `out/Example/`.
3. Add your own data: drop a CSV in `data/` named
   `Body Measurements - <YourName>.csv` (the part after ` - ` becomes
   the user folder under `out/`).
4. Optional — copy `data/users.json.example` to `data/users.json` and
   add your height (and anyone else's) so BMI is accurate:
   ```bash
   cp data/users.json.example data/users.json
   ```
5. Run again. Your graphs land in `out/<YourName>/`.

Everything under `data/` except the shipped `*.example*` files is
gitignored, so your measurements never leave your machine.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python generate_graphs.py
```

Every `*.csv` file in `data/` is processed. The user name is derived from
the filename (the part after the last ` - ` in the stem), so
`Body Measurements - Example.csv` → user `Example`.

## CSV format

Expected columns (names are auto-detected, case-insensitive):

- **Date** / time / timestamp
- **Type** / category / kind (e.g. `Weight`, `Waist`, `Body Fat`, ...)
- **Value** / measurement / amount

## User profiles (`data/users.json`)

Per-user info is read from `data/users.json`. Missing users fall back to
defaults.

```json
{
  "Alice": { "height_m": 1.65, "gender": "female" },
  "Bob":   { "height_m": 1.80, "gender": "male" }
}
```

Fields:

- `height_m` — used to compute BMI. Default: 1.75.
- `gender` — recorded on the profile (not used in BMI; BMI thresholds are
  the same for both sexes per WHO).

The `data/` folder is gitignored, so profiles and CSVs stay local.

## Output layout

```
out/
  <User>/
    combined/        # all-time
      data_graphs_combined_absolute.png
      Weight_graph_absolute.png
      Waist_graph_absolute.png
      Weight_Waist_absolute.png
      BMI_absolute.png
      ...
    1year/           # last 365 days
    2year/           # last 730 days
```

Adding a second user's CSV automatically creates a sibling folder under
`out/` without touching existing users.

## Charts

- **Per-type graphs** — one PNG per measurement type, plus a grid in
  `data_graphs_combined_*.png`. Series with fewer than 4 points in the
  timeframe are skipped.
- **Weight + Waist** — dual y-axis overlay (kg vs cm). Only generated
  when both series have at least 4 points in the timeframe.
- **BMI** — computed from Weight and the user's `height_m`. Shaded zones
  and threshold lines mark:
  - Underweight (BMI < 18.5)
  - Overweight (25–30)
  - Obese (≥ 30)

  The chart title shows the latest BMI and flags `WARNING` when it falls
  in the underweight or obese band.

## Timeframes

| Suffix     | Window                          | Folder     |
| ---------- | ------------------------------- | ---------- |
| `absolute` | All recorded data               | `combined` |
| `1year`    | Last 365 days from latest entry | `1year`    |
| `2year`    | Last 730 days from latest entry | `2year`    |
