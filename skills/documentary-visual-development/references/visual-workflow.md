# Visual Development Workflow

## Contents

1. Visual audit
2. Treatment selection
3. Documents and diagrams
4. Motion and layout
5. Review renders
6. Audio and transition protection
7. Full-assembly promotion
8. Delivery evidence

## 1. Visual audit

Begin after the narrative map, narration, archival selections, and source
ledger are stable enough to judge the complete story. Create an audit table:

| Field | Meaning |
|---|---|
| program range | Exact start and end in the preferred assembly |
| narration job | Claim or transition carried by the host |
| current picture | Host, archival clip, document, card, or placeholder |
| visual problem | What the audience cannot currently see or understand |
| proposed treatment | One concise visual idea |
| evidence | Source-ledger claim IDs and authentic assets |
| audio risk | Pickup, splice, pause, breath, or clip boundary nearby |
| priority | Essential, useful, or decorative |

Prioritize visuals that clarify a system relationship, reveal primary evidence,
cover a verified narration splice, or replace repetitive talking-head footage.
Reject movement that exists only to keep the frame busy.

## 2. Treatment selection

Choose the lightest implementation that can express the idea:

| Need | Preferred path |
|---|---|
| Static quotation, date, attribution | Existing card renderer |
| Authentic document focus | HTML/CSS masks, highlights, or staged crops |
| Simple process or state diagram | HTML/CSS/SVG rendered to a silent insert |
| Complex 2.5D or typography motion | Isolated Remotion insert |
| Candidate stock/archive B-roll | Manual search or optional OpenMontage sidecar |
| Timeline integration | FFmpeg plus `apply_visual_overlays.py` |

Do not replatform an established edit because one shot benefits from a different
renderer.

## 3. Documents and diagrams

For authentic documents:

- Show enough of the real page to establish provenance.
- Highlight only text supported by the narration.
- Keep surrounding text visible so the excerpt does not look fabricated.
- Add a short publisher/date/source label.
- Hold the important line long enough to read at normal playback speed.
- Do not fake-type an entire archival document.

For conceptual diagrams:

- Label them `conceptual overview` when implementation details are omitted.
- Distinguish optional inputs from inputs always present.
- Do not depict untrusted hardware as an unquestioned oracle.
- Show state changes in discrete, readable stages.
- Land on a stable final state.

For vertical documents in 16:9, prefer a sharp central page with a restrained
background field, cropped duplicate, or low-contrast blur. Preserve page edges
when they help establish authenticity. Avoid mirrored edges when they create
false text or distracting symmetry.

## 4. Motion and layout

- Use eased motion with an explicit settle and reading hold.
- Test pans and zooms at the final frame rate; do not judge from keyframes alone.
- Keep movement large enough to be visibly smooth but small enough to preserve
  document legibility.
- Avoid ultra-slow fractional scaling that produces visible stepping.
- Use fixed seeds for procedural motion.
- Keep one visual subject and one motion grammar per shot.
- Maintain safe margins for platform playback and lower thirds.
- Place overlays so they do not awkwardly bisect the host's face or gesture.

## 5. Review renders

For every proposed treatment:

1. Include at least two seconds before and after the treatment when program
   material exists.
2. Preserve the approved audio from the current assembly.
3. Render at delivery resolution and frame rate.
4. Watch at normal speed with ordinary speakers and headphones.
5. Extract frame strips around the in and out points.
6. Check labels at 1080p, not only on a development monitor.
7. Probe resolution, frame rate, codecs, audio presence, and duration.
8. Full-decode the review file.

Do not promote rejected or unreviewed treatments merely because they render.

## 6. Audio and transition protection

- Listen at least 15 seconds around narration and archival boundaries.
- Preserve complete final words, breaths, and meaningful pauses.
- Do not expose section names, take numbers, or setup language.
- Preserve the project's approved host-to-clip transition beat.
- Extend a visual's first or final stable frame across an existing picture gap
  rather than moving audio.
- Compare encoded audio packet hashes when the base audio should be unchanged.
- If packet hashes differ unexpectedly, reject the assembly and investigate.

## 7. Full-assembly promotion

Create a YAML file based on `config/visual-overlays.example.yaml`. Each insert
must be a complete, approved full-frame render with exact program timing.

```bash
python scripts/apply_visual_overlays.py timeline/visual-overlays.yaml --dry-run
python scripts/apply_visual_overlays.py timeline/visual-overlays.yaml
```

The promoter intentionally re-encodes picture for frame-accurate placement and
stream-copies the base assembly audio. It refuses overlapping inserts, missing
media, insert durations beyond the source, existing outputs, and changed audio
packet hashes.

If a project needs transparency, partial-frame overlays, overlapping layers, or
shot-specific color management, extend the project renderer rather than
forcing those cases into the generic promoter.

## 8. Delivery evidence

Record:

- Preferred output and rollback paths.
- Runtime, resolution, constant/variable frame rate, codecs, and frame count.
- Full-file SHA-256.
- Base and output audio packet hashes.
- Complete FFmpeg decode result.
- Boundary contact-sheet or frame-strip paths.
- Normal-speed human review decision.
- Every upstream repository, exact commit, license, adapted file, and required
  attribution.
- Any unresolved rights, rendering, or editorial decision.
