---
title: Development Setup
description: Local dev environment, running tests, code quality tools, and building documentation.
icon: material/wrench
---

# Development Setup

## Prerequisites

- Python 3.9+
- [Hatch](https://hatch.pypa.io/) — build tool and environment manager
- `ffmpeg` — for audio processing tests

```bash
pip install hatch

# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get install ffmpeg
```

---

## Clone and install

```bash
git clone https://github.com/TheWinterShadow/The-Data-Packet.git
cd The-Data-Packet

# Activate the default hatch environment (installs all dev deps)
hatch shell
```

Hatch manages virtual environments automatically. The `default` environment includes
pytest, mypy, black, isort, and all other dev tools.

---

## Project structure

```
The-Data-Packet/
├── the_data_packet/        # Main application package
│   ├── core/               # Config, exceptions, logging
│   ├── sources/            # Article collection (Wired, TechCrunch)
│   ├── generation/         # Script and audio generation
│   ├── utils/              # HTTP, S3, MongoDB, Loki clients
│   └── workflows/          # PodcastPipeline orchestration
├── tests/                  # Test suite (mirrors package structure)
├── docs/                   # Zensical documentation (this site)
├── sphinx/                 # Sphinx API reference source
├── infra/                  # Terraform infrastructure
├── zensical.toml           # Documentation site config
├── pyproject.toml          # Build system and tool config
└── Dockerfile              # Production Docker image
```

---

## Running tests

=== "All tests"

    ```bash
    hatch run test
    ```

=== "With coverage"

    ```bash
    hatch run test-cov
    hatch run cov-report
    ```

=== "Specific file"

    ```bash
    hatch run test tests/sources/test_wired.py
    ```

=== "All Python versions"

    ```bash
    hatch run all:test
    ```

!!! info "No real API keys needed"

    External API calls (Claude, Google Cloud TTS, S3) are all mocked in the test suite.
    231+ tests run without any real credentials.

---

## Code quality

```bash
# Format (black + isort)
hatch run format

# Check formatting without modifying
hatch run format-check

# Type checking
hatch run typecheck

# All quality checks
hatch run check
```

---

## Building documentation

=== "Zensical (this site)"

    ```bash
    hatch run docs:build
    # Output: site/
    ```

=== "Sphinx (API reference)"

    ```bash
    hatch run docs:build-sphinx
    # Output: site/reference/
    ```

=== "Both"

    ```bash
    hatch run docs:build-all
    ```

=== "Local preview"

    ```bash
    hatch run docs:serve
    # Opens http://localhost:8000
    ```

---

## Quick end-to-end test with real APIs

```bash
cp .env.template .env
# Fill in real API keys

hatch run the-data-packet \
  --script-only \
  --output ./test-output \
  --log-level DEBUG
```

Then inspect the structured logs:

```bash
cat test-output/logs/*.jsonl | jq .
```

---

## Useful snippets

=== "Test a source"

    ```python
    from the_data_packet.sources.wired import WiredSource

    source = WiredSource()
    articles = source.collect_articles(
        categories=["security"], max_articles=2
    )
    for article in articles:
        print(article.title, article.url)
    ```

=== "Test config loading"

    ```python
    from the_data_packet import get_config

    config = get_config(show_name="Test Show", max_articles_per_source=1)
    print(config.show_name)
    print(config.male_voice)
    ```

---

## CI pipeline

The GitHub Actions CI runs on every push and PR:

- [x] Format check — `isort` + `black`
- [x] Type check — `mypy`
- [x] Tests — `pytest` with coverage on Python 3.10–3.12
- [x] Coverage report — uploaded to Codecov
- [x] Docs build — Zensical + Sphinx, deployed to GitHub Pages
- [x] Docker build — Multi-platform image published to GHCR

All checks must pass before a PR can be merged.
