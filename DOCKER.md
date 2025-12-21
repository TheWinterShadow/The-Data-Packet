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

## 🚀 Running with Configuration Variables

### Method 1: Using Environment File (Recommended)

Create a `.env` file with your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
ELEVENLABS_API_KEY=sk_your-elevenlabs-key-here
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-west-2
S3_BUCKET_NAME=your-bucket-name
```

**Set up the output directory with proper permissions:**

```bash
# Create output directory and set permissions for the container user (UID 1000)
mkdir -p output
sudo chown -R 1000:1000 output

# Or if you don't want to use sudo, make it writable for everyone
mkdir -p output
chmod 777 output
```

Then run with the environment file:

```bash
# Build the image first
docker build -t the-data-packet .

# Run full pipeline (note: you need to specify at least output directory to avoid help message)
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  the-data-packet \
  --output /app/output

# Or use the published image
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  thewintershadow/the-data-packet:latest \
  --output /app/output
```

### Method 2: Direct Environment Variables

**First, set up the output directory permissions:**

```bash
mkdir -p output
sudo chown -R 1000:1000 output
# Or alternatively: chmod 777 output
```

```bash
docker run --rm \
  -e ANTHROPIC_API_KEY='your-anthropic-key' \
  -e ELEVENLABS_API_KEY='your-elevenlabs-key' \
  -e AWS_ACCESS_KEY_ID='your-aws-access-key' \
  -e AWS_SECRET_ACCESS_KEY='your-aws-secret-key' \
  -e AWS_REGION='us-west-2' \
  -e S3_BUCKET_NAME='your-bucket-name' \
  -v "$(pwd)/output:/app/output" \
  the-data-packet \
  --output /app/output
```

### Method 3: Using CLI Arguments

Pass additional configuration via CLI arguments:

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  the-data-packet \
  --show-name "Daily Tech Brief" \
  --sources wired techcrunch \
  --categories security ai guide \
  --max-articles 2 \
  --log-level INFO \
  --save-intermediate
```

## 📋 Common Usage Examples

### Complete Podcast Generation
```bash
# Using published image
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  thewintershadow/the-data-packet:latest \
  --output /app/output \
  --show-name "The Data Packet" \
  --sources wired techcrunch \
  --categories security ai \
  --max-articles 1
```

### Script Only Generation
```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  thewintershadow/the-data-packet:latest \
  --script-only \
  --output /app/output
```

### Audio Only from Existing Script
```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  thewintershadow/the-data-packet:latest \
  --audio-only \
  --script-file /app/output/episode_script.txt
```

### Custom Voices and Settings
```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  thewintershadow/the-data-packet:latest \
  --output /app/output \
  --voice-a XrExE9yKIg1WjnnlVkGX \
  --voice-b IKne3meq5aSn9XLyUdCD \
  --show-name "Custom Tech News" \
  --log-level DEBUG \
  --save-intermediate
```

### Disable S3 Uploads
```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  thewintershadow/the-data-packet:latest \
  --output /app/output \
  --no-s3
```

## ⚠️ Important Notes

- **Always specify `--output /app/output`** to avoid the help message and ensure proper output directory mapping
- **Set correct permissions** on the output directory: `sudo chown -R 1000:1000 output` or `chmod 777 output`
- The container defaults to showing help when no arguments are provided
- The container runs as non-root user (UID 1000) for security
- Use `thewintershadow/the-data-packet:latest` for the published image or build locally with `docker build -t the-data-packet .`
- The `.env` file must be in your current directory when using `--env-file .env`

## 🔧 Troubleshooting Permission Issues

If you get permission denied errors:

```bash
# Option 1: Set ownership to container user (UID 1000)
sudo chown -R 1000:1000 output

# Option 2: Make directory writable by all (less secure)
chmod 777 output

# Option 3: Run container as current user (may have other implications)
docker run --rm \
  --user $(id -u):$(id -g) \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  thewintershadow/the-data-packet:latest \
  --output /app/output
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