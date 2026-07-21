# B-Roll and Assembly

Use B-roll to carry evidence and clarify mechanisms, not merely to hide edits.

## Presentation modes

1. **Archival video:** Preserve source aspect ratio and texture.
2. **Document canvas:** Place portrait documents on a 16:9 evidence canvas with
   a readable crop, source title, date, and attribution. Blurred or mirrored
   edges may fill unused space, but the document itself must remain undistorted.
3. **Quotation card:** Show only the amount of text the audience can read during
   the available narration. Keep the original document visible as context.
4. **Mechanism diagram:** Use restrained arrows, labels, and animation to explain
   relationships that prose cannot show efficiently.
5. **Correspondence exhibit:** Identify sender, recipient, exact date, and archive.

## Motion

- Alternate restrained pushes with static holds.
- Avoid continuous imperceptibly slow zooms that render unevenly.
- Cap scale changes unless the shot has a clear editorial reason to travel.
- Verify motion in the exported program, not only in a browser preview.

## Narration composites

- Hide exposed visual joins with evidence-led B-roll.
- Do not use B-roll as permission to cut speech carelessly.
- Preserve whole words and natural releases before inserting room tone.
- When combining takes, render and review the exact join in a focused excerpt.
- If an edit remains audible, prefer a clean alternate sentence or pickup over
  increasingly complicated micro-splices.

## Assembly

Prepare one picture asset per timeline entry, then list it in
`timeline/video-assembly.yaml`. Build the rough cut with:

```bash
python scripts/build_video_assembly.py timeline/video-assembly.yaml
```

The script normalizes picture geometry to the configured canvas, creates
uniform intermediate segments, muxes the locked audio program, and decode-checks
the result. It does not replace a final color, graphics, or audio finish.
