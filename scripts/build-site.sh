#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
public_root="$repo_root/site-public"
output_root="$repo_root/dist"
allowlist="$public_root/publish-allowlist.txt"

if [[ ! -f "$allowlist" ]]; then
  echo "Missing public publish allowlist" >&2
  exit 1
fi

python3 "$repo_root/scripts/verify-site.py"

python3 - "$public_root" "$output_root" "$allowlist" <<'PY'
from pathlib import Path
import shutil
import sys

public_root = Path(sys.argv[1]).resolve()
output_root = Path(sys.argv[2]).resolve()
allowlist = Path(sys.argv[3]).resolve()

if output_root.exists():
    shutil.rmtree(output_root)
output_root.mkdir(parents=True)

for raw in allowlist.read_text(encoding="utf-8").splitlines():
    name = raw.strip()
    if not name or name.startswith("#"):
        continue
    source = (public_root / name).resolve()
    if public_root not in source.parents:
        raise SystemExit(f"Allowlist path escapes site-public: {name}")
    if not source.is_file():
        raise SystemExit(f"Allowlisted public file is missing: {name}")
    target = output_root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

print(f"Built {sum(1 for p in output_root.rglob('*') if p.is_file())} public files in {output_root}")
PY
