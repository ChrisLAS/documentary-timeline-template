#!/usr/bin/env python3
"""Render waveform, silence, and frame evidence around one edit boundary."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess


SILENCE_START = re.compile(r"silence_start: ([0-9.]+)")
SILENCE_END = re.compile(r"silence_end: ([0-9.]+)")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=pathlib.Path)
    parser.add_argument("center_seconds", type=float)
    parser.add_argument("output_directory", type=pathlib.Path)
    parser.add_argument("--window", type=float, default=4.0)
    args = parser.parse_args()

    if not args.media.is_file():
        raise SystemExit(f"media not found: {args.media}")
    output = args.output_directory
    output.mkdir(parents=True, exist_ok=True)
    start = max(0.0, args.center_seconds - args.window / 2)

    waveform = output / "waveform.png"
    frames = output / "frames.png"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{start:.3f}", "-t", f"{args.window:.3f}", "-i", str(args.media),
        "-filter_complex",
        "showwavespic=s=1600x260:colors=0x42a5f5,format=rgba,"
        "drawbox=x=799:y=0:w=3:h=260:color=0xff5252@0.9:t=fill",
        "-frames:v", "1", str(waveform),
    ])
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{start:.3f}", "-t", f"{args.window:.3f}", "-i", str(args.media),
        "-vf", "fps=2,scale=400:-2:flags=lanczos,tile=4x2:padding=4:margin=4:color=black",
        "-frames:v", "1", str(frames),
    ])
    silence = run([
        "ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start:.3f}",
        "-t", f"{args.window:.3f}", "-i", str(args.media),
        "-af", "silencedetect=noise=-38dB:d=0.08", "-f", "null", "-",
    ])

    events: list[dict[str, float | None]] = []
    open_start: float | None = None
    for line in silence.stderr.splitlines():
        start_match = SILENCE_START.search(line)
        if start_match:
            open_start = float(start_match.group(1))
        end_match = SILENCE_END.search(line)
        if end_match:
            events.append({"start_relative": open_start, "end_relative": float(end_match.group(1))})
            open_start = None

    result = {
        "media": str(args.media),
        "center_seconds": args.center_seconds,
        "window_start_seconds": start,
        "window_duration_seconds": args.window,
        "silence_events": events,
        "waveform": str(waveform),
        "frames": str(frames),
    }
    (output / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote boundary evidence to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
