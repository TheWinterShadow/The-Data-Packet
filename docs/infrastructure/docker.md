---
title: Docker
description: Docker deployment guide — image registry, permissions, Compose, and production hardening.
icon: fontawesome/brands/docker
---

# Docker Deployment

Docker is the recommended way to run The Data Packet in production. The image includes
all system dependencies (including `ffmpeg`) and runs as a non-root user.

---

## Quick run

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/service-account-key.json:/credentials.json:ro" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

---

## Image tags

| Tag | Description |
|---|---|
| `latest` | Latest stable release |
| `v2.0.0` | Specific version pin |
| `main` | Latest commit on main |
| `sha-abc1234` | Specific commit SHA |

Platforms: `linux/amd64` · `linux/arm64`

---

## Output directory permissions

!!! warning "Required before first run"

    The container runs as UID `1000` (user `app`). The host output directory must be
    writable by that user:

    ```bash
    mkdir -p output
    sudo chown -R 1000:1000 output
    ```

    Or world-writable (less secure):
    ```bash
    chmod 777 output
    ```

---

## Environment file

```bash
cp .env.template .env
# Edit .env with your keys
```

Minimum `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
GCS_BUCKET_NAME=your-gcs-bucket
GOOGLE_APPLICATION_CREDENTIALS=/credentials.json
```

---

## Common usage

=== "Full episode"

    ```bash
    docker run --rm --env-file .env \
      -v "$(pwd)/output:/app/output" \
      -v "$(pwd)/key.json:/credentials.json:ro" \
      ghcr.io/thewintershadow/the-data-packet:latest
    ```

=== "Script only"

    ```bash
    docker run --rm --env-file .env \
      -v "$(pwd)/output:/app/output" \
      -v "$(pwd)/key.json:/credentials.json:ro" \
      ghcr.io/thewintershadow/the-data-packet:latest \
      --script-only
    ```

=== "Custom show + sources"

    ```bash
    docker run --rm --env-file .env \
      -v "$(pwd)/output:/app/output" \
      -v "$(pwd)/key.json:/credentials.json:ro" \
      ghcr.io/thewintershadow/the-data-packet:latest \
      --show-name "Daily Security Brief" \
      --sources wired techcrunch \
      --categories security \
      --max-articles 2
    ```

=== "Debug mode"

    ```bash
    docker run --rm --env-file .env \
      -v "$(pwd)/output:/app/output" \
      -v "$(pwd)/key.json:/credentials.json:ro" \
      ghcr.io/thewintershadow/the-data-packet:latest \
      --log-level DEBUG \
      --save-intermediate
    ```

---

## Docker Compose

=== "Simple"

    ```yaml title="docker-compose.yml"
    services:
      podcast-generator:
        image: ghcr.io/thewintershadow/the-data-packet:latest
        env_file: .env
        volumes:
          - ./output:/app/output
          - ./service-account-key.json:/credentials.json:ro
        command:
          - --show-name
          - "Tech Brief Daily"
          - --sources
          - wired
          - techcrunch
    ```

=== "With MongoDB"

    ```yaml title="docker-compose.yml"
    services:
      mongodb:
        image: mongo:7
        environment:
          MONGO_INITDB_ROOT_USERNAME: admin
          MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
        volumes:
          - mongo-data:/data/db

      podcast-generator:
        image: ghcr.io/thewintershadow/the-data-packet:latest
        env_file: .env
        depends_on:
          - mongodb
        volumes:
          - ./output:/app/output
          - ./service-account-key.json:/credentials.json:ro

    volumes:
      mongo-data:
    ```

---

## Building from source

```bash
git clone https://github.com/TheWinterShadow/The-Data-Packet.git
cd The-Data-Packet

# Single platform
docker build -t the-data-packet:local .

# Multi-platform push
docker buildx create --name multiplatform --bootstrap --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t the-data-packet:latest \
  --push .
```

---

## Security hardening

The image is already production-hardened:

- [x] Runs as non-root (`app`, UID 1000)
- [x] `python:3.11-slim` minimal base image
- [x] No hardcoded secrets
- [x] Read-only credential mount

Additional production flags:

```bash
docker run --rm \
  --read-only \
  --user "1000:1000" \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --env-file .env \
  -v "$(pwd)/output:/app/output:Z" \
  -v "$(pwd)/key.json:/credentials.json:ro" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

---

## Monitoring

```bash
# Live logs
docker logs -f podcast-generator

# Resource usage
docker stats podcast-generator

# Health check
docker inspect --format='{{.State.Health.Status}}' podcast-generator
```

---

## Troubleshooting

!!! failure "ARM64 exec format error"

    ```
    exec /usr/local/bin/python: exec format error
    ```

    Pull explicitly for your platform:
    ```bash
    docker pull --platform linux/arm64 \
      ghcr.io/thewintershadow/the-data-packet:latest
    ```

!!! failure "Permission denied on output"

    ```bash
    sudo chown -R 1000:1000 output
    ```

!!! failure "Container exits immediately"

    Check what error the container emits:
    ```bash
    docker run --rm --env-file .env \
      ghcr.io/thewintershadow/the-data-packet:latest --help
    ```
