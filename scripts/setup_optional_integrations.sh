#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
lock_file="$repo_root/integrations/integrations.lock.json"

mkdir -p "$repo_root/.integrations"

while IFS=$'\t' read -r integration_id repository commit checkout; do
  destination="$repo_root/$checkout"
  if [[ -e "$destination" ]]; then
    echo "preserving existing checkout: $checkout"
    continue
  fi

  echo "cloning $integration_id at pinned commit $commit"
  git clone --filter=blob:none --no-checkout "$repository" "$destination"
  git -C "$destination" fetch --depth 1 origin "$commit"
  git -C "$destination" checkout --detach "$commit"
done < <(
  python3 - "$lock_file" <<'PY'
import json
import pathlib
import sys

data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for item in data["integrations"]:
    print("\t".join((item["id"], item["repository"], item["commit"], item["checkout"])))
PY
)

python3 "$repo_root/scripts/check_optional_integrations.py" --root "$repo_root"

cat <<'EOF'
Optional integrations are pinned and ready for inspection.

They are not installed into the documentary runtime and no provider credentials
were requested. Read docs/VISUAL_INTEGRATIONS.md before enabling upstream tools.
EOF
