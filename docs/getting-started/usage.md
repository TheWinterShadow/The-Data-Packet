---
title: Usage
description: Full CLI reference, common examples, Python API, and automation patterns.
icon: material/console
---

# Usage

## CLI reference

The `the-data-packet` command runs the full pipeline. All options can also be set via
environment variables — CLI flags override them.

```bash
the-data-packet [OPTIONS]
```

### API keys

| Option | Env var | Description |
|---|---|---|
| `--anthropic-key KEY` | `ANTHROPIC_API_KEY` | Anthropic (Claude) API key |
| `--gcs-bucket NAME` | `GCS_BUCKET_NAME` | GCS bucket for audio synthesis |
| `--google-credentials PATH` | `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON |
| `--mongodb-username USER` | `MONGODB_USERNAME` | MongoDB username (optional) |
| `--mongodb-password PASS` | `MONGODB_PASSWORD` | MongoDB password (optional) |
| `--s3-bucket BUCKET` | `S3_BUCKET_NAME` | S3 bucket for uploads (optional) |

### Content

| Option | Default | Description |
|---|---|---|
| `--sources SOURCE ...` | `wired` | Sources: `wired`, `techcrunch` |
| `--categories CAT ...` | `security ai` | Categories to fetch |
| `--max-articles N` | `1` | Articles per source |

### Generation

| Option | Description |
|---|---|
| `--script-only` | Generate script, skip audio |
| `--audio-only` | Generate audio from an existing script |

### Audio voices

| Option | Default | Description |
|---|---|---|
| `--male-voice VOICE` | `en-US-Studio-Q` | Google Cloud TTS voice for first speaker (Alex) |
| `--female-voice VOICE` | `en-US-Studio-O` | Google Cloud TTS voice for second speaker (Sam) |

!!! info "Available Studio voices"

    Only `en-US-Studio-*` voices support multi-speaker Long Audio Synthesis.

    | Voice ID | Character |
    |---|---|
    | `en-US-Studio-Q` | Male — warm, professional |
    | `en-US-Studio-O` | Female — clear, engaging |
    | `en-US-Studio-M` | Male — authoritative |

### Output

| Option | Default | Description |
|---|---|---|
| `--output DIR` | `./output` | Output directory |
| `--show-name NAME` | `The Data Packet` | Podcast show name |
| `--no-s3` | — | Disable S3 uploads even if configured |
| `--save-intermediate` | — | Keep intermediate files |
| `--log-level LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

---

## Common examples

=== "Full episode"

    ```bash
    the-data-packet --output ./episode
    ```

=== "Script only"

    ```bash
    the-data-packet --script-only --output ./scripts
    ```

=== "Custom show + voices"

    ```bash
    the-data-packet \
      --show-name "Tech Brief" \
      --male-voice en-US-Studio-Q \
      --female-voice en-US-Studio-O \
      --output ./episode
    ```

=== "Multiple sources"

    ```bash
    the-data-packet \
      --sources wired techcrunch \
      --categories security ai \
      --max-articles 2 \
      --output ./multi-source
    ```

=== "Local only (no S3)"

    ```bash
    the-data-packet --no-s3 --output ./local-episode
    ```

=== "Debug"

    ```bash
    the-data-packet \
      --log-level DEBUG \
      --save-intermediate \
      --output ./debug
    ```

---

## Via Docker

All CLI options work identically when passed to the Docker image:

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/service-account-key.json:/credentials.json:ro" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --show-name "Daily Tech Brief" \
  --sources wired techcrunch \
  --categories security ai \
  --max-articles 2
```

---

## Python API

```python
from the_data_packet import PodcastPipeline, get_config

# With overrides
config = get_config(
    show_name="Tech Brief",
    max_articles_per_source=2,
    article_sources=["wired", "techcrunch"],
    article_categories=["security", "ai"],
    male_voice="en-US-Studio-Q",
    female_voice="en-US-Studio-O",
)

pipeline = PodcastPipeline(config)
result = pipeline.run()

if result.success:
    print(f"Script:   {result.script_path}")
    print(f"Audio:    {result.audio_path}")
    print(f"Time:     {result.execution_time_seconds:.1f}s")
    print(f"Articles: {result.number_of_articles_collected}")
    if result.s3_audio_url:
        print(f"S3 URL:   {result.s3_audio_url}")
else:
    print(f"Failed: {result.error_message}")
```

---

## Output files

| File | Description |
|---|---|
| `episode_script.txt` | Full two-host dialogue with `Alex:` / `Sam:` speaker labels |
| `episode.wav` | Synthesized multi-speaker audio at 44.1 kHz |
| `feed.xml` | RSS 2.0 podcast feed (only generated when S3 is configured) |

---

## Automation

=== ":octicons-clock-16: Cron"

    ```bash
    # Daily at 8 AM
    0 8 * * * docker run --rm \
      --env-file /opt/podcast/.env \
      -v /opt/podcast/output:/app/output \
      ghcr.io/thewintershadow/the-data-packet:latest
    ```

=== ":fontawesome-brands-github: GitHub Actions"

    ```yaml
    name: Generate Daily Podcast
    on:
      schedule:
        - cron: '0 8 * * 1-5'  # Weekdays at 8 AM UTC

    jobs:
      generate:
        runs-on: ubuntu-latest
        steps:
          - name: Generate Podcast
            run: |
              docker run --rm \
                -e ANTHROPIC_API_KEY="${{ secrets.ANTHROPIC_API_KEY }}" \
                -e GCS_BUCKET_NAME="${{ secrets.GCS_BUCKET_NAME }}" \
                -v "/tmp/output:/app/output" \
                ghcr.io/thewintershadow/the-data-packet:latest

          - name: Upload episode
            uses: actions/upload-artifact@v4
            with:
              name: podcast-episode
              path: /tmp/output/
    ```

=== ":simple-kubernetes: Kubernetes CronJob"

    ```yaml
    apiVersion: batch/v1
    kind: CronJob
    metadata:
      name: podcast-generator
    spec:
      schedule: "0 8 * * 1-5"
      jobTemplate:
        spec:
          template:
            spec:
              containers:
                - name: podcast-generator
                  image: ghcr.io/thewintershadow/the-data-packet:latest
                  env:
                    - name: ANTHROPIC_API_KEY
                      valueFrom:
                        secretKeyRef:
                          name: podcast-secrets
                          key: anthropic-key
                    - name: GCS_BUCKET_NAME
                      valueFrom:
                        secretKeyRef:
                          name: podcast-secrets
                          key: gcs-bucket
              restartPolicy: OnFailure
    ```

---

## Troubleshooting

!!! warning "Permission denied on output directory"

    The container runs as UID 1000. Fix with:
    ```bash
    sudo chown -R 1000:1000 output
    ```

!!! warning "API key not found"

    Verify your env file is being picked up:
    ```bash
    docker run --rm --env-file .env \
      ghcr.io/thewintershadow/the-data-packet:latest \
      --log-level DEBUG
    ```

!!! warning "ARM64 platform mismatch"

    ```bash
    docker pull --platform linux/arm64 \
      ghcr.io/thewintershadow/the-data-packet:latest
    ```
