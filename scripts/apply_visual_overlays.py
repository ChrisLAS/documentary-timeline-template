#!/usr/bin/env python3
"""Promote approved full-frame visual inserts while preserving base audio."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shlex
import subprocess
from fractions import Fraction

import yaml


HASH_RE = re.compile(r"SHA256=([0-9a-f]{64})")


def run(command: list[str], *, capture: bool = False) -> str:
    print(shlex.join(command))
    result = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )
    if capture:
        return (result.stdout or "") + (result.stderr or "")
    return ""


def media_info(path: pathlib.Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_streams", "-show_format",
            "-of", "json", str(path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return json.loads(result.stdout)


def packet_hash(path: pathlib.Path, stream: str) -> str | None:
    info = media_info(path)
    stream_type = "audio" if stream == "a:0" else "video"
    if not any(item.get("codec_type") == stream_type for item in info["streams"]):
        return None
    output = run(
        [
            "ffmpeg", "-v", "error", "-i", str(path), "-map", f"0:{stream}",
            "-c", "copy", "-f", "hash", "-hash", "sha256", "-",
        ],
        capture=True,
    )
    match = HASH_RE.search(output)
    if not match:
        raise RuntimeError(f"could not parse packet hash for {path} stream {stream}")
    return match.group(1)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project_path(root: pathlib.Path, value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    return path if path.is_absolute() else root / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=pathlib.Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path.cwd().resolve()
    config_path = args.config.resolve()
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    render = yaml.safe_load((root / "config/render.yaml").read_text(encoding="utf-8"))
    base = project_path(root, data["base_assembly"])
    output = project_path(root, data["output"])
    if not base.is_file():
        raise SystemExit(f"base assembly not found: {base}")
    if output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite: {output}")

    base_info = media_info(base)
    video = next(item for item in base_info["streams"] if item["codec_type"] == "video")
    width = int(video["width"])
    height = int(video["height"])
    fps = Fraction(video["avg_frame_rate"])
    fps_text = f"{fps.numerator}/{fps.denominator}"
    base_duration = float(base_info["format"]["duration"])

    overlays = []
    for raw in data.get("overlays", []):
        overlay = dict(raw)
        overlay["path"] = project_path(root, overlay["path"])
        overlay["start"] = float(overlay["start"])
        overlay["duration"] = float(overlay["duration"])
        overlay["fade_in"] = float(overlay.get("fade_in", 0.0))
        overlay["fade_out"] = float(overlay.get("fade_out", 0.0))
        overlay["end"] = overlay["start"] + overlay["duration"]
        if not overlay["path"].is_file():
            raise SystemExit(f"overlay not found: {overlay['path']}")
        if overlay["start"] < 0 or overlay["duration"] <= 0:
            raise SystemExit(f"invalid timing for overlay {overlay.get('id')}")
        if overlay["end"] > base_duration + 0.001:
            raise SystemExit(f"overlay exceeds base duration: {overlay.get('id')}")
        if overlay["fade_in"] + overlay["fade_out"] > overlay["duration"]:
            raise SystemExit(f"fades exceed overlay duration: {overlay.get('id')}")
        overlay_info = media_info(overlay["path"])
        overlay_duration = float(overlay_info["format"]["duration"])
        if overlay_duration + (1 / float(fps)) < overlay["duration"]:
            raise SystemExit(
                f"overlay {overlay.get('id')} is {overlay_duration:.3f}s but "
                f"{overlay['duration']:.3f}s is required"
            )
        overlays.append(overlay)

    overlays.sort(key=lambda item: item["start"])
    for previous, current in zip(overlays, overlays[1:]):
        if current["start"] < previous["end"] - 0.0005:
            raise SystemExit(
                f"overlays overlap: {previous.get('id')} and {current.get('id')}"
            )
    if not overlays:
        raise SystemExit("config contains no overlays")

    filter_parts = ["[0:v]setpts=PTS-STARTPTS[v0]"]
    previous_label = "v0"
    for index, overlay in enumerate(overlays, start=1):
        local_label = f"overlay{index}"
        output_label = f"v{index}"
        filters = [
            f"trim=duration={overlay['duration']:.6f}",
            "setpts=PTS-STARTPTS",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black@1",
            "setsar=1",
            f"fps={fps_text}",
            "format=rgba",
        ]
        if overlay["fade_in"] > 0:
            filters.append(
                f"fade=t=in:st=0:d={overlay['fade_in']:.6f}:alpha=1"
            )
        if overlay["fade_out"] > 0:
            fade_start = overlay["duration"] - overlay["fade_out"]
            filters.append(
                f"fade=t=out:st={fade_start:.6f}:d={overlay['fade_out']:.6f}:alpha=1"
            )
        filters.append(f"setpts=PTS+{overlay['start']:.6f}/TB")
        filter_parts.append(f"[{index}:v]{','.join(filters)}[{local_label}]")
        filter_parts.append(
            f"[{previous_label}][{local_label}]overlay=0:0:"
            f"eof_action=pass:enable='between(t,{overlay['start']:.6f},"
            f"{overlay['end']:.6f})'[{output_label}]"
        )
        previous_label = output_label

    command = ["ffmpeg", "-y" if args.force else "-n", "-hide_banner", "-loglevel", "error"]
    command.extend(["-i", str(base)])
    for overlay in overlays:
        command.extend(["-i", str(overlay["path"])])
    command.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", f"[{previous_label}]", "-map", "0:a?", "-map_metadata", "0",
        "-c:v", "libx264",
        "-preset", str(data.get("preset", "slow")),
        "-crf", str(data.get("crf", 18)),
        "-pix_fmt", render["video"]["pixel_format"],
        "-r", fps_text,
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output),
    ])

    if args.dry_run:
        print(shlex.join(command))
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    base_audio_hash = packet_hash(base, "a:0")
    run(command)
    run(["ffmpeg", "-v", "error", "-i", str(output), "-map", "0", "-f", "null", "-"])
    output_audio_hash = packet_hash(output, "a:0")
    if base_audio_hash != output_audio_hash:
        output.unlink(missing_ok=True)
        raise SystemExit("audio packet hash changed; removed invalid output")

    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(
        json.dumps(
            {
                "config": str(config_path),
                "base_assembly": str(base),
                "output": str(output),
                "duration": float(media_info(output)["format"]["duration"]),
                "sha256": sha256(output),
                "audio_packet_sha256": output_audio_hash,
                "audio_stream_preserved": True,
                "full_decode_verified": True,
                "overlays": [
                    {
                        "id": item.get("id"),
                        "path": str(item["path"]),
                        "start": item["start"],
                        "end": item["end"],
                        "fade_in": item["fade_in"],
                        "fade_out": item["fade_out"],
                    }
                    for item in overlays
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"built and decode-verified visual assembly: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
