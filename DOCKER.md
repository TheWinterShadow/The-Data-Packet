# Docker Deployment Guide

## 🐳 Overview

The Data Packet is now optimized for Docker deployment with a comprehensive CLI interface. This guide shows you how to deploy and run the podcast generator in various configurations.

## 📦 What's Included

- **Dockerfile**: Production-ready container with security best practices
- **docker-compose.yml**: Multi-service orchestration for different use cases
- **deploy.sh**: Automated deployment script
- **.env.template**: Environment variable template
- **CLI Interface**: Full command-line interface for all operations

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
# GOOGLE_API_KEY=your-gemini-key
```

### 2. Deploy with Script

```bash
# Build the Docker image
./deploy.sh build

# Generate complete podcast
./deploy.sh run

# Generate script only
./deploy.sh script

# Generate audio from existing script
./deploy.sh audio

# Custom generation
./deploy.sh custom --show-name "My Podcast" --categories security
```

### 3. Manual Docker Commands

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
GOOGLE_API_KEY=AIzaSy...

# Optional
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

### Docker Compose Services

```bash
# Default: Complete podcast generation
docker-compose up podcast-generator

# Script only
docker-compose --profile script-only up script-only

# Audio only  
docker-compose --profile audio-only up audio-only
```

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