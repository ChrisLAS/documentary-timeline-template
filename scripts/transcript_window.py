#!/usr/bin/env python3
"""Print transcript segments overlapping an editorial time window."""

from __future__ import annotations

import argparse
import json
import pathlib


def milliseconds(value: str) -> int:
    parts = value.replace(",", ".").split(":")
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise argparse.ArgumentTypeError("time must be MM:SS or HH:MM:SS")
    return int((int(hours) * 3600 + int(minutes) * 60 + float(seconds)) * 1000)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=pathlib.Path)
    parser.add_argument("start", type=milliseconds)
    parser.add_argument("end", type=milliseconds)
    args = parser.parse_args()

    data = json.loads(args.transcript.read_text(encoding="utf-8"))
    entries = data.get("segments", data.get("transcription", []))
    for item in entries:
        if "start_ms" in item:
            start_ms, end_ms = item["start_ms"], item["end_ms"]
            start_label, end_label = item.get("start", start_ms), item.get("end", end_ms)
        elif "offsets" in item:
            start_ms = item["offsets"]["from"]
            end_ms = item["offsets"]["to"]
            start_label = item.get("timestamps", {}).get("from", start_ms)
            end_label = item.get("timestamps", {}).get("to", end_ms)
        else:
            continue
        if end_ms < args.start or start_ms > args.end:
            continue
        check = " [CHECK]" if item.get("uncertain_tokens") else ""
        print(f"{start_label} --> {end_label}{check}\n{item.get('text', '').strip()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
