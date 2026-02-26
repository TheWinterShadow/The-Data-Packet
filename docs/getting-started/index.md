---
title: Quick Start
description: Get your first AI-generated podcast episode running in 5 minutes with Docker or pip.
icon: material/rocket-launch
---

# Quick Start

Get your first AI-generated podcast episode in about 5 minutes.

---

## Prerequisites

!!! abstract "What you need"

    **Required**

    - **Anthropic API key** — Claude script generation.
      Get one at [console.anthropic.com](https://console.anthropic.com/).
    - **Google Cloud project** with TTS + GCS enabled.
      Use the [Terraform setup](../infrastructure/terraform.md) to provision everything automatically.

    **Optional**

    AWS S3 (hosting), MongoDB (deduplication), and Grafana Loki (logging) are all optional.
    The core pipeline works without them — output is saved locally.

---

## 5-minute quickstart

=== ":fontawesome-brands-docker: Docker (recommended)"

    **Step 1 — Pull the image**

    ```bash
    docker pull ghcr.io/thewintershadow/the-data-packet:latest
    ```

    **Step 2 — Create an environment file**

    ```bash
    cat > .env << 'EOF'
    ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
    GCS_BUCKET_NAME=your-gcs-bucket-name
    GOOGLE_APPLICATION_CREDENTIALS=/credentials.json
    EOF
    ```

    **Step 3 — Fix output directory permissions**

    ```bash
    mkdir -p output
    sudo chown -R 1000:1000 output  # (1)!
    ```

    1. The container runs as UID 1000. This ensures it can write to the mounted volume.

    **Step 4 — Run**

    ```bash
    docker run --rm \
      --env-file .env \
      -v "$(pwd)/output:/app/output" \
      -v "$(pwd)/service-account-key.json:/credentials.json:ro" \
      ghcr.io/thewintershadow/the-data-packet:latest
    ```

=== ":fontawesome-brands-python: pip"

    ```bash
    pip install the-data-packet

    # Set required env vars
    export ANTHROPIC_API_KEY="sk-ant-api03-your-key"
    export GCS_BUCKET_NAME="your-gcs-bucket"
    export GOOGLE_APPLICATION_CREDENTIALS="./service-account-key.json"

    # Run
    the-data-packet --output ./episode
    ```

---

## What you'll get

After a few minutes the pipeline completes and you'll have:

```
output/
├── episode_script.txt    # Two-host dialogue script
└── episode.wav           # Synthesized audio file
```

!!! success "That's it!"

    You now have a complete podcast episode. The script is the raw dialogue,
    and the `.wav` file is ready to upload to any podcast host.

---

## What just happened?

``` mermaid
sequenceDiagram
    participant You
    participant Pipeline
    participant Wired
    participant Claude
    participant GoogleTTS

    You->>Pipeline: docker run ...
    Pipeline->>Wired: fetch RSS feed
    Wired-->>Pipeline: latest articles
    Pipeline->>Claude: write podcast script
    Claude-->>Pipeline: two-host dialogue
    Pipeline->>GoogleTTS: synthesize audio
    GoogleTTS-->>Pipeline: episode.wav
    Pipeline-->>You: output/episode_script.txt + episode.wav
```

---

## Next steps

<div class="grid cards" markdown>

-   :material-package-variant-closed: **Installation options**

    ---

    All ways to install: Docker, pip, or from source, with platform notes.

    [Installation →](installation.md)

-   :material-tune: **CLI reference**

    ---

    Every flag, voice option, source selector, and output setting documented.

    [Usage →](usage.md)

-   :material-cog: **Configuration**

    ---

    All environment variables with defaults and examples.

    [Configuration →](../configuration/index.md)

</div>
