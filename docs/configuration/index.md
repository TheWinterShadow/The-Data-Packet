---
title: Configuration
description: Every environment variable, its default, and examples — the complete configuration reference.
icon: material/tune
---

# Configuration Reference

The Data Packet is configured entirely through environment variables. No config file is required.

---

## Resolution order

Config values resolve from highest to lowest priority:

```
1. get_config(keyword=value)    ← Python API direct override (highest)
2. CLI flags                    ← --show-name, --male-voice, etc.
3. Environment variables        ← SHOW_NAME, MALE_VOICE, etc.
4. Built-in defaults            ← hardcoded in Config dataclass (lowest)
```

---

## Required

!!! danger "Required variables"

    The pipeline will not start without these two.

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude script generation. Get one at [console.anthropic.com](https://console.anthropic.com/). |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket used as intermediate storage during Long Audio Synthesis. |

---

## Google Cloud credentials

=== "Service account JSON (recommended)"

    ```bash
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
    ```

    Mount into Docker:
    ```bash
    -v "$(pwd)/service-account-key.json:/credentials.json:ro" \
    -e GOOGLE_APPLICATION_CREDENTIALS=/credentials.json
    ```

=== "Application Default Credentials"

    If running on GCP (Compute Engine, Cloud Run, GKE), credentials are provided
    automatically by the environment — no variable needed.

---

## AWS S3 (optional)

!!! info

    If `S3_BUCKET_NAME` is not set, S3 upload is silently skipped and files are saved locally only.

| Variable | Default | Description |
|---|---|---|
| `S3_BUCKET_NAME` | — | S3 bucket name |
| `AWS_ACCESS_KEY_ID` | — | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | — | AWS secret key |
| `AWS_REGION` | `us-east-1` | AWS region |

---

## MongoDB (optional)

!!! info

    If credentials are absent, deduplication is skipped. All articles are always eligible.

| Variable | Default | Description |
|---|---|---|
| `MONGODB_USERNAME` | — | MongoDB username |
| `MONGODB_PASSWORD` | — | MongoDB password |
| `MONGODB_HOST` | `localhost` | MongoDB host |
| `MONGODB_PORT` | `27017` | MongoDB port |
| `MONGODB_DATABASE` | `the_data_packet` | Database name |

---

## Podcast content

| Variable | Default | Description |
|---|---|---|
| `SHOW_NAME` | `The Data Packet` | Podcast show name, used in script and RSS feed |
| `MAX_ARTICLES` | `1` | Maximum articles fetched per source per run |

---

## Audio voices

!!! note "Studio voices only"

    Only `en-US-Studio-*` voices are compatible with Long Audio Synthesis.
    Standard and WaveNet voices are not supported.

| Variable | Default | Description |
|---|---|---|
| `MALE_VOICE` | `en-US-Studio-Q` | Voice for first speaker (Alex) |
| `FEMALE_VOICE` | `en-US-Studio-O` | Voice for second speaker (Sam) |

**Available Studio voices:**

| Voice ID | Character |
|---|---|
| `en-US-Studio-Q` | Male — warm, professional |
| `en-US-Studio-O` | Female — clear, engaging |
| `en-US-Studio-M` | Male — authoritative |

---

## Logging

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `LOG_DIRECTORY` | `output/logs` | Directory for JSONL log files |
| `ENABLE_JSONL_LOGGING` | `true` | Write structured JSONL log files |
| `ENABLE_S3_LOG_UPLOAD` | `true` | Upload completed daily log files to S3 |
| `LOG_UPLOAD_INTERVAL` | `3600` | Seconds between S3 log upload checks |
| `REMOVE_LOGS_AFTER_UPLOAD` | `false` | Delete local files after S3 upload |

---

## Grafana Loki (optional)

| Variable | Description |
|---|---|
| `GRAFANA_LOKI_URL` | Loki push API URL (e.g. `https://loki.example.com`) |
| `GRAFANA_LOKI_USERNAME` | Basic auth username |
| `GRAFANA_LOKI_PASSWORD` | Basic auth password |

---

## Complete `.env` example

```bash title=".env"
# ── Required ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
GCS_BUCKET_NAME=my-tts-audio-bucket
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

# ── AWS S3 (optional) ────────────────────────────────────────────────────────
S3_BUCKET_NAME=my-podcast-hosting-bucket
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# ── MongoDB (optional) ───────────────────────────────────────────────────────
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your-password

# ── Podcast settings ─────────────────────────────────────────────────────────
SHOW_NAME=Tech Brief Daily
MAX_ARTICLES=1
MALE_VOICE=en-US-Studio-Q
FEMALE_VOICE=en-US-Studio-O

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL=INFO
ENABLE_JSONL_LOGGING=true
ENABLE_S3_LOG_UPLOAD=false
```

---

## Sources and categories

=== "CLI"

    ```bash
    the-data-packet \
      --sources wired techcrunch \
      --categories security ai \
      --max-articles 2
    ```

=== "Python API"

    ```python
    config = get_config(
        article_sources=["wired", "techcrunch"],
        article_categories=["security", "ai"],
        max_articles_per_source=2,
    )
    ```

**Available sources and categories:**

| Source | ID | Categories |
|---|---|---|
| Wired.com | `wired` | `security`, `science`, `ai` |
| TechCrunch | `techcrunch` | `ai`, `security` |
