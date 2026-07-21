#!/usr/bin/env python3
"""Render selected narration or interview takes from a non-destructive master."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess

import yaml


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duration(path: pathlib.Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return float(result.stdout.strip())


def input_args(master: pathlib.Path, segments: list[list[float]]) -> list[str]:
    arguments: list[str] = []
    for start, end in segments:
        if end <= start:
            raise ValueError(f"invalid segment {start}–{end}")
        arguments.extend(["-ss", f"{start:.3f}", "-t", f"{end-start:.3f}", "-i", str(master)])
    return arguments


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=pathlib.Path)
    parser.add_argument("--id")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config_path = args.config.resolve()
    root = config_path.parent.parent if config_path.parent.name == "config" else pathlib.Path.cwd()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    master = (root / config["master"]).resolve()
    output_dir = root / config["output_directory"]
    output_dir.mkdir(parents=True, exist_ok=True)
    if not master.is_file():
        raise SystemExit(f"master not found: {master}")

    entries = config["entries"]
    if args.id:
        entries = [entry for entry in entries if entry["id"] == args.id]
        if len(entries) != 1:
            raise SystemExit(f"take ID is missing or duplicated: {args.id}")

    outputs = []
    for entry in entries:
        stem = entry["id"]
        video = output_dir / f"{stem}.mp4"
        wave = output_dir / f"{stem}.wav"
        if not args.force and (video.exists() or wave.exists()):
            raise SystemExit(f"refusing to overwrite selected take: {stem}")
        segments = entry["segments"]
        arguments = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + input_args(master, segments)
        if len(segments) == 1:
            video_map = ["-map", "0:v:0", "-map", "0:a:0"]
            audio_map = ["-map", "0:a:0"]
        else:
            av_streams = "".join(f"[{index}:v:0][{index}:a:0]" for index in range(len(segments)))
            video_map = [
                "-filter_complex", f"{av_streams}concat=n={len(segments)}:v=1:a=1[outv][outa]",
                "-map", "[outv]", "-map", "[outa]",
            ]
            audio_streams = "".join(f"[{index}:a:0]" for index in range(len(segments)))
            audio_map = [
                "-filter_complex", f"{audio_streams}concat=n={len(segments)}:v=0:a=1[outa]",
                "-map", "[outa]",
            ]
        run(arguments + video_map + [
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video),
        ])
        run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
            + input_args(master, segments)
            + audio_map
            + ["-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", str(wave)]
        )
        run(["ffmpeg", "-v", "error", "-i", str(video), "-map", "0", "-f", "null", "-"])
        outputs.append({
            "id": stem,
            "video": str(video.relative_to(root)),
            "wave": str(wave.relative_to(root)),
            "duration": round(duration(video), 3),
            "video_sha256": sha256(video),
            "wave_sha256": sha256(wave),
        })
        print(f"rendered {stem}")

    manifest = output_dir / "manifest.json"
    manifest.write_text(json.dumps({"master": config["master"], "outputs": outputs}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
