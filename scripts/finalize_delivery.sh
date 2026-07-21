#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 INPUT_MP4 OUTPUT_MP4" >&2
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
ffmpeg -y -hide_banner -loglevel error -i "$input" \
  -map 0:v:0 -map '0:a?' -map_metadata 0 \
  -c copy -movflags +faststart "$output"

ffmpeg -v error -i "$output" -map 0 -f null -
ffprobe -v error -show_format -show_streams -of json "$output" > "$output.ffprobe.json"
sha256sum -- "$output" > "$output.sha256"

echo "delivery remuxed without re-encoding and fully decode-verified: $output"
