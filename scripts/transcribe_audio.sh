#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "usage: $0 INPUT_AUDIO OUTPUT_PREFIX [MODEL] [THREADS]" >&2
  exit 2
fi

input=$1
output_prefix=$2
model=${3:-models/ggml-large-v3-turbo-q5_0.bin}
threads=${4:-10}

if [[ ! -f "$input" ]]; then
  echo "input not found: $input" >&2
  exit 1
fi
if [[ ! -f "$model" ]]; then
  echo "model not found: $model" >&2
  exit 1
fi
for suffix in json txt vtt srt; do
  if [[ -e "$output_prefix.$suffix" ]]; then
    echo "refusing to overwrite $output_prefix.$suffix" >&2
    exit 1
  fi
done

mkdir -p "$(dirname "$output_prefix")" logs
prompt=$(awk '
  /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
  { if (count++) printf ", "; printf "%s", $0 }
  END { if (count) printf "\n" }
' config/vocabulary.txt)
log="logs/transcription-$(basename "$output_prefix").log"
if [[ -e "$log" ]]; then
  echo "refusing to overwrite $log" >&2
  exit 1
fi

command=(
  whisper-cli
  -m "$model"
  -f "$input"
  -l en
  -t "$threads"
  -bo 5
  -bs 5
  -ojf
  -ovtt
  -osrt
  -otxt
  -of "$output_prefix"
)
if [[ -n "$prompt" ]]; then
  command+=(--prompt "$prompt")
fi

printf '%q ' "${command[@]}" > "$output_prefix-command.txt"
printf '\n' >> "$output_prefix-command.txt"
"${command[@]}" > "$log" 2>&1

echo "transcript outputs written to $output_prefix.{json,txt,vtt,srt}"
