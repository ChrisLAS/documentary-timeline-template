#!/usr/bin/env python3
"""Build a PCM radio edit from timeline entries with prepared audio assets."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

import yaml


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("timeline", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path.cwd().resolve()
    timeline = yaml.safe_load(args.timeline.read_text(encoding="utf-8"))
    output = args.output.resolve()
    if output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite: {output}")

    assets = output.parent / f"{output.stem}-assets"
    assets.mkdir(parents=True, exist_ok=True)
    concat_lines = []
    manifest_entries = []
    for entry in timeline["entries"]:
        order = int(entry["order"])
        content_duration = float(entry["duration"])
        transition = float(entry.get("transition_out_seconds", 0.0))
        target = content_duration + transition
        rendered = assets / f"{order:03d}.wav"
        if rendered.exists() and not args.force:
            raise SystemExit(f"refusing to overwrite timeline asset: {rendered}")
        if entry["type"] == "Silence":
            command = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{target:.3f}",
            ]
        else:
            asset_name = entry.get("asset")
            if not asset_name:
                raise SystemExit(f"radio order {order} has no audio asset")
            asset = root / asset_name
            if not asset.is_file():
                raise SystemExit(f"radio order {order} asset not found: {asset}")
            command = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(asset),
                "-af", "apad", "-t", f"{target:.3f}",
            ]
        run(command + ["-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", str(rendered)])
        escaped = str(rendered).replace("'", "'\\''")
        concat_lines.append(f"file '{escaped}'")
        manifest_entries.append({
            "order": order,
            "type": entry["type"],
            "content_duration": content_duration,
            "transition_out_seconds": transition,
            "rendered_duration": target,
            "asset": str(rendered.relative_to(root)),
        })

    concat = assets / "concat.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c", "copy", str(output),
    ])
    run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"])
    output.with_suffix(output.suffix + ".manifest.json").write_text(
        json.dumps({"timeline": str(args.timeline), "output": str(output), "entries": manifest_entries}, indent=2) + "\n"
    )
    print(f"built and decode-verified audio timeline: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
