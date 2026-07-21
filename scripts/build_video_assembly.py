#!/usr/bin/env python3
"""Build a uniform rough-cut picture assembly and mux the locked audio program."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

import yaml


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=pathlib.Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path.cwd().resolve()
    data = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    render = yaml.safe_load((root / "config/render.yaml").read_text(encoding="utf-8"))
    width = int(render["video"]["width"])
    height = int(render["video"]["height"])
    fps = int(render["video"]["frame_rate"])
    output = root / data["output"]
    audio = root / data["audio_program"]
    if not audio.is_file():
        raise SystemExit(f"audio program not found: {audio}")
    if output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite: {output}")

    segment_dir = output.parent / f"{output.stem}-segments"
    segment_dir.mkdir(parents=True, exist_ok=True)
    concat_lines = []
    manifest_entries = []
    for entry in sorted(data["entries"], key=lambda item: item["order"]):
        order = int(entry["order"])
        duration = float(entry["duration"])
        segment = segment_dir / f"{order:03d}.mp4"
        if segment.exists() and not args.force:
            raise SystemExit(f"refusing to overwrite segment: {segment}")
        picture_name = entry.get("picture_asset")
        if picture_name:
            picture = root / picture_name
            if not picture.is_file():
                raise SystemExit(f"picture asset not found for order {order}: {picture}")
            if picture.suffix.lower() in IMAGE_SUFFIXES:
                inputs = ["-loop", "1", "-i", str(picture)]
            else:
                inputs = ["-i", str(picture)]
            filter_video = (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x07111d,"
                f"setsar=1,fps={fps},tpad=stop_mode=clone:stop_duration=1"
            )
        else:
            inputs = [
                "-f", "lavfi", "-i",
                f"color=c=0x07111d:s={width}x{height}:r={fps}:d={duration:.3f}",
            ]
            filter_video = "format=yuv420p"
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
            "-t", f"{duration:.3f}", "-an", "-vf", filter_video,
            "-c:v", "libx264", "-preset", render["video"]["review_preset"],
            "-crf", str(render["video"]["review_crf"]), "-r", str(fps),
            "-pix_fmt", render["video"]["pixel_format"], str(segment),
        ])
        escaped = str(segment).replace("'", "'\\''")
        concat_lines.append(f"file '{escaped}'")
        manifest_entries.append({
            "order": order,
            "duration": duration,
            "picture_asset": picture_name,
            "segment": str(segment.relative_to(root)),
            "picture_status": entry.get("picture_status", "unspecified"),
        })

    concat = segment_dir / "concat.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    picture_program = output.parent / f"{output.stem}-video-only.mp4"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-map", "0:v:0", "-c:v", "copy", str(picture_program),
    ])
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(picture_program), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-c:a", "aac", "-b:a", render["audio"]["review_bitrate"],
        "-ar", str(render["audio"]["sample_rate"]), "-ac", str(render["audio"]["channels"]),
        "-shortest", "-movflags", "+faststart", str(output),
    ])
    run(["ffmpeg", "-v", "error", "-i", str(output), "-map", "0", "-f", "null", "-"])
    output.with_suffix(output.suffix + ".manifest.json").write_text(
        json.dumps({
            "config": str(args.config),
            "audio_program": data["audio_program"],
            "output": data["output"],
            "entries": manifest_entries,
            "full_decode_verified": True,
        }, indent=2) + "\n"
    )
    print(f"built and decode-verified video assembly: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
