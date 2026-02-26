# The Data Packet

**AI-powered automated podcast generation** — scrapes tech news, writes two-host dialogue with Claude, synthesizes audio with Google Cloud TTS, and publishes to AWS S3.

[![CI Tests](https://img.shields.io/github/actions/workflow/status/TheWinterShadow/The-Data-Packet/ci.yml?branch=main&logo=github&label=CI%20Tests)](https://github.com/TheWinterShadow/The-Data-Packet/actions/workflows/ci.yml)
[![Docker Build](https://img.shields.io/github/actions/workflow/status/TheWinterShadow/The-Data-Packet/docker.yml?branch=main&logo=docker&label=Docker%20Build)](https://github.com/TheWinterShadow/The-Data-Packet/actions/workflows/docker.yml)
[![Documentation](https://img.shields.io/github/actions/workflow/status/TheWinterShadow/The-Data-Packet/docs.yml?branch=main&logo=readthedocs&label=Docs)](https://github.com/TheWinterShadow/The-Data-Packet/actions/workflows/docs.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?logo=python)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Spotify](https://img.shields.io/badge/Spotify-Listen-1DB954?logo=spotify&logoColor=white)](https://open.spotify.com/show/3LZkCwaYdOeGPo9flaYcop?si=7TJU0DEMTGC3bb1w5_2wxQ)
[![Apple Podcasts](https://img.shields.io/badge/Apple%20Podcasts-Listen-9933CC?logo=applepodcasts&logoColor=white)](https://podcasts.apple.com/us/podcast/the-data-packet/id1880395487)

**Full documentation:** [the-data-packet.thewintershadow.com](https://the-data-packet.thewintershadow.com)

---

## What it does

1. Scrapes the latest tech news from Wired and TechCrunch
2. Generates a two-host dialogue script using Anthropic Claude
3. Synthesizes multi-speaker audio using Google Cloud Text-to-Speech Long Audio Synthesis
4. Uploads the episode and RSS feed to AWS S3
5. Optionally tracks episodes in MongoDB to avoid republishing duplicates

## Quick start

Pull and run from the GitHub Container Registry:

```bash
docker run --rm \
  -e ANTHROPIC_API_KEY="your-key" \
  -e GCS_BUCKET_NAME="your-gcs-bucket" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/run/secrets/gcp-creds.json" \
  -e S3_BUCKET_NAME="your-s3-bucket" \
  -e AWS_ACCESS_KEY_ID="your-aws-key" \
  -e AWS_SECRET_ACCESS_KEY="your-aws-secret" \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

Common flags:

```bash
# Script only (no audio or upload)
--script-only

# Custom show name and voice selection
--show-name "Tech Brief" \
--male-voice "en-US-Studio-Q" \
--female-voice "en-US-Studio-O"

# Limit sources and categories
--sources wired techcrunch \
--categories security ai \
--max-articles 3

# Skip S3 upload, save output locally
--no-s3 --output ./output
```

For the full CLI reference and Docker examples, see the [Usage Guide](https://the-data-packet.thewintershadow.com/getting-started/usage/).

## Requirements

| Requirement | Notes |
|---|---|
| Anthropic API key | Script generation via Claude |
| Google Cloud service account | TTS Long Audio Synthesis + GCS bucket |
| AWS credentials | S3 hosting and RSS feed (skip with `--no-s3`) |
| Docker 20.10+ | Recommended deployment method |
| MongoDB (optional) | Episode tracking and deduplication |

## Development

This project uses [Hatch](https://hatch.pypa.io/) for environment and build management.

```bash
git clone https://github.com/TheWinterShadow/The-Data-Packet.git
cd The-Data-Packet

# Install Hatch if needed
pip install hatch

# Run tests
hatch run test

# Type checking
hatch run lint:typing

# Format and lint
hatch run lint:fmt
hatch run lint:style
```

See the [Development Guide](https://the-data-packet.thewintershadow.com/contributing/) for full setup instructions, contribution guidelines, and architecture details.

## Documentation

The full documentation site covers:

- [Getting Started](https://the-data-packet.thewintershadow.com/getting-started/) — installation and first run
- [Usage Guide](https://the-data-packet.thewintershadow.com/getting-started/usage/) — CLI reference and examples
- [Architecture](https://the-data-packet.thewintershadow.com/overview/architecture/) — system design and pipeline overview
- [Infrastructure](https://the-data-packet.thewintershadow.com/infrastructure/) — Docker, GCS, MongoDB, Terraform
- [Contributing](https://the-data-packet.thewintershadow.com/contributing/) — development setup and guidelines
- [API Reference](https://the-data-packet.thewintershadow.com/reference/) — auto-generated from source

## License

MIT — see [LICENSE](LICENSE) for details.
