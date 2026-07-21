# Rights and Provenance

This workflow does not determine whether a use is legally permitted. The
producer remains responsible for access, licensing, fair-use analysis,
attribution, and distribution.

## Access rules

- Do not bypass DRM, authentication, paywalls, geographic controls, or other
  technical restrictions.
- Do not assume public availability means public domain or reusable.
- Do not store platform cookies, tokens, or account credentials in the project.
- Use an authorized alternate source when the preferred source is unavailable.

## Required source record

For every source preserve:

- Original URL.
- Title, publisher, speakers, and relevant dates.
- Runtime, description, and available captions.
- Visible license information.
- Download date and exact acquisition command.
- Source quality and provenance assessment.
- SHA-256 and FFprobe report for acquired masters.
- Proposed editorial purpose.
- Rights or attribution uncertainty.

## Repository boundary

Git should contain research metadata, schemas, scripts, and editorial decisions.
It should not normally contain:

- Downloaded third-party media.
- Narration masters containing private production material.
- Whisper models.
- Rendered review or delivery videos.
- Platform cookies or credentials.
- Material supplied under confidential terms.

Store large media in backed-up project storage and use checksums to connect it
to the tracked manifest.

## Attribution

On-screen and show-notes attribution should identify the actual uploader or
archive, the original speaker or author, the date, and whether an item is an
original document, later interview, archival mirror, or third-party account.
