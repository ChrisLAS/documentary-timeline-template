# Optional Visual Production Integrations

The template can use two pinned upstream projects without giving either one
control of the documentary edit:

- **Video Shotcraft** supplies motion recipes and implementation references.
- **OpenMontage** can be evaluated as an isolated B-roll retrieval, storyboard,
  checkpoint, and QC sidecar.

The built-in `documentary-visual-development` Codex skill carries the workflow
proven on source-faithful, narration-led historical pieces: render focused
previews, protect the audio conform, verify boundaries, then promote approved
inserts into a versioned assembly.

## Adoption decision

| Integration | Decision | Production role |
|---|---|---|
| Documentary visual-development skill | Adopted | Authoritative visual-pass procedure inside this template |
| Video Shotcraft | Adopted selectively | Pinned motion vocabulary and implementation reference; no bundled audio or promo defaults |
| OpenMontage | Pilot as a sidecar | Candidate B-roll corpus, semantic retrieval, contact sheets, checkpoints, and supplemental QC |
| OpenMontage documentary pipeline | Not adopted as authority | Its pinned beta pipeline targets short, music-led, mostly non-narrated montage |

Pinned revisions:

- Video Shotcraft: `d4915443232e89527fdc9d7e79f132ba411fc440`
- OpenMontage: `c36e41223e819441748817105635ac4036d41b10`

The OpenMontage sidecar should graduate beyond pilot status only after a real
project demonstrates useful retrieval precision, complete provenance, reduced
review time, acceptable dependency cost, and clean Nix-host operation.

## Fresh Nix host

```bash
git clone https://github.com/ChrisLAS/documentary-timeline-template.git my-documentary
cd my-documentary
nix develop .#visual
make integration-setup
make integration-check
make install-codex-skill
```

The `visual` shell adds Chromium, Node.js, ImageMagick, and `uv` to the normal
FFmpeg, Whisper, yt-dlp, Python, and validation environment.

`integration-setup` creates ignored checkouts under `.integrations/` at the
exact commits in `integrations/integrations.lock.json`. It does not install
upstream Python or Node dependencies, run paid providers, copy code, or request
credentials.

The skill installer creates a link under `${CODEX_HOME:-$HOME/.codex}/skills`.
Use `scripts/install_codex_skill.sh --copy` when the repository will not remain
at a stable path.

Restart Codex after installing the skill so it is discovered in a new session.

## Integration roles

| Capability | Default implementation | Optional upstream role |
|---|---|---|
| Research and fact checking | Documentary template | None |
| Narration and archival boundaries | Documentary template | None |
| Cards, documents, diagrams | HTML/CSS/SVG plus FFmpeg | Shotcraft motion reference |
| Complex isolated animation | Project-selected renderer | Shotcraft recipe or Remotion reference |
| B-roll candidate retrieval | Human archival search | OpenMontage corpus experiment |
| Storyboard and checkpoints | Project reviews/status | OpenMontage concepts or sidecar |
| Full timeline and audio | FFmpeg project renderer | None |
| Delivery verification | FFmpeg/FFprobe/checksums | Supplemental QC only |

## Promoting visual inserts

Render each treatment independently and review it with surrounding program
context. After approval, create a project manifest from
`config/visual-overlays.example.yaml`:

```bash
python scripts/apply_visual_overlays.py timeline/visual-overlays.yaml --dry-run
python scripts/apply_visual_overlays.py timeline/visual-overlays.yaml
```

The promoter re-encodes video for frame-accurate placement, copies the approved
base audio stream, full-decodes the output, compares audio packet hashes, and
writes a reproducibility manifest.

## OpenMontage experiment setup

OpenMontage is intentionally not installed by default. Its complete platform is
large and its documentary-montage pipeline is beta and optimized for short,
music-driven, mostly non-narrated work.

Inside `nix develop .#visual`, an isolated experiment can be prepared with:

```bash
cd .integrations/OpenMontage
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
uv pip install --python .venv/bin/python opencv-python torch transformers
npm --prefix remotion-composer install
```

Start with candidate retrieval and contact sheets rather than a complete edit.
Evaluate provenance completeness, retrieval precision, duplication control,
human review time, and dependency cost before adopting more of the platform.

## Licensing boundary

The template contains no copied OpenMontage or Video Shotcraft source code or
bundled media.

- Video Shotcraft is pinned as an Apache-2.0 motion reference. Direct code reuse
  requires provenance and any applicable notices; bundled assets may have
  separate terms.
- OpenMontage is pinned as an AGPL-3.0-only isolated sidecar. Do not copy its
  code into this MIT repository without a deliberate licensing review.

Public availability of footage or assets does not establish permission to use
them. Continue recording original URLs, publishers, visible licenses, download
commands, checksums, and rights uncertainty in the source ledger.
