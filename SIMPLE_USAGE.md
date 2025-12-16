# Simplified Data Packet Interface

This directory contains the simplified interface for The Data Packet, making podcast generation and S3 upload much easier.

## Quick Start

### 1. Simple Podcast Generation

```python
from the_data_packet import SimplePodcastGenerator

# Initialize (uses environment variables for API keys)
generator = SimplePodcastGenerator()

# Generate podcast
result = generator.generate_podcast(
    show_name="My Tech Show",
    categories=["security", "guide"]
)

if result.success:
    print(f"Audio file: {result.audio_path}")
    print(f"Script file: {result.script_path}")
```

### 2. Generate and Upload to S3

```python
from the_data_packet import SimplePodcastGenerator

# Initialize with S3 bucket
generator = SimplePodcastGenerator(
    s3_bucket="my-podcast-bucket"
)

# Generate and upload
result = generator.generate_podcast(
    show_name="Daily Tech",
    upload_to_s3=True,
    public_read=True
)

if result.success and result.s3_result:
    print(f"S3 URL: {result.s3_result.s3_url}")
```

### 3. Upload Existing Audio File

```python
from pathlib import Path
from the_data_packet import SimplePodcastGenerator

generator = SimplePodcastGenerator(s3_bucket="my-podcast-bucket")

result = generator.upload_existing_audio(
    audio_file=Path("./my_episode.wav"),
    show_name="Tech Daily",
    episode_date="2025-12-13"
)

if result.success:
    print(f"Uploaded to: {result.s3_url}")
```

## CLI Usage

### Simple CLI Command

```bash
# Generate podcast with environment API keys
simple-podcast-generator --show-name "My Tech Show"

# Generate and upload to S3
simple-podcast-generator --show-name "Daily Tech" --s3-bucket my-podcast-bucket

# Upload existing audio file
simple-podcast-generator --upload-only audio.wav --show-name "Tech Show" --episode-date 2025-12-13
```

## Environment Variables

Set these environment variables for authentication:

```bash
# Required for podcast generation
export ANTHROPIC_API_KEY="your-claude-api-key"
export GOOGLE_API_KEY="your-gemini-api-key" 

# Required for S3 upload
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
```

## Features

- **Simple API**: One class handles everything
- **Automatic S3 Upload**: Built-in upload with standardized naming
- **Error Handling**: Clear error messages and status reporting
- **Flexible Configuration**: Environment variables or direct parameters
- **Public/Private S3**: Choose public-read or private uploads

## S3 Object Structure

Files are uploaded with this structure:
```
episodes/
  show-name/
    2025-12-13/
      episode.wav
```

With metadata:
- `show-name`: Podcast show name
- `episode-date`: Episode date
- `content-type`: "podcast-episode"
- `generated-by`: "the-data-packet"

## Example Script

See [`examples/simple_usage.py`](../examples/simple_usage.py) for complete working examples.