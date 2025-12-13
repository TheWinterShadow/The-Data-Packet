# Usage Guide - The Data Packet

This guide covers all aspects of using The Data Packet Docker image for automated podcast generation.

## 📦 Getting the Image

### Pull from GitHub Container Registry (Recommended)

```bash
# Latest stable version
docker pull ghcr.io/thewintershadow/the-data-packet:latest

# Specific version
docker pull ghcr.io/thewintershadow/the-data-packet:v2.0.0

# Development version
docker pull ghcr.io/thewintershadow/the-data-packet:main
```

### Build from Source

```bash
git clone https://github.com/TheWinterShadow/the_data_packet.git
cd the_data_packet
docker build -t the-data-packet:local .
```

## 🔑 API Keys Setup

### Required API Keys

1. **Anthropic API Key** (for Claude AI script generation)
   - Get from: https://console.anthropic.com/
   - Used for: Converting articles into podcast dialogue

2. **Google API Key** (for Gemini TTS audio generation)
   - Get from: https://console.cloud.google.com/
   - Enable: Generative AI API
   - Used for: Converting scripts to multi-speaker audio

### Setting Up Environment Variables

**Option 1: Environment File (.env)**
```bash
# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
GOOGLE_API_KEY=AIzaSyYour-google-key-here
EOF

# Use with Docker
docker run --rm --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

**Option 2: Command Line**
```bash
docker run --rm \
  -e ANTHROPIC_API_KEY="sk-ant-api03-your-key" \
  -e GOOGLE_API_KEY="AIzaSyYour-google-key" \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

## 🎬 Basic Usage

### Generate Complete Podcast

```bash
# Default: Generate script + audio for security and guide articles
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

**Output:**
- `output/episode_script.txt` - Generated podcast script
- `output/episode.wav` - Generated audio file

### Generate Script Only

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --script-only
```

### Generate Audio from Existing Script

```bash
# First, ensure you have a script file
ls output/episode_script.txt

# Generate audio
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --audio-only \
  --script-file /app/output/episode_script.txt
```

## 🎛️ Advanced Configuration

### Custom Show Configuration

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --show-name "Tech Brief Daily" \
  --episode-date "Monday, December 16, 2024" \
  --categories security guide \
  --script-filename "tech_brief.txt" \
  --audio-filename "tech_brief.wav"
```

### Voice Customization

Available voices:
- **Puck** - Energetic and dynamic
- **Charon** - Deep and authoritative  
- **Kore** - Warm and conversational
- **Fenrir** - Rich and engaging
- **Aoede** - Clear and professional
- **Zephyr** - Natural and balanced

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --voice-a Charon \
  --voice-b Aoede \
  --show-name "Professional Tech Update"
```

### Category Selection

Available categories:
- `security` - Cybersecurity and privacy articles
- `guide` - How-to and tutorial articles

```bash
# Security articles only
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --categories security

# Both categories (default)
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --categories security guide
```

## 🐳 Docker Compose Usage

### Simple Setup

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  podcast-generator:
    image: ghcr.io/thewintershadow/the-data-packet:latest
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./output:/app/output
    command: ["--show-name", "Daily Tech Update"]
```

Run:
```bash
docker-compose up
```

### Advanced Multi-Service Setup

```yaml
version: '3.8'
services:
  # Complete podcast generation
  podcast-generator:
    image: ghcr.io/thewintershadow/the-data-packet:latest
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./output:/app/output
    command: [
      "--show-name", "Tech Daily",
      "--categories", "security", "guide",
      "--voice-a", "Puck",
      "--voice-b", "Kore"
    ]
    
  # Script-only generation
  script-only:
    image: ghcr.io/thewintershadow/the-data-packet:latest
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./scripts:/app/output
    command: [
      "--script-only",
      "--show-name", "Quick Scripts",
      "--categories", "security"
    ]
    profiles: ["script"]
    
  # Audio-only generation  
  audio-only:
    image: ghcr.io/thewintershadow/the-data-packet:latest
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./output:/app/output
    command: [
      "--audio-only",
      "--script-file", "/app/output/episode_script.txt"
    ]
    profiles: ["audio"]
```

Run specific services:
```bash
# Default podcast generation
docker-compose up podcast-generator

# Script only
docker-compose --profile script up script-only

