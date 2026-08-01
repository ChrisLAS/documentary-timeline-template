#!/usr/bin/env python3
"""Validate the pinned optional-integration lock and any local checkouts."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlparse


SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def normalize_repository(value: str) -> str:
    value = value.strip().removesuffix("/").removesuffix(".git")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return f"https://{parsed.netloc.lower()}{parsed.path}".lower()
    return value.lower()


def git(checkout: pathlib.Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(checkout), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path)
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()

    root = (args.root or pathlib.Path(__file__).resolve().parents[1]).resolve()
    lock_path = root / "integrations/integrations.lock.json"
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    seen: set[str] = set()

    if data.get("schema_version") != 1:
        errors.append("unsupported integrations.lock.json schema_version")

    for entry in data.get("integrations", []):
        integration_id = entry.get("id", "")
        if not integration_id or integration_id in seen:
            errors.append(f"invalid or duplicate integration id: {integration_id!r}")
            continue
        seen.add(integration_id)

        commit = entry.get("commit", "")
        if not SHA_RE.fullmatch(commit):
            errors.append(f"{integration_id}: commit must be a full 40-character SHA")
        if not entry.get("license"):
            errors.append(f"{integration_id}: license is required")

        relative_checkout = pathlib.PurePosixPath(entry.get("checkout", ""))
        if (
            not relative_checkout.parts
            or relative_checkout.parts[0] != ".integrations"
            or ".." in relative_checkout.parts
        ):
            errors.append(f"{integration_id}: checkout must be under .integrations/")
            continue

        checkout = root.joinpath(*relative_checkout.parts)
        if not checkout.exists():
            message = f"{integration_id}: missing optional checkout {relative_checkout}"
            if args.allow_missing:
                print(f"OPTIONAL {message}")
            else:
                errors.append(message)
            continue
        if not (checkout / ".git").exists():
            errors.append(f"{integration_id}: checkout is not a Git repository: {checkout}")
            continue

        try:
            actual_commit = git(checkout, "rev-parse", "HEAD")
            actual_remote = git(checkout, "remote", "get-url", "origin")
            dirty = git(checkout, "status", "--porcelain")
        except subprocess.CalledProcessError as error:
            errors.append(f"{integration_id}: Git inspection failed: {error.stderr.strip()}")
            continue

        if actual_commit != commit:
            errors.append(
                f"{integration_id}: expected {commit}, found {actual_commit}"
            )
        if normalize_repository(actual_remote) != normalize_repository(entry["repository"]):
            errors.append(
                f"{integration_id}: origin mismatch: {actual_remote}"
            )
        if dirty:
            errors.append(f"{integration_id}: checkout has local modifications")
        if actual_commit == commit and not dirty:
            print(f"OK {integration_id} {actual_commit}")

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(f"validated {len(seen)} optional integration definitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
