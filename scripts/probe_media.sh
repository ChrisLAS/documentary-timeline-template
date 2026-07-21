#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 MEDIA_FILE SOURCE_ID" >&2
  exit 2
fi

media=$1
source_id=$2
source_dir="sources/$source_id"
probe="$source_dir/ffprobe.json"
checksum="$source_dir/checksum.sha256"

if [[ ! -f "$media" ]]; then
  echo "media file not found: $media" >&2
  exit 1
fi
if [[ -e "$probe" || -e "$checksum" ]]; then
  echo "refusing to overwrite existing probe or checksum for $source_id" >&2
  exit 1
fi

mkdir -p "$source_dir"
probe_tmp=$(mktemp "$source_dir/.ffprobe.XXXXXX")
ffprobe -v error -show_format -show_streams -of json "$media" > "$probe_tmp"
mv "$probe_tmp" "$probe"

digest=$(sha256sum -- "$media" | cut -d ' ' -f1)
printf '%s  %s\n' "$digest" "$(basename "$media")" > "$checksum"

echo "wrote $probe and $checksum"
