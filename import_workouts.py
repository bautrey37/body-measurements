#!/usr/bin/env python3
"""Import workout/strength data from the Progression app into data/.

Finds the newest Progression export in ~/Downloads (detected by its CSV
header, regardless of filename), aggregates it into weekly metrics, and
writes "data/Workouts - <Name>.csv" using the same
Measurement,Unit,Type,Date schema that generate_graphs.py expects.

Usage:
    python import_workouts.py            # writes "Workouts - Brandon.csv"
    python import_workouts.py Alice      # writes "Workouts - Alice.csv"
"""

import sys
from pathlib import Path

import pandas as pd

DOWNLOADS = Path.home() / "Downloads"
DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_NAME = "Brandon"

LB_TO_KG = 0.45359237

# Progression export header (UTF-8 BOM stripped by utf-8-sig).
PROGRESSION_COLUMNS = {
    "Date", "Time", "Workout Name", "Workout Description", "Exercise Name",
    "Set Order", "Set Timestamp", "Weight", "Weight Unit", "Repetitions",
    "Distance", "Distance Unit", "Set Duration (s)", "RPE", "Set Comment",
    "Session Comment", "Session Duration (s)",
}

# Exercises that count as cardio even when no Distance is recorded.
CARDIO_EXERCISES = {
    "Running on Treadmill", "Running Outdoors", "Cardio Rower",
    "Elliptical Trainer", "Walking on Treadmill", "Stairmaster",
    "Biking Indoors",
}
# Subset of cardio exercises that count as runs.
RUN_EXERCISES = {"Running on Treadmill", "Running Outdoors"}


def _is_progression_csv(path):
    """True if the file's header matches the Progression export schema."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            header = f.readline().strip()
    except (OSError, UnicodeDecodeError):
        return False
    cols = {c.strip() for c in header.split(",")}
    return PROGRESSION_COLUMNS.issubset(cols)


def find_progression_csv():
    """Return the newest Progression CSV in ~/Downloads, or None."""
    candidates = sorted(
        DOWNLOADS.glob("*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        if _is_progression_csv(path):
            return path
    return None


def aggregate_weekly(df):
    """Aggregate set-level rows into weekly long-format metrics.

    Returns a DataFrame with columns Measurement,Unit,Type,Date. Metrics with
    no data in a given week are omitted (no zero rows emitted).
    """
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for col in ("Weight", "Repetitions", "Distance", "Set Duration (s)"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date"])

    # Normalize weight to kg.
    is_lb = df["Weight Unit"].astype(str).str.strip().str.lower() == "lb"
    df["weight_kg"] = df["Weight"].where(~is_lb, df["Weight"] * LB_TO_KG)

    # Classify rows.
    exercise = df["Exercise Name"].astype(str)
    has_distance = df["Distance"].notna()
    is_cardio = has_distance | exercise.isin(CARDIO_EXERCISES)
    is_run = exercise.isin(RUN_EXERCISES)
    is_strength = df["weight_kg"].notna() & df["Repetitions"].notna() & ~is_cardio

    df["week"] = df["Date"].dt.to_period("W-MON").dt.start_time

    records = []

    strength = df[is_strength]
    for week, grp in strength.groupby("week"):
        volume = (grp["weight_kg"] * grp["Repetitions"]).sum()
        if volume > 0:
            records.append((round(volume, 2), "kg", "Strength Volume", week))
        sessions = grp["Date"].dt.normalize().nunique()
        if sessions > 0:
            records.append((round(float(sessions), 2), "count", "Strength Sessions", week))

    runs = df[is_run]
    for week, grp in runs.groupby("week"):
        dist = grp["Distance"].sum()
        if dist > 0:
            records.append((round(dist, 2), "km", "Run Distance", week))

    cardio = df[is_cardio]
    for week, grp in cardio.groupby("week"):
        dist = grp["Distance"].sum()
        if dist > 0:
            records.append((round(dist, 2), "km", "Cardio Distance", week))
        duration_min = grp["Set Duration (s)"].sum() / 60.0
        if duration_min > 0:
            records.append((round(duration_min, 2), "min", "Cardio Duration", week))

    out = pd.DataFrame(records, columns=["Measurement", "Unit", "Type", "Date"])
    out["Date"] = pd.to_datetime(out["Date"]).dt.strftime("%Y-%m-%d")
    out = out.sort_values(["Date", "Type"]).reset_index(drop=True)
    return out


def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NAME

    src = find_progression_csv()
    if src is None:
        print(f"No Progression export found in {DOWNLOADS}")
        return 1
    print(f"Found Progression export: {src}")

    df = pd.read_csv(src, encoding="utf-8-sig")
    print(f"Read {len(df)} set rows")

    out = aggregate_weekly(df)
    if out.empty:
        print("No weekly metrics produced (no usable rows)")
        return 1

    DATA_DIR.mkdir(exist_ok=True)
    dest = DATA_DIR / f"Workouts - {name}.csv"
    out.to_csv(dest, index=False)

    print(f"\nWrote {len(out)} rows -> {dest}")
    print(f"Date range: {out['Date'].min()} to {out['Date'].max()}")
    print("Per-Type counts:")
    for type_name, count in out["Type"].value_counts().sort_index().items():
        print(f"  {type_name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
