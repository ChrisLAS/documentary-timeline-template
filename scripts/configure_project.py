#!/usr/bin/env python3
"""Configure a fresh clone of the documentary timeline template."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re

import yaml


DEFAULT_SLUG = "example-documentary-project"
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def replace_text(path: pathlib.Path, replacements: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--thesis", required=True)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not SLUG_PATTERN.fullmatch(args.slug):
        parser.error("--slug must use lowercase letters, numbers, and single hyphens")

    root = args.root.resolve()
    config_path = root / "config/project.yaml"
    if not config_path.exists():
        raise SystemExit(f"not a template checkout: missing {config_path}")

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    current_slug = config["project"]["slug"]
    if current_slug != DEFAULT_SLUG and not args.force:
        raise SystemExit(
            f"project is already configured as {current_slug}; use --force to replace it"
        )

    today = dt.date.today().isoformat()
    replacements = {
        DEFAULT_SLUG: args.slug,
        "Untitled Documentary Timeline": args.title,
        "Replace this with the central historical argument.": args.thesis,
        "Replace this with the project's controlling historical argument.": args.thesis,
        "YYYY-MM-DD": today,
    }

    configurable = [
        "PROJECT_BRIEF.md",
        "PROJECT_STATUS.md",
        "config/project.yaml",
        "config/selected-takes.yaml",
        "sources.yaml",
        "narrative/thesis.md",
        "narrative/narrative-beats.yaml",
        "candidates/candidates.yaml",
        "timeline/radio-edit.yaml",
        "timeline/rough-cut.yaml",
        "timeline/edit-list.json",
        "timeline/music-cues.yaml",
        "timeline/video-assembly.yaml",
    ]
    for relative in configurable:
        replace_text(root / relative, replacements)

    readme = root / "README.md"
    readme_text = readme.read_text(encoding="utf-8")
    readme_text = readme_text.replace(
        "# Documentary Timeline Template",
        f"# {args.title}\n\nGenerated from the Documentary Timeline Template.",
        1,
    )
    readme.write_text(readme_text, encoding="utf-8")

    print(f"configured {root}")
    print(f"title: {args.title}")
    print(f"slug: {args.slug}")
    print("next: complete PROJECT_BRIEF.md and sources.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
