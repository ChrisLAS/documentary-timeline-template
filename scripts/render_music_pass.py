#!/usr/bin/env python3
"""Mix sparse, configured music cues beneath a locked audio program."""

from __future__ import annotations

import argparse
import pathlib
import subprocess

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=pathlib.Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path.cwd().resolve()
    data = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    program = root / data["program"]
    output = root / data["output"]
    if not program.is_file():
        raise SystemExit(f"program not found: {program}")
    if output.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    tracks: list[pathlib.Path] = []
    track_indexes: dict[pathlib.Path, int] = {}
    for cue in data["cues"]:
        track = (root / cue["track"]).resolve()
        if not track.is_file():
            raise SystemExit(f"music track not found: {track}")
        if track not in track_indexes:
            track_indexes[track] = len(tracks) + 1
            tracks.append(track)

    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(program)]
    for track in tracks:
        command.extend(["-i", str(track)])

    filters = []
    labels = []
    for index, cue in enumerate(data["cues"]):
        length = float(cue["duration"])
        fade_out = float(cue.get("fade_out", 0.0))
        label = f"cue{index}"
        delay = int(round(float(cue["program_in"]) * 1000))
        filters.append(
            f"[{track_indexes[(root / cue['track']).resolve()]}:a]"
            f"atrim=start={float(cue.get('track_in', 0.0)):.3f}:duration={length:.3f},"
            f"asetpts=PTS-STARTPTS,volume={float(cue.get('gain_db', -18.0)):.1f}dB,"
            f"afade=t=in:st=0:d={float(cue.get('fade_in', 0.0)):.3f},"
            f"afade=t=out:st={max(0.0, length-fade_out):.3f}:d={fade_out:.3f},"
            f"adelay={delay}:all=1[{label}]"
        )
        labels.append(f"[{label}]")
    if labels:
        filters.append(
            "[0:a]asetpts=PTS-STARTPTS[program];[program]"
            + "".join(labels)
            + f"amix=inputs={1+len(labels)}:duration=first:normalize=0[mix]"
        )
        command.extend(["-filter_complex", ";".join(filters), "-map", "[mix]"])
    else:
        command.extend(["-map", "0:a:0"])
    command.extend(["-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", str(output)])
    subprocess.run(command, check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"], check=True)
    print(f"rendered and decode-verified music pass: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
