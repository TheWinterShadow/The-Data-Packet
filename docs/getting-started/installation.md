---
title: Installation
description: All installation methods — Docker (recommended), pip, and building from source.
icon: material/download
---

# Installation

The Data Packet can be installed and run in three ways.

---

## Option 1: Docker (recommended)

Docker requires no Python environment and is the recommended approach for all production use.

### Pull from GitHub Container Registry

```bash
# Latest stable
docker pull ghcr.io/thewintershadow/the-data-packet:latest

# Specific version
docker pull ghcr.io/thewintershadow/the-data-packet:v2.0.0

# Latest main branch build
docker pull ghcr.io/thewintershadow/the-data-packet:main
```

### Build from source

```bash
git clone https://github.com/TheWinterShadow/The-Data-Packet.git
cd The-Data-Packet
docker build -t the-data-packet:local .
```

### Multi-platform (amd64 + arm64)

Pre-built images support both `linux/amd64` and `linux/arm64` (Raspberry Pi).

```bash
# One-time builder setup
docker buildx create --name multiplatform --bootstrap --use

# Build for ARM64
docker buildx build \
  --platform linux/arm64 \
  -t the-data-packet:arm64 \
  --load .
```

!!! tip "Raspberry Pi"

    On ARM64 devices, pull explicitly with `--platform`:
    ```bash
    docker pull --platform linux/arm64 \
      ghcr.io/thewintershadow/the-data-packet:latest
    ```

---

## Option 2: pip

```bash
pip install the-data-packet
```

!!! note "Virtual environment"

    Always install in a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install the-data-packet
    ```

Then use the CLI:

```bash
the-data-packet --output ./episode
```

Or the Python API:

```python
from the_data_packet import PodcastPipeline, get_config

config = get_config(show_name="My Podcast")
pipeline = PodcastPipeline(config)
result = pipeline.run()
```

---

## Option 3: From source

```bash
git clone https://github.com/TheWinterShadow/The-Data-Packet.git
cd The-Data-Packet
pip install hatch          # build tool
hatch run the-data-packet --output ./episode
```

See [Development Setup](../contributing/development.md) for the full local dev workflow.

---

## System dependencies

=== ":fontawesome-brands-docker: Docker"

    Everything is included. `ffmpeg`, Python, and all libraries are bundled in the image.

=== ":fontawesome-brands-python: pip / source"

    `ffmpeg` must be installed as a system package.

    === ":simple-ubuntu: Ubuntu / Debian"

        ```bash
        sudo apt-get install ffmpeg
        ```

    === ":simple-apple: macOS"

        ```bash
        brew install ffmpeg
        ```

    === ":simple-windows: Windows"

        Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to `PATH`.

---

## Python package dependencies

| Package | Min version | Purpose |
|---|---|---|
| `anthropic` | 0.25.0 | Claude script generation |
| `google-cloud-texttospeech` | 2.16.0 | Long Audio Synthesis |
| `google-cloud-storage` | 2.10.0 | GCS bucket access |
| `feedparser` | 6.0.0 | RSS article collection |
| `beautifulsoup4` | 4.9.0 | HTML parsing |
| `requests` | 2.25.0 | HTTP client |
| `tenacity` | 8.0.0 | Retry logic |
| `boto3` | 1.20.0 | AWS S3 integration |
| `pymongo` | latest | MongoDB episode tracking |
| `pydub` | latest | Audio processing |

All are installed automatically via `pip install the-data-packet`.
