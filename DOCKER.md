# Docker Deployment Guide

## 🐳 Overview

The Data Packet is now optimized for Docker deployment with a comprehensive CLI interface. This guide shows you how to deploy and run the podcast generator in various configurations.

## 📦 What's Included

- **Dockerfile**: Production-ready container with security best practices
- **.env.template**: Environment variable template
- **CLI Interface**: Full command-line interface for all operations
- **GitHub Actions**: Automated CI/CD for building and publishing

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/TheWinterShadow/the_data_packet.git
cd the_data_packet

# Setup environment
cp .env.template .env
# Edit .env with your API keys:
# ANTHROPIC_API_KEY=your-claude-key
# ELEVENLABS_API_KEY=your-elevenlabs-key
```

### 2. Build and Run with Docker

```bash
# Build the Docker image
docker build -t the-data-packet .

# Run the container
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  the-data-packet
```

### 3. GitHub Actions Deployment

The project includes GitHub Actions for automated building and publishing:

```bash
# Complete podcast generation
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  the-data-packet:latest \
  --output /app/output \
  --show-name "Daily Tech Update" \
  --categories security guide

# Script only
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  the-data-packet:latest \
  --script-only \
  --output /app/output

# Audio from existing script
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  the-data-packet:latest \
  --audio-only \
  --script-file /app/output/episode_script.txt
```

## 🎛️ CLI Options

```bash
# Core options
--output DIR                    Output directory
--show-name NAME               Podcast show name
--episode-date DATE            Episode date
--categories CAT1 CAT2         Article categories

# Generation control
--script-only                  Generate script only
--audio-only                   Generate audio only
--script-file PATH             Script file for audio-only mode

# Audio configuration  
--voice-a VOICE               Voice for Alex (Puck, Charon, etc.)
--voice-b VOICE               Voice for Sam (Kore, Aoede, etc.)

# Output files
--script-filename FILE        Script filename
--audio-filename FILE         Audio filename

# Debugging
--verbose                     Verbose logging
--debug                       Debug logging
--quiet                       Quiet mode

# API keys (override environment variables)
--anthropic-key KEY           Anthropic API key
--google-key KEY              Google API key
```

## 🔧 Configuration

### Environment Variables

Set these in your `.env` file:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...

# Optional
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-podcast-bucket
```

### Docker Compose Services

> **Note**: Docker Compose configuration removed in favor of direct `docker build` and GitHub Actions workflow.

## 📁 File Structure

```
/app/
├── the_data_packet/    # Application code
├── output/             # Generated files (mounted volume)
├── pyproject.toml      # Package configuration
└── README.md           # Documentation

# Host machine
./output/               # Persistent output directory
├── episode_script.txt  # Generated script
└── episode.wav         # Generated audio
```

## 🛡️ Security Features

- **Non-root user**: Container runs as `app` user
- **Minimal base image**: Python 3.11 slim
- **Environment variables**: No hardcoded secrets
- **Volume mounts**: Secure file access
- **Health checks**: Container health monitoring

## 🔍 Troubleshooting

### Check Container Status
```bash
docker ps
docker logs podcast-generator
```

### Debug Mode
```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  the-data-packet:latest \
  --debug \
  --categories security
```

### Verify Environment
```bash
docker run --rm --env-file .env the-data-packet:latest --help
```

## 🚢 Production Deployment

### Build for Production
```bash
# Multi-platform build
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t the-data-packet:latest \
  --push .

# Run in production
docker run -d \
  --name podcast-generator \
  --restart unless-stopped \
  --env-file .env \
  -v podcast-output:/app/output \
  the-data-packet:latest \
  --output /app/output \
  --quiet
```

### Kubernetes Deployment
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: podcast-generator
spec:
  schedule: "0 8 * * 1-5"  # Run weekdays at 8 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: podcast-generator
            image: the-data-packet:latest
            env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: podcast-secrets
                  key: anthropic-key
            - name: GOOGLE_API_KEY
              valueFrom:
                secretKeyRef:
                  name: podcast-secrets
                  key: google-key
            volumeMounts:
            - name: output
              mountPath: /app/output
          volumes:
          - name: output
            persistentVolumeClaim:
              claimName: podcast-storage
          restartPolicy: OnFailure
```

## 📊 Monitoring

### Health Check
```bash
docker inspect --format='{{.State.Health.Status}}' podcast-generator
```

### Logs
```bash
docker logs -f podcast-generator
```

### Metrics
```bash
docker stats podcast-generator
```