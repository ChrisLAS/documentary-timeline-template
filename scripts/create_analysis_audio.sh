#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 INPUT_MEDIA OUTPUT_WAV" >&2
  exit 2
fi

input=$1
output=$2

if [[ ! -f "$input" ]]; then
  echo "input not found: $input" >&2
  exit 1
fi
if [[ -e "$output" ]]; then
  echo "refusing to overwrite: $output" >&2
  exit 1
fi

mkdir -p "$(dirname "$output")"
ffmpeg -hide_banner -loglevel error -i "$input" -map 0:a:0 \
  -vn -ac 1 -ar 16000 -c:a pcm_s16le "$output"

echo "created analysis audio: $output"
