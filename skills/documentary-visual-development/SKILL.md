---
name: documentary-visual-development
description: Plan, render, and validate source-faithful documentary B-roll, authentic document sequences, diagrams, restrained motion overlays, and final visual assemblies while preserving narration timing, archival provenance, and the approved audio conform. Use for narrated historical or technical documentary projects that need visual development, Shotcraft-inspired motion, optional OpenMontage B-roll retrieval, HTML/CSS or Remotion inserts, review previews, transition repair, or frame-accurate promotion into an FFmpeg timeline.
---

# Documentary Visual Development

Preserve the documentary edit as the authority. Treat animation and retrieval
systems as supporting tools, never as reasons to change narration, source
boundaries, historical claims, or editorial rhythm.

## Start safely

1. Read the project `AGENTS.md`, brief, status, timeline, source ledger, current
   edit notes, and render scripts.
2. Run `git status --short` and identify the preferred assembly plus the exact
   script and data that produced it.
3. Preserve source masters, narration masters, timecodes, music decisions, and
   approved renders. Produce versioned outputs.
4. Resolve existing audio defects before adding visual polish.
5. Read [visual-workflow.md](references/visual-workflow.md) before planning or
   rendering visual changes.

## Select the smallest useful tool path

- Use the project's existing FFmpeg and HTML/CSS renderer for cards, document
  reveals, simple diagrams, and restrained staged motion.
- Use Video Shotcraft as a motion-reference library when a documented shot
  concept materially improves the explanation.
- Use OpenMontage only as an isolated sidecar for candidate B-roll retrieval,
  contact sheets, source-media analysis, checkpoints, or QC experiments.
- Use Remotion for a self-contained insert only when it provides a clear
  implementation advantage. Render the insert and return to the FFmpeg
  timeline.

Read [upstream-integrations.md](references/upstream-integrations.md) before
cloning, running, adapting, or attributing either upstream project.

## Build the visual pass

1. Audit the timeline and rank visual needs by explanatory value.
2. Choose two or three treatments with one clear visual idea per shot.
3. Verify every document, label, date, relationship, portrait, and license
   against the source ledger.
4. Render each treatment as an isolated review clip with at least two seconds
   of surrounding program context.
5. Watch the rendered motion at normal speed and inspect both boundaries frame
   by frame. Check that movement settles before reading begins.
6. Obtain approval before promoting inserts into the full assembly.
7. Use `scripts/apply_visual_overlays.py` for approved full-frame inserts when
   its manifest model fits. It re-encodes picture for frame accuracy, copies the
   base audio stream, and rejects an audio packet-hash change.
8. Decode-check the complete promoted assembly and preserve the prior version.

## Enforce editorial guardrails

- Never move narration or archival in/out points to make an animation fit.
- Never conceal a broken word, slate read, retake instruction, or audio dropout
  with B-roll and call it repaired.
- Prevent isolated host-camera frames from appearing between adjacent visuals.
- Preserve a small natural beat between host narration and archival clips.
- Prefer authentic documents to recreated approximations.
- Preserve enough surrounding document text to establish authenticity.
- Use one motion concept per shot and finish on a readable hold.
- Avoid perpetual movement, choppy zooms, crash zooms, product-launch styling,
  unnecessary SFX, and mandatory beat synchronization.
- Keep music subordinate to speech and use only cleared project audio.

## Finish with evidence

Record the output path, runtime, checksum, codec and frame-rate probe, audio
packet hash, full-decode result, boundary-review evidence, upstream commits,
licenses, direct code adaptations, commands, and remaining human decisions.
