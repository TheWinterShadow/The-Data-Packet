# RSS Feed Management

This document describes the RSS feed management functionality for The Data Packet podcast.

## Overview

The RSS feed management system automatically updates an RSS feed whenever new podcast episodes are uploaded to S3. The system includes:

- **RSS Generation**: Creates podcast-compliant RSS feeds with iTunes tags
- **Episode Management**: Generates episodes from article collections
- **S3 Integration**: Uploads and manages RSS feeds in S3 storage
- **Feed Updates**: Maintains episode history and limits feed size

## Components

### RSSGenerator Class

Located in `the_data_packet/generation/rss.py`, this class handles all RSS operations:

- `generate_episode_from_articles()`: Creates podcast episodes from article collections
- `generate_rss_feed()`: Creates complete RSS XML with channel metadata
- `update_rss_feed()`: Updates existing feed with new episodes
- `load_existing_feed()`: Parses existing RSS to extract episodes

### Integration with Podcast Pipeline

The RSS functionality is integrated into the main podcast workflow (`the_data_packet/workflows/podcast.py`):

1. After audio is generated and uploaded to S3
2. RSS generator creates an episode from the source articles
3. Existing RSS feed is downloaded from S3 (if exists)
4. New episode is added to the feed
5. Updated RSS feed is uploaded back to S3

## Configuration

RSS settings can be configured via environment variables or in the Config class:

```bash
# RSS Feed Configuration
RSS_CHANNEL_TITLE="My Podcast"
RSS_CHANNEL_DESCRIPTION="Description of my podcast"
RSS_CHANNEL_LINK="https://example.com"
RSS_CHANNEL_IMAGE_URL="https://example.com/logo.jpg"
MAX_RSS_EPISODES=50
GENERATE_RSS=true
```

## Usage with Hatch

The project is fully configured to work with Hatch. Common commands:

```bash
# Run code formatting
hatch run format

# Check code quality
hatch run check

# Run tests
hatch run test

# Build the project
hatch build

# Run type checking
hatch run typecheck
```

## RSS Feed Structure

The generated RSS feeds include:

- Standard RSS 2.0 elements
- iTunes podcast tags for Apple Podcasts compatibility
- Episode metadata (duration, file size, etc.)
- Proper GUID generation for episode tracking
- Technology category classification

## S3 Storage

RSS feeds are stored in S3 with the key pattern:
```
{show-name-lowercase}/feed.xml
```

The feed is publicly accessible for podcast clients to consume.

## Episode Limit

To prevent RSS feeds from becoming too large, the system maintains only the most recent N episodes (configurable via `MAX_RSS_EPISODES`, default: 50).