#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
skill_name=documentary-visual-development
source_skill="$repo_root/skills/$skill_name"
codex_root=${CODEX_HOME:-${HOME:?HOME is required}/.codex}
target="$codex_root/skills/$skill_name"
mode='link'

if [[ ${1:-} == "--copy" ]]; then
  mode='copy'
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--copy]" >&2
  exit 2
fi

if [[ -L "$target" ]] && [[ $(readlink -f "$target") == $(readlink -f "$source_skill") ]]; then
  echo "skill already linked: $target"
  exit 0
fi
if [[ -e "$target" || -L "$target" ]]; then
  echo "refusing to replace existing skill: $target" >&2
  exit 1
fi

mkdir -p "$(dirname "$target")"
if [[ $mode == copy ]]; then
  cp -a "$source_skill" "$target"
  echo "copied skill to $target"
else
  ln -s "$source_skill" "$target"
  echo "linked skill at $target"
fi