# Audio only
docker-compose --profile audio up audio-only
```

## 📋 Complete CLI Reference

### Core Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output DIR` | Output directory | `./output` |
| `--show-name NAME` | Podcast show name | `Tech Daily` |
| `--episode-date DATE` | Episode date | Current date |
| `--categories CAT1 CAT2` | Article categories | `security guide` |

### Generation Control

| Option | Description |
|--------|-------------|
| `--script-only` | Generate script only, skip audio |
| `--audio-only` | Generate audio only from existing script |
| `--script-file PATH` | Script file for audio-only mode |

### Voice Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `--voice-a VOICE` | Voice for Alex | `Puck` |
| `--voice-b VOICE` | Voice for Sam | `Kore` |

### Output Files

| Option | Description | Default |
|--------|-------------|---------|
| `--script-filename FILE` | Script filename | `episode_script.txt` |
| `--audio-filename FILE` | Audio filename | `episode.wav` |

### API Keys (Override Environment)

| Option | Description |
|--------|-------------|
| `--anthropic-key KEY` | Anthropic API key |
| `--google-key KEY` | Google API key |

### Debugging

| Option | Description |
|--------|-------------|
| `--verbose` | Verbose logging |
| `--debug` | Debug logging |
| `--quiet` | Quiet mode (errors only) |
| `--no-cleanup` | Don't clean up temp files |
| `--validate` | Validate results after generation |

## 🔄 Production Workflows

### Scheduled Podcast Generation

**Using Cron:**
```bash
# Add to crontab (daily at 8 AM)
0 8 * * * docker run --rm --env-file /path/to/.env -v /path/to/output:/app/output ghcr.io/thewintershadow/the-data-packet:latest
```

**Using systemd timer:**
```ini
# /etc/systemd/system/podcast-generator.service
[Unit]
Description=Daily Tech Podcast Generator
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker run --rm --env-file /opt/podcast/.env -v /opt/podcast/output:/app/output ghcr.io/thewintershadow/the-data-packet:latest

# /etc/systemd/system/podcast-generator.timer
[Unit]
Description=Run podcast generator daily
Requires=podcast-generator.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

### CI/CD Integration

**GitHub Actions:**
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
          -e GOOGLE_API_KEY="${{ secrets.GOOGLE_API_KEY }}" \
          -v "/tmp/output:/app/output" \
          ghcr.io/thewintershadow/the-data-packet:latest
          
    - name: Upload Artifacts
      uses: actions/upload-artifact@v3
      with:
        name: podcast-episode
        path: /tmp/output/
```

## 🛠️ Troubleshooting

### Common Issues

**1. Permission Denied on Output Directory**
```bash
# Fix: Ensure output directory is writable
chmod 755 ./output

# Or run with user mapping
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

**2. API Key Errors**
```bash
# Verify API keys are set
docker run --rm \
  --env-file .env \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --debug
```

**3. Out of Memory**
```bash
# Run with memory limit
docker run --rm \
  --memory=2g \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

### Debug Mode

```bash
# Enable debug logging
docker run --rm \
  --env-file .env \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --debug

# Get help
docker run --rm \
  ghcr.io/thewintershadow/the-data-packet:latest \
  --help
```

### Health Check

```bash
# Verify container health
docker run --rm \
  ghcr.io/thewintershadow/the-data-packet:latest \
  -c "python -c 'import the_data_packet; print(\"OK\")'"
```

## 📊 Monitoring

### Container Logs

```bash
# Follow logs in real-time
docker logs -f podcast-generator

# View recent logs
docker logs --tail 50 podcast-generator
```

### Resource Usage

```bash
# Monitor resource usage
docker stats podcast-generator

# Check container health
docker inspect --format='{{.State.Health.Status}}' podcast-generator
```

## 🔒 Security Best Practices

1. **Environment Variables**: Always use environment variables for API keys
2. **Volume Mounts**: Use read-only mounts when possible
3. **User Context**: Run with specific user IDs in production
4. **Network**: Use custom networks for multi-container setups
5. **Secrets**: Use Docker secrets or external secret managers

```bash
# Secure production example
docker run --rm \
  --read-only \
  --user "1000:1000" \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --env-file .env \
  -v "$(pwd)/output:/app/output:Z" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/TheWinterShadow/the_data_packet/issues)
- **Documentation**: [GitHub Repository](https://github.com/TheWinterShadow/the_data_packet)
- **Docker Images**: [GitHub Container Registry](https://github.com/TheWinterShadow/the_data_packet/pkgs/container/the-data-packet)