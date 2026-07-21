#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 SOURCE_ID URL" >&2
  exit 2
fi

source_id=$1
source_url=$2

if [[ ! $source_id =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "invalid source ID: use lowercase letters, numbers, and hyphens" >&2
  exit 2
fi
if [[ ! $source_url =~ ^https?:// ]]; then
  echo "invalid URL: expected http:// or https://" >&2
  exit 2
fi

source_dir="sources/$source_id"
if [[ -e "$source_dir/source-url.txt" || -e "$source_dir/acquisition-command.txt" ]]; then
  echo "refusing to overwrite existing source record: $source_dir" >&2
  exit 1
fi

mkdir -p "$source_dir"
printf '%s\n' "$source_url" > "$source_dir/source-url.txt"

command=(
  yt-dlp
  --skip-download
  --write-info-json
  --write-description
  --write-thumbnail
  --write-subs
  --write-auto-subs
  --sub-langs 'all,-live_chat'
  --sub-format 'vtt/best'
  --no-write-playlist-metafiles
  --output "$source_dir/platform.%(ext)s"
  "$source_url"
)

printf '%q ' "${command[@]}" > "$source_dir/acquisition-command.txt"
printf '\n' >> "$source_dir/acquisition-command.txt"
"${command[@]}"

echo "metadata and available captions saved under $source_dir"
