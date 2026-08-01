# AGENTS.md

This repository is a reusable workflow for source-faithful documentary timeline
projects. Preserve editorial reasoning and original media at every step.

## Operating priorities

1. Never overwrite an archival master.
2. Record provenance, rights uncertainty, commands, and checksums.
3. Complete the narrative map before final clip extraction.
4. Select complete editorial thoughts, not keyword hits.
5. Verify edit boundaries by listening and inspecting picture and waveform.
6. Separate documented influence, technical similarity, and interpretation.
7. Preserve review variants when a boundary remains uncertain.

## Before changing files

- Read `PROJECT_BRIEF.md`, `PROJECT_STATUS.md`, and `config/project.yaml`.
- Inspect `git status --short` and preserve unrelated changes.
- Read the relevant narrative beat and source notes before editing candidates.
- Prefer the checked-in schemas and established YAML fields.

## Media rules

- Source media belongs under `sources/SOURCE_ID/media/` and is ignored by Git.
- Never transcode or modify archival masters in place.
- Store exact acquisition commands and SHA-256 checksums.
- Use frame-accurate re-encoding for editorial cuts when stream-copy boundaries
  would shift to keyframes.
- Render focused review excerpts before replacing a full assembly.
- Decode-check final deliverables with FFmpeg.

## Optional visual integrations

- Use the bundled `documentary-visual-development` skill for B-roll, document
  animation, diagrams, motion overlays, and visual-pass promotion.
- Keep Video Shotcraft and OpenMontage checkouts under ignored `.integrations/`
  at the commits in `integrations/integrations.lock.json`.
- Treat Shotcraft as a motion reference and OpenMontage as an isolated retrieval
  or QC sidecar. Neither may silently replace the project's research, timeline,
  narration, source boundaries, or audio conform.
- Do not copy upstream code or assets without recording exact provenance,
  licenses, notices, and any separate asset terms.
- Render focused visual previews before promoting a versioned full assembly.

## Validation

Run the narrowest relevant checks, then the project validator:

```bash
nix develop --command python scripts/validate_project.py .
```

Do not commit downloaded media, models, generated renders, authentication data,
or platform cookies.
