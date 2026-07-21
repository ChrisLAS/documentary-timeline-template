# Source Storage

Create one directory per source:

```text
sources/source-id/
├── metadata.json
├── source-url.txt
├── acquisition-command.txt
├── checksum.sha256
├── ffprobe.json
├── captions-original.vtt
├── transcript-local.json
├── transcript.json
├── transcript.md
├── speakers.json
├── source-notes.md
├── frames/
└── media/
    ├── master.ext
    └── proxy.mp4
```

`media/`, `frames/`, and analysis artifacts are ignored by Git. Metadata,
transcripts, corrections, notes, and checksums may be tracked after rights and
privacy review.
