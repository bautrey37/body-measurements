#!/usr/bin/env python3
"""Import body measurement CSV files from the Downloads folder into data/.

Finds files named "Body Measurements - <Name>.csv" in ~/Downloads and copies
them into the project's data/ folder. If multiple copies of the same file
exist, the most recently modified one wins.

Usage:
    python import_data.py            # import all matching files
    python import_data.py Brandon    # import only "Body Measurements - Brandon.csv"
"""

import shutil
import sys
from pathlib import Path

DOWNLOADS = Path.home() / "Downloads"
DATA_DIR = Path(__file__).resolve().parent / "data"
PATTERN = "Body Measurements - *.csv"


def main() -> int:
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None

    matches = sorted(
        DOWNLOADS.glob(PATTERN),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if name_filter:
        matches = [p for p in matches if p.stem == f"Body Measurements - {name_filter}"]

    if not matches:
        target = name_filter or "any user"
        print(f"No '{PATTERN}' files for {target} found in {DOWNLOADS}")
        return 1

    # Keep only the newest file per destination name.
    seen: set[str] = set()
    imported = 0
    for src in matches:
        if src.name in seen:
            continue
        seen.add(src.name)

        dest = DATA_DIR / src.name
        shutil.copy2(src, dest)
        print(f"Imported {src.name} -> {dest}")
        imported += 1

    print(f"\nDone. {imported} file(s) imported into {DATA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
