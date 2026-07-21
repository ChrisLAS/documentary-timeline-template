#!/usr/bin/env python3
"""Validate documentary project structure, schemas, and cross-references."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from collections.abc import Iterable

import jsonschema
import yaml


REQUIRED_PATHS = [
    "PROJECT_BRIEF.md",
    "PROJECT_STATUS.md",
    "config/project.yaml",
    "config/render.yaml",
    "config/selected-takes.yaml",
    "sources.yaml",
    "narrative/thesis.md",
    "narrative/historical-timeline.md",
    "narrative/narrative-beats.yaml",
    "narrative/fact-check-notes.md",
    "candidates/candidates.yaml",
    "candidates/rejected-candidates.md",
    "reviews/boundary-review.md",
    "reviews/editorial-review.md",
    "reviews/duplication-review.md",
    "reviews/historical-review.md",
    "timeline/radio-edit.yaml",
    "timeline/rough-cut.yaml",
    "timeline/edit-list.csv",
    "timeline/edit-list.json",
    "timeline/host-script.md",
    "timeline/music-cues.yaml",
    "timeline/video-assembly.yaml",
]

SCHEMA_TARGETS = {
    "config/project.yaml": "schemas/project.schema.json",
    "sources.yaml": "schemas/sources.schema.json",
    "narrative/narrative-beats.yaml": "schemas/narrative-beats.schema.json",
    "candidates/candidates.yaml": "schemas/candidates.schema.json",
    "timeline/radio-edit.yaml": "schemas/radio-edit.schema.json",
}

FORBIDDEN_TRACKED_PARTS = {"media", "models", "__pycache__"}
SECRET_NAMES = {
    ".env",
    "auth.json",
    "cookies.txt",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
}


def load_yaml(path: pathlib.Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def duplicates(values: Iterable[object]) -> set[object]:
    seen: set[object] = set()
    repeated: set[object] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def publishable_files(root: pathlib.Path) -> list[pathlib.Path]:
    result = subprocess.run(
        [
            "git", "-C", str(root), "ls-files", "--cached", "--others",
            "--exclude-standard", "-z",
        ],
        check=False,
        stdout=subprocess.PIPE,
    )
    if result.returncode != 0:
        return []
    return [root / item.decode() for item in result.stdout.split(b"\0") if item]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            errors.append(f"missing required path: {relative}")

    documents: dict[str, object] = {}
    for target, schema_name in SCHEMA_TARGETS.items():
        target_path = root / target
        schema_path = root / schema_name
        if not target_path.exists() or not schema_path.exists():
            continue
        try:
            document = load_yaml(target_path)
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(document)
            documents[target] = document
        except (yaml.YAMLError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
            errors.append(f"{target}: {exc}")

    config = documents.get("config/project.yaml")
    if isinstance(config, dict):
        slug = config["project"]["slug"]
        for target in (
            "sources.yaml",
            "narrative/narrative-beats.yaml",
            "candidates/candidates.yaml",
            "timeline/radio-edit.yaml",
        ):
            document = documents.get(target)
            if isinstance(document, dict) and document.get("project") != slug:
                errors.append(f"{target}: project slug does not match config/project.yaml")
        if slug == "example-documentary-project":
            warnings.append("project still uses the example slug")

    sources_document = documents.get("sources.yaml") or {}
    beats_document = documents.get("narrative/narrative-beats.yaml") or {}
    candidates_document = documents.get("candidates/candidates.yaml") or {}
    radio_document = documents.get("timeline/radio-edit.yaml") or {}
    sources = sources_document.get("sources", []) if isinstance(sources_document, dict) else []
    beats = beats_document.get("beats", []) if isinstance(beats_document, dict) else []
    candidates = candidates_document.get("candidates", []) if isinstance(candidates_document, dict) else []
    entries = radio_document.get("entries", []) if isinstance(radio_document, dict) else []

    source_ids = [item["id"] for item in sources]
    beat_ids = [item["id"] for item in beats]
    candidate_ids = [item["candidate_id"] for item in candidates]
    for label, values in (
        ("source IDs", source_ids),
        ("narrative beat IDs", beat_ids),
        ("candidate IDs", candidate_ids),
        ("narrative beat order values", [item["order"] for item in beats]),
        ("radio-edit order values", [item["order"] for item in entries]),
    ):
        repeated = duplicates(values)
        if repeated:
            errors.append(f"duplicate {label}: {sorted(repeated)}")

    for candidate in candidates:
        if candidate["source_id"] not in source_ids:
            errors.append(
                f"candidate {candidate['candidate_id']}: unknown source {candidate['source_id']}"
            )
        if candidate["narrative_beat"] not in beat_ids:
            errors.append(
                f"candidate {candidate['candidate_id']}: unknown beat {candidate['narrative_beat']}"
            )

    for entry in entries:
        candidate_id = entry.get("candidate_id")
        source_id = entry.get("source_id")
        if candidate_id is not None and candidate_id not in candidate_ids:
            errors.append(f"radio order {entry['order']}: unknown candidate {candidate_id}")
        if source_id is not None and source_id not in source_ids:
            errors.append(f"radio order {entry['order']}: unknown source {source_id}")

    if not sources:
        warnings.append("source manifest is empty")
    if not beats:
        warnings.append("narrative map is empty")

    for path in publishable_files(root):
        relative = path.relative_to(root)
        if path.name in SECRET_NAMES:
            errors.append(f"sensitive filename is tracked: {relative}")
        if any(part in FORBIDDEN_TRACKED_PARTS for part in relative.parts):
            errors.append(f"generated or large-media path is tracked: {relative}")
        if path.exists() and path.stat().st_size > 10 * 1024 * 1024:
            errors.append(f"tracked file exceeds 10 MiB: {relative}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors or (warnings and args.strict):
        return 1
    print(
        f"validated {root}: {len(sources)} sources, {len(beats)} beats, "
        f"{len(candidates)} candidates, {len(entries)} timeline entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
