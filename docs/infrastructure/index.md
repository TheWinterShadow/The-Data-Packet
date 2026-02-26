---
title: Infrastructure
description: Cloud architecture overview — GCP, AWS, MongoDB, and Grafana Loki setup.
icon: material/server
---

# Infrastructure

The Data Packet uses a hybrid cloud architecture: Google Cloud for audio synthesis,
AWS for podcast hosting, and optional MongoDB for episode tracking.

---

## Cloud components

``` mermaid
graph TB
    subgraph GCP ["Google Cloud Platform"]
        TTS["Cloud TTS\nLong Audio Synthesis"]
        GCS["Cloud Storage\n30-day lifecycle"]
        TTS -->|writes audio| GCS
    end

    subgraph AWS
        S3["S3 Bucket\nPodcast hosting\n(public read)"]
    end

    subgraph Optional
        MongoDB["MongoDB\nEpisode tracking"]
        Loki["Grafana Loki\nLog aggregation"]
    end

    Pipeline -->|synthesize| TTS
    GCS -->|download| Pipeline
    Pipeline -->|upload| S3
    Pipeline -->|record episode| MongoDB
    Pipeline -->|forward logs| Loki
```

---

## What you need to set up

<div class="grid cards" markdown>

-   :simple-anthropic: **Anthropic API key**

    ---

    Required for script generation. Get one at
    [console.anthropic.com](https://console.anthropic.com/).

    No infrastructure to provision.

-   :simple-googlecloud: **GCS bucket + TTS API**

    ---

    Required for audio synthesis. The [Terraform setup](terraform.md)
    provisions everything in one command.

-   :fontawesome-brands-aws: **AWS S3 bucket**

    ---

    Optional but recommended for podcast distribution. Terraform
    provisions this alongside the GCP resources.

-   :simple-mongodb: **MongoDB**

    ---

    Optional. Prevents article reuse across episodes. Use the
    included `mongodb.sh` script for a local Docker instance.

</div>

---

## Provisioning with Terraform

The `infra/` directory contains Terraform that provisions all required GCP and AWS
resources in one apply. See the [Terraform guide](terraform.md) for step-by-step
instructions.

!!! tip "One command provisions everything"

    ```bash
    cd infra/
    terraform init && terraform apply
    ```

---

## In this section

- [**Docker**](docker.md) — Docker deployment, compose, and production hardening
- [**Terraform**](terraform.md) — GCP + AWS infrastructure provisioning
- [**Logging**](logging.md) — Structured JSONL logging, S3 upload, and Grafana Loki
