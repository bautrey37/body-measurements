#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "$script_dir/../../../.." && pwd)"
sheet_id="1U06xbIb4CJxKM3gv7V3JSuUOYF9lJ63nrBaUhksYjYQ"
tab_gid="2119120537"
target_csv="$project_dir/data/Body Measurements - Brandon.csv"
temp_csv="$(mktemp "${TMPDIR:-/tmp}/brandon-measurements.XXXXXX.csv")"
venv_dir="${TMPDIR:-/tmp}/body-measurements-graphs-venv"

cleanup() {
  rm -f "$temp_csv"
}
trap cleanup EXIT

curl --fail --location --silent --show-error \
  "https://docs.google.com/spreadsheets/d/${sheet_id}/export?format=csv&gid=${tab_gid}" \
  --output "$temp_csv"

if [[ "$(head -n 1 "$temp_csv" | tr -d '\r')" != "Measurement,Unit,Type,Date" ]]; then
  printf 'Unexpected CSV header; leaving existing data unchanged.\n' >&2
  exit 1
fi

mv "$temp_csv" "$target_csv"
trap - EXIT

if [[ ! -x "$venv_dir/bin/python" ]]; then
  python3 -m venv "$venv_dir"
  "$venv_dir/bin/pip" install -r "$project_dir/requirements.txt"
fi

"$venv_dir/bin/python" "$project_dir/generate_graphs.py"
printf 'Updated %s (%s measurements)\n' "$target_csv" "$(awk 'END { print NR - 1 }' "$target_csv")"
printf 'Regenerated %s Brandon graphs\n' "$(find "$project_dir/out/Brandon" -type f -name '*.png' | wc -l | tr -d ' ')"
