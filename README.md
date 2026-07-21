# Documentary Timeline Template

[![Validate template](https://github.com/ChrisLAS/documentary-timeline-template/actions/workflows/validate.yml/badge.svg)](https://github.com/ChrisLAS/documentary-timeline-template/actions/workflows/validate.yml)

A reproducible, human-edited workflow for building archival documentary and
podcast segments from interviews, primary documents, narration, and historical
footage.

This is not a keyword-clipping system. It organizes the work around explicit
narrative beats, complete editorial thoughts, source provenance, human boundary
review, historical fact-checking, and export-level quality control.

## What it provides

- Source manifests with provenance, rights notes, captions, and checksums.
- A historical chronology and claim-driven narrative map.
- Candidate passages with context, scoring, weaknesses, and rejection reasons.
- Human-reviewed start and end decisions with focused review renders.
- Narration take selection, radio edits, transition spacing, and sparse music cues.
- Evidence-led B-roll guidance and a configurable 1080p rough-cut assembler.
- Full decode checks, delivery specifications, and SHA-256 output records.
- Schemas, cross-reference validation, unit tests, media smoke tests, and CI.

The editorial method is documented in [the complete workflow](docs/WORKFLOW.md)
and [editorial standard](docs/EDITORIAL_STANDARD.md).

## Quick start on a Nix host

The repository includes a pinned `flake.lock`. A fresh Nix machine does not need
Python, FFmpeg, yt-dlp, Whisper, or the validation libraries installed globally.

### 1. Create a project from the template

Use GitHub's **Use this template** button, or clone it directly:

```bash
git clone https://github.com/ChrisLAS/documentary-timeline-template.git my-documentary
cd my-documentary
```

If Git is not already installed on the Nix host:

```bash
nix shell nixpkgs#git --command \
  git clone https://github.com/ChrisLAS/documentary-timeline-template.git my-documentary
cd my-documentary
```

### 2. Enter the reproducible environment

```bash
nix develop
```

The first run downloads the pinned package closure. Later runs reuse the Nix
store. The shell includes:

- FFmpeg and FFprobe
- yt-dlp
- whisper.cpp
- Python with PyYAML, jsonschema, and PySceneDetect
- jq, Git, ShellCheck, and actionlint

If flakes are not enabled in the host's Nix configuration, either enable
`nix-command` and `flakes` declaratively or use the one-command fallback:

```bash
nix --extra-experimental-features 'nix-command flakes' develop
```

On NixOS, the durable configuration is:

```nix
nix.settings.experimental-features = [ "nix-command" "flakes" ];
```

### 3. Verify the checkout

Inside the development shell:

```bash
nix flake check
make validate
make test
make shellcheck
make actionlint
make media-smoke
```

The media smoke test generates temporary synthetic footage and exercises take
selection, radio-edit assembly, music cues, picture assembly, delivery remuxing,
checksums, and full decode verification. It does not download third-party media.

### 4. Configure the clone for a topic

```bash
python scripts/configure_project.py \
  --title "My Documentary" \
  --slug my-documentary \
  --thesis "The central historical argument."
python scripts/validate_project.py .
```

Then complete `PROJECT_BRIEF.md`, add research leads to `sources.yaml`, and work
through Checkpoints A–E in [docs/WORKFLOW.md](docs/WORKFLOW.md).

### 5. Download a local Whisper model when transcription is needed

Models are intentionally not stored in Git. From the development shell:

```bash
mkdir -p models
whisper-cpp-download-ggml-model large-v3-turbo-q5_0 models
```

That creates the default model path expected by `scripts/transcribe_audio.sh`:

```text
models/ggml-large-v3-turbo-q5_0.bin
```

## Core commands

```bash
# Preserve platform metadata, captions, description, and thumbnail first.
scripts/acquire_source_metadata.sh SOURCE_ID URL

# Acquire a master only after source approval and rights review.
scripts/acquire_archival_master.sh SOURCE_ID URL
scripts/probe_media.sh PATH_TO_MASTER SOURCE_ID

# Create and transcribe analysis audio.
scripts/create_analysis_audio.sh PATH_TO_MASTER OUTPUT_WAV
scripts/transcribe_audio.sh INPUT_AUDIO OUTPUT_PREFIX

# Inspect and render editorial boundaries.
python scripts/analyze_boundary.py MEDIA CENTER_SECONDS OUTPUT_DIRECTORY
scripts/render_review_clip.sh INPUT START END OUTPUT CANDIDATE_ID

# Render selected takes and build the program.
python scripts/render_selected_takes.py config/selected-takes.yaml
python scripts/build_audio_timeline.py \
  timeline/radio-edit.yaml renders/assemblies/radio-edit.wav
python scripts/render_music_pass.py timeline/music-cues.yaml
python scripts/build_video_assembly.py timeline/video-assembly.yaml

# Package a stream-preserving MP4 delivery and verify it completely.
scripts/finalize_delivery.sh INPUT_MP4 OUTPUT_MP4
```

## Project layout

```text
config/       Project identity, render policy, vocabulary, and take selections
narrative/    Thesis, chronology, narrative beats, and fact-check notes
sources/      Per-source metadata, transcripts, notes, and ignored media folders
candidates/   Candidate passages, scores, and rejection reasoning
reviews/      Source, boundary, duplication, editorial, and historical reviews
timeline/     Radio edit, host script, music cues, edit lists, and video assembly
renders/      Ignored review clips, assemblies, and delivery media
scripts/      Reusable acquisition, analysis, conform, assembly, and QC tools
schemas/      JSON schemas used by the project validator
tests/        Unit tests and a synthetic end-to-end media fixture
```

Large media, Whisper models, renders, logs, cookies, and credentials are excluded
from Git. Read [Rights and Provenance](docs/RIGHTS_AND_PROVENANCE.md) before
acquiring or publishing source material.

## Editorial and legal boundary

Every acquisition and use of third-party material remains the producer's legal
responsibility. Public availability is not a license grant. The template helps
record provenance and uncertainty; it does not determine whether a particular
use is licensed, fair use, public domain, or otherwise permitted.

## License

The original code and documentation in this repository are available under the
[MIT License](LICENSE). That license does not grant rights to third-party media,
transcripts, quotations, trademarks, or research materials used in a project.
