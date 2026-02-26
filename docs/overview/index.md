---
title: Overview
description: What The Data Packet is, what problem it solves, and the technology powering it.
icon: material/information-outline
---

# Overview

The Data Packet is a production-ready, AI-powered podcast generator. It scrapes tech news,
writes a two-host dialogue script using Claude, synthesizes professional audio with Google
Cloud TTS, and uploads the finished episode to S3 — all from a single command.

**Version:** `2.0.0` &nbsp;|&nbsp; **License:** MIT &nbsp;|&nbsp; **Author:** TheWinterShadow

---

## What problem does it solve?

Creating a regular tech podcast manually involves:

- [ ] Monitoring multiple news sources for relevant articles
- [ ] Writing a coherent, natural-sounding script for two hosts
- [ ] Recording, editing, and mixing audio
- [ ] Generating an RSS feed and uploading everything for distribution

The Data Packet automates every step. It produces a complete, ready-to-publish episode —
script, audio file, and RSS feed — without manual intervention.

---

## The full pipeline

``` mermaid
flowchart LR
    A["Article Sources\nWired · TechCrunch"] -->|RSS fetch + parse| B
    B["MongoDB Check\nDeduplication"] -->|fresh articles| C
    C["Script Generator\nAnthropic Claude"] -->|dialogue script| D
    D["Audio Generator\nGoogle Cloud TTS"] -->|synthesized audio| E
    E["RSS Generator"] -->|episode files| F
    F["S3 Upload\nAWS S3"]
```

---

## Technology stack

<div class="grid cards" markdown>

-   :simple-anthropic: **Script generation**

    ---

    **Anthropic Claude** writes the dialogue. Articles are fed as context; Claude produces a
    natural two-host conversation covering each story.

-   :material-microphone: **Audio synthesis**

    ---

    **Google Cloud TTS Long Audio Synthesis** generates the final `.wav`. Studio voices at
    44.1 kHz — no per-segment timeouts, no quality limits.

-   :material-cloud-outline: **Intermediate storage**

    ---

    **Google Cloud Storage (GCS)** holds synthesized audio during processing. A 30-day
    lifecycle policy keeps costs low automatically.

-   :fontawesome-brands-aws: **Podcast hosting**

    ---

    **AWS S3** stores the finished episode files with public read access, making them
    immediately distributable via any podcast app.

-   :simple-mongodb: **Episode tracking**

    ---

    **MongoDB** (optional) tracks which articles have been used, preventing repetition
    across episodes.

-   :material-chart-line: **Observability**

    ---

    **JSONL structured logging** with optional S3 archival and **Grafana Loki** forwarding
    for centralised log aggregation.

</div>

---

## What you get

After running the pipeline, your `output/` directory contains:

```
output/
├── episode_script.txt    # Full two-host dialogue (Alex + Sam)
├── episode.wav           # Professional stereo audio, 44.1 kHz
└── feed.xml              # RSS 2.0 podcast feed (if S3 is configured)
```

If S3 is configured, all three files are uploaded and the public URLs are printed to the
console — ready to add to Apple Podcasts, Spotify, or any podcast directory.

---

## Key design decisions

??? info "Docker-first"

    The primary deployment target is Docker. A pre-built multi-platform image (`amd64` + `arm64`)
    is published to GitHub Container Registry on every release. You don't need Python or any
    system dependencies installed locally.

??? info "Modular architecture"

    Each pipeline stage is an independent, swappable module. Sources, generators, and utilities
    follow consistent interfaces, making it straightforward to add new article sources or
    swap the audio backend.

??? info "Environment-variable configuration"

    All secrets and tunables are configured via environment variables. Nothing is hardcoded.
    A `.env` file or Docker `-e` flags are the primary configuration mechanism.

??? info "Retry-first reliability"

    Every external API call (Claude, Google Cloud TTS, S3) uses exponential backoff via
    `tenacity`. Transient failures are handled transparently without crashing the pipeline.

??? info "No ElevenLabs dependency (v2.0 migration)"

    Version 2.0 migrated entirely to Google Cloud TTS Long Audio Synthesis. This removes
    per-character pricing caps, eliminates timeout issues on long scripts, and provides
    Studio-quality voices at 44.1 kHz.

---

## Next steps

<div class="grid cards" markdown>

-   [Architecture](architecture.md){ .md-button }

    Detailed component map and data flow.

-   [Getting Started](../getting-started/index.md){ .md-button .md-button--primary }

    Run your first episode in 5 minutes.

-   [Configuration](../configuration/index.md){ .md-button }

    All environment variables and options.

</div>
