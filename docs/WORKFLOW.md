# Documentary Timeline Workflow

The workflow is chronological, but it is not mechanical. Each phase preserves
the reasoning needed for a human editor to understand and revise the result.

## Phase 0: Project definition

Complete `PROJECT_BRIEF.md` and `config/project.yaml`.

Define:

- The central thesis.
- The historical period and required subjects.
- The audience's assumed knowledge.
- The target runtime and delivery context.
- Claims requiring special caution.
- What the project explicitly will not cover.

## Phase 1: Source discovery

Record every serious source lead in `sources.yaml`, including rejected sources.
Rank first-person and period material above modern summaries when they perform
the same narrative job.

### Checkpoint A: source shortlist

Report:

- Best available source for each chapter.
- Source quality and provenance.
- Missing subjects.
- Access failures and legal alternatives.
- Proposed substitutions.

Do not download a large volume of full-resolution media before this checkpoint.

## Phase 2: Acquisition and preservation

For approved sources:

1. Acquire metadata, descriptions, thumbnails, and captions first.
2. Download only material the producer may lawfully access.
3. Preserve the original codec and container when practical.
4. Save the exact command used.
5. Generate a SHA-256 checksum and FFprobe report.
6. Create separate analysis proxies when needed.

Never overwrite the archival master.

## Phase 3: Transcript corpus

- Preserve platform captions as one input, not as unquestioned truth.
- Generate a local transcript from source audio.
- Preserve word timestamps when supported.
- Correct names and terms without silently changing meaning.
- Mark uncertainty, nonverbal events, and speaker changes.
- Compare captions with local transcription.

## Phase 4: Narrative map

Complete `narrative/narrative-beats.yaml` before selecting final clips. Every
beat must define the audience question, claim, necessary context, preferred
speaker, ideal duration, host bridge, visual opportunities, and caveats.

### Checkpoint B: narrative map

Report chapter order, core claims, expected runtime, host-led sections, and
historical assertions requiring caution.

## Phase 5: Candidate discovery

Search the full transcript corpus semantically. For each beat, retain up to five
candidates with generous surrounding context. Reject mentions that do not
explain or complete the assigned narrative job.

### Checkpoint C: candidate clips

Present the top candidates, transcript excerpts, rough timestamps, strengths,
weaknesses, and a recommendation.

## Phase 6: Boundary analysis

For every promoted candidate, inspect at least 60 seconds before and 90 seconds
after when available. Record context, clean, preferred, factual, rhetorical,
and extended boundaries. Explain every preferred in and out.

Then inspect waveform and picture. Listen to at least 15 seconds on both sides
of every proposed boundary. Do not trust transcript timestamps alone.

### Checkpoint D: boundary review

Present preferred and alternate boundaries, reasons, and focused review files.

## Phase 7: Independent editorial review

Assign exactly one verdict to every proposed clip:

- `KEEP`
- `TRIM`
- `EXTEND`
- `REPLACE`
- `DROP`

Non-KEEP verdicts require exact timestamps or replacement candidate IDs.

## Phase 8: Duplication and accuracy

Compare selected clips for repeated ideas. Keep repetition only when it creates
meaningful contrast. Fact-check every host bridge and distinguish primary
evidence, correspondence, interpretation, inference, and speculation.

## Phase 9: Radio edit and narration

Build an audio-first sequence alternating narration, primary clips, document
readings, transitions, and intentional silence. Record narration as continuous
takes if convenient, but preserve take numbers and source timecodes. Render
focused previews for every composite repair.

## Phase 10: Picture, music, and assembly

Use evidence-led B-roll: original documents, correspondence, diagrams, period
footage, and restrained motion. Use music as punctuation, not a continuous bed
under dense explanation unless the project calls for it.

### Checkpoint E: rough assembly

Report runtime, timeline, missing narration, repetition, weak transitions, and
remaining judgment calls.

## Phase 10.5: Visual development

After the audio conform and archival boundaries are stable, audit the timeline
for primary-document sequences, explanatory diagrams, restrained motion, and
B-roll. Render focused previews with surrounding context before replacing any
part of the full assembly.

Use `skills/documentary-visual-development/SKILL.md` and
`docs/VISUAL_INTEGRATIONS.md`. Keep optional Shotcraft and OpenMontage work
isolated from the authoritative timeline. Promote only approved full-frame
inserts with `scripts/apply_visual_overlays.py`, then full-decode the assembly
and verify that its audio packet hash matches the approved base.

## Phase 11: Delivery

- Freeze editorial timing before finishing.
- Recheck the entire program after every timing-changing repair.
- Verify focused problem windows from the exported program.
- Decode-check the complete delivery file.
- Record technical specifications and SHA-256.
- Preserve the prior approved version when creating a revision.
