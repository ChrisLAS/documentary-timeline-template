# Upstream Integration Policy

## Contents

1. Authority boundary
2. Video Shotcraft
3. OpenMontage
4. Licensing and provenance
5. Fresh-system commands

## 1. Authority boundary

The documentary repository remains authoritative for research, claims, source
provenance, transcript corrections, clip boundaries, narration, audio, music,
timeline data, and final delivery. Optional integrations may propose or render
assets; they may not silently rewrite those decisions.

Pinned revisions live in `integrations/integrations.lock.json`. Local checkouts
belong under ignored `.integrations/` and must pass
`scripts/check_optional_integrations.py`.

## 2. Video Shotcraft

Default mode: `motion-reference`.

Useful for:

- Document focus and reveal vocabulary.
- Historical timeline motion.
- Connected-system diagrams.
- Typography and camera-motion implementation references.
- The rule that motion should settle into a readable hold.

Do not inherit by default:

- Product-promo framing.
- Fast 2.5D travel, crash zooms, or speed ramps.
- Mandatory beat synchronization.
- Bundled music or sound effects.
- Fictional replacements for authentic documents.

Prefer an original implementation in the project's existing HTML/CSS/FFmpeg
system. If direct source code is adapted, record the source file and commit,
retain Apache-2.0 notices as required, and separately inspect asset and Remotion
licenses.

## 3. OpenMontage

Default mode: `isolated-sidecar`.

Promising uses:

- Building a local candidate corpus from approved stock and archive providers.
- CLIP-assisted candidate ranking and visual diversification.
- Reference-video and source-media analysis.
- Contact-sheet and storyboard approval surfaces.
- Checkpoints, decision logs, and automated QC experiments.

Do not make its `documentary-montage` pipeline authoritative for a narrated
historical segment. At the pinned revision that pipeline is beta, optimized for
short non-narrated music-led montages, and mandates creative conventions that
may conflict with the documentary edit.

Review every retrieved asset manually. Semantic similarity is not editorial
relevance, factual accuracy, provenance, or license clearance.

Keep OpenMontage code and dependencies in its own checkout and environment. Do
not copy AGPL-covered code into this MIT repository without a deliberate license
decision.

## 4. Licensing and provenance

The integration lock records:

- Video Shotcraft: Apache-2.0 at the pinned commit.
- OpenMontage: AGPL-3.0-only at the pinned commit.

Upstream repositories may contain assets, generated media, fonts, provider
SDKs, or dependencies under other terms. Inspect those terms before use. Never
assume an upstream repository license clears third-party footage, music, images,
or model output.

If no upstream code or asset is copied, record the project and commit as a
method or motion reference. If code or assets are copied, record exact files,
licenses, notices, and transformations in project provenance notes.

## 5. Fresh-system commands

From the template repository:

```bash
nix develop .#visual
make integration-setup
make integration-check
make install-codex-skill
```

`integration-setup` clones exact pinned commits but does not install provider
SDKs, request credentials, or run upstream setup scripts.

To experiment with OpenMontage in isolation:

```bash
cd .integrations/OpenMontage
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
uv pip install --python .venv/bin/python opencv-python torch transformers
npm --prefix remotion-composer install
```

Only add provider credentials to the ignored OpenMontage environment when a
specific approved experiment requires them. Never copy credentials into the
documentary repository.
