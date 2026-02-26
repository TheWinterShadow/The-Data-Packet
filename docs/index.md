---
title: The Data Packet
description: AI-powered automated podcast generation — transform tech news into multi-speaker audio episodes with a single command.
icon: material/podcast
hide:
  - navigation
  - toc
---

# The Data Packet :material-podcast:

**AI-powered automated podcast generation** — transform tech news articles into engaging,
multi-speaker podcast episodes with a single command.

[![CI](https://img.shields.io/github/actions/workflow/status/TheWinterShadow/The-Data-Packet/ci.yml?branch=main&logo=github&label=CI)](https://github.com/TheWinterShadow/The-Data-Packet/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/github/actions/workflow/status/TheWinterShadow/The-Data-Packet/docker.yml?branch=main&logo=docker&label=Docker)](https://github.com/TheWinterShadow/The-Data-Packet/actions/workflows/docker.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/TheWinterShadow/The-Data-Packet/blob/main/LICENSE)
[![Spotify](https://img.shields.io/badge/Spotify-Listen-1DB954?logo=spotify&logoColor=white)](https://open.spotify.com/show/3LZkCwaYdOeGPo9flaYcop?si=7TJU0DEMTGC3bb1w5_2wxQ)
[![Apple Podcasts](https://img.shields.io/badge/Apple%20Podcasts-Listen-9933CC?logo=applepodcasts&logoColor=white)](https://podcasts.apple.com/us/podcast/the-data-packet/id1880395487)

---

<div class="grid cards" markdown>

-   :material-newspaper-variant-outline: **Collect articles**

    ---

    Scrapes the latest tech news from Wired and TechCrunch via RSS feeds, across security, AI,
    and science categories — automatically, on every run.

-   :simple-anthropic: **Generate scripts**

    ---

    Uses **Anthropic Claude** to write natural, engaging two-host dialogue from the collected
    articles. No templates, no fill-in-the-blanks — real AI writing.

-   :material-microphone: **Produce audio**

    ---

    Synthesizes professional multi-speaker audio with **Google Cloud TTS Long Audio Synthesis**.
    Studio voices, 44.1 kHz, no timeouts, no length caps.

-   :material-rss: **Distribute**

    ---

    Generates RSS feeds and uploads audio, script, and feed to **AWS S3** for immediate podcast
    hosting. Live on [Spotify](https://open.spotify.com/show/3LZkCwaYdOeGPo9flaYcop?si=7TJU0DEMTGC3bb1w5_2wxQ)
    and [Apple Podcasts](https://podcasts.apple.com/us/podcast/the-data-packet/id1880395487).

</div>

---

## Quick start

=== ":fontawesome-brands-docker: Docker"

    ```bash title="Pull and run"
    docker pull ghcr.io/thewintershadow/the-data-packet:latest

    docker run --rm \
      -e ANTHROPIC_API_KEY="your-claude-key" \  # (1)!
      -e GCS_BUCKET_NAME="your-gcs-bucket" \    # (2)!
      -v "$(pwd)/output:/app/output" \
      -v "$(pwd)/service-account-key.json:/credentials.json:ro" \
      ghcr.io/thewintershadow/the-data-packet:latest
    ```

    1. Get a key at [console.anthropic.com](https://console.anthropic.com/).
    2. GCS bucket for intermediate TTS audio. Provisioned by the [Terraform setup](infrastructure/terraform.md).

=== ":fontawesome-brands-python: pip"

    ```bash
    pip install the-data-packet
    the-data-packet --output ./episode
    ```

=== ":material-code-braces: Python API"

    ```python
    from the_data_packet import PodcastPipeline, get_config

    config = get_config(show_name="Tech Brief", max_articles_per_source=1)
    pipeline = PodcastPipeline(config)
    result = pipeline.run()

    if result.success:
        print(f"Audio:  {result.audio_path}")
        print(f"Script: {result.script_path}")
        print(f"Articles collected: {result.number_of_articles_collected}")
    ```

---

## Features at a glance

<div class="grid cards" markdown>

-   :fontawesome-brands-docker: **Docker-first deployment**

    ---

    Pull and run — no Python environment or system dependencies needed locally.

-   :simple-anthropic: **AI-written scripts**

    ---

    Claude writes natural two-host dialogue from real articles. Every episode is unique.

-   :material-microphone: **Professional audio**

    ---

    Google Cloud TTS Studio voices at 44.1 kHz. No length limits, no quality caps.

-   :simple-mongodb: **Smart deduplication**

    ---

    Optional MongoDB integration ensures each episode contains fresh, unseen articles.

-   :fontawesome-brands-aws: **One-step distribution**

    ---

    Audio, script, and RSS feed auto-uploaded to S3. Ready for podcast directories.

-   :material-chart-line: **Full observability**

    ---

    Structured JSONL logging with optional S3 archival and Grafana Loki forwarding.

-   :material-check-all: **Production quality**

    ---

    Full mypy type coverage, 231+ tests, CI matrix across Python 3.10–3.13.

-   :material-cpu-64-bit: **Multi-architecture**

    ---

    Docker images for `linux/amd64` and `linux/arm64` (Raspberry Pi).

</div>

---

## Where to go next

<div class="grid cards" markdown>

-   [**:material-information-outline: Overview**](overview/index.md){ .md-button }

    Learn what The Data Packet is, how it works, and the design decisions behind it.

-   [**:material-rocket-launch: Getting Started**](getting-started/index.md){ .md-button .md-button--primary }

    Run your first episode in 5 minutes with Docker or pip.

-   [**:material-tune: Configuration**](configuration/index.md){ .md-button }

    Every environment variable and CLI option, fully documented.

-   [**:material-server: Infrastructure**](infrastructure/index.md){ .md-button }

    Docker, Terraform, cloud setup, and production logging.

-   [**:material-code-tags: API Reference**](https://the-data-packet.thewintershadow.com/reference/){ .md-button }

    Sphinx-generated code documentation for every module, class, and function.

</div>
