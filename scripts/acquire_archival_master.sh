#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 SOURCE_ID URL" >&2
  exit 2
fi

source_id=$1
source_url=$2
source_dir="sources/$source_id"
master_dir="$source_dir/media"

if [[ ! $source_id =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "invalid source ID: use lowercase letters, numbers, and hyphens" >&2
  exit 2
fi
if [[ ! $source_url =~ ^https?:// ]]; then
  echo "invalid URL: expected http:// or https://" >&2
  exit 2
fi
if [[ ! -f "$source_dir/source-url.txt" ]]; then
  echo "run scripts/acquire_source_metadata.sh first for $source_id" >&2
  exit 1
fi
if [[ -d "$master_dir" ]] && find "$master_dir" -mindepth 1 -print -quit | grep -q .; then
  echo "refusing to overwrite or add to non-empty master directory: $master_dir" >&2
  exit 1
fi

mkdir -p "$master_dir"
command=(
  yt-dlp
  --no-overwrites
  --write-info-json
  --write-description
  --write-thumbnail
  --write-subs
  --write-auto-subs
  --sub-langs 'all,-live_chat'
  --sub-format 'vtt/best'
  --format 'bestvideo+bestaudio/best'
  --merge-output-format mkv
  --output "$master_dir/master.%(ext)s"
  "$source_url"
)

printf '%q ' "${command[@]}" > "$source_dir/master-acquisition-command.txt"
printf '\n' >> "$source_dir/master-acquisition-command.txt"
"${command[@]}"

echo "archival source saved under $master_dir; run scripts/probe_media.sh next"
