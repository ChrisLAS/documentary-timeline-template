#!/usr/bin/env bash
set -euo pipefail

template_root=$(cd "$(dirname "$0")/.." && pwd)
smoke_root=$(mktemp -d /tmp/documentary-template-smoke.XXXXXX)
trap 'rm -rf -- "$smoke_root"' EXIT

mkdir -p \
  "$smoke_root/config" \
  "$smoke_root/timeline" \
  "$smoke_root/sources/host-narration/media" \
  "$smoke_root/music" \
  "$smoke_root/renders/assemblies"

cp "$template_root/config/render.yaml" "$smoke_root/config/render.yaml"
cp "$template_root/tests/fixtures/smoke/selected-takes.yaml" "$smoke_root/config/selected-takes.yaml"
cp "$template_root/tests/fixtures/smoke/radio-edit.yaml" "$smoke_root/timeline/radio-edit.yaml"
cp "$template_root/tests/fixtures/smoke/music-cues.yaml" "$smoke_root/timeline/music-cues.yaml"
cp "$template_root/tests/fixtures/smoke/video-assembly.yaml" "$smoke_root/timeline/video-assembly.yaml"

ffmpeg -y -hide_banner -loglevel error \
  -f lavfi -i color=c=0x17324d:s=1280x720:r=30:d=3 \
  -f lavfi -i sine=frequency=440:sample_rate=48000:duration=3 \
  -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac \
  "$smoke_root/sources/host-narration/media/master.mp4"
ffmpeg -y -hide_banner -loglevel error \
  -f lavfi -i sine=frequency=220:sample_rate=48000:duration=3 \
  -c:a pcm_s24le "$smoke_root/music/test.wav"

cd "$smoke_root"
python "$template_root/scripts/render_selected_takes.py" config/selected-takes.yaml
python "$template_root/scripts/build_audio_timeline.py" \
  timeline/radio-edit.yaml renders/assemblies/radio-edit.wav
python "$template_root/scripts/render_music_pass.py" timeline/music-cues.yaml
python "$template_root/scripts/build_video_assembly.py" timeline/video-assembly.yaml
"$template_root/scripts/finalize_delivery.sh" \
  renders/assemblies/rough-cut.mp4 renders/assemblies/delivery.mp4

test -s renders/selected-takes/manifest.json
test -s renders/assemblies/radio-edit.wav.manifest.json
test -s renders/assemblies/radio-edit-music.wav
test -s renders/assemblies/rough-cut.mp4.manifest.json
test -s renders/assemblies/delivery.mp4.sha256

echo "media pipeline smoke test passed"
