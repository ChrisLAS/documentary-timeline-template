#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 5 || $# -gt 7 ]]; then
  echo "usage: $0 INPUT START_SECONDS END_SECONDS OUTPUT CANDIDATE_ID [HANDLE_BEFORE=5] [HANDLE_AFTER=5]" >&2
  exit 2
fi

input=$1
preferred_start=$2
preferred_end=$3
output=$4
candidate_id=$5
handle_before=${6:-5}
handle_after=${7:-5}

if [[ ! -f "$input" ]]; then
  echo "input not found: $input" >&2
  exit 1
fi
if [[ -e "$output" ]]; then
  echo "refusing to overwrite: $output" >&2
  exit 1
fi

read -r context_start duration < <(
  awk -v s="$preferred_start" -v e="$preferred_end" -v hb="$handle_before" -v ha="$handle_after" '
    BEGIN {
      if (e <= s) exit 2
      cs=s-hb; if (cs < 0) cs=0
      printf "%.3f %.3f\n", cs, (e+ha)-cs
    }
  '
)

mkdir -p "$(dirname "$output")"
label=$(mktemp)
trap 'rm -f "$label"' EXIT
printf '%s | proposed in %.3f | out %.3f' "$candidate_id" "$preferred_start" "$preferred_end" > "$label"

ffmpeg -y -hide_banner -loglevel error -i "$input" \
  -ss "$context_start" -t "$duration" \
  -map 0:v:0 -map 0:a:0 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,drawtext=font='DejaVu Sans':textfile='$label':fontsize=28:fontcolor=white:box=1:boxcolor=black@0.72:boxborderw=12:x=36:y=36" \
  -af "afade=t=in:st=0:d=0.01,afade=t=out:st=$(awk -v d="$duration" 'BEGIN {printf "%.3f", d-0.01}'):d=0.01" \
  -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$output"

ffmpeg -v error -i "$output" -map 0 -f null -
echo "rendered and decode-verified review clip: $output"
