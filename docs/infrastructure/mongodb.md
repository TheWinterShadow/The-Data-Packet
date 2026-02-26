---
title: MongoDB
description: Episode tracking and article deduplication with MongoDB — local setup, connection details, and data schema.
icon: simple/mongodb
---

# MongoDB

MongoDB is an **optional** integration that prevents article reuse across episodes and
maintains a full audit trail of podcast generation history. If credentials are absent,
the pipeline runs normally and deduplication is simply skipped.

---

## What MongoDB stores

<div class="grid cards" markdown>

-   :material-newspaper-check: **Articles collection**

    ---

    Tracks every article URL that has been used in a past episode.

    When the pipeline runs, it checks this collection and excludes any articles
    already seen — ensuring every episode has fresh, unique content.

-   :material-history: **Episodes collection**

    ---

    Records metadata for every generated episode: execution time, success status,
    article count, output file paths, and S3 URLs.

    Provides a complete audit trail and generation history.

</div>

---

## Local setup (Docker)

The included `mongodb.sh` script manages a local MongoDB container for development and testing.

```bash title="Start MongoDB"
./mongodb.sh start
```

```bash title="Other commands"
./mongodb.sh status   # Check if running
./mongodb.sh shell    # Open MongoDB shell
./mongodb.sh logs     # View container logs
./mongodb.sh stop     # Stop the container
./mongodb.sh remove   # Stop + remove container and data volume
```

---

## Connection details

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `27017` |
| Username | `admin` |
| Password | Set in `mongodb.sh` (default: `password123`) |
| Database | `the_data_packet` |

**Connection URL:**

```
mongodb://admin:password123@localhost:27017/the_data_packet?authSource=admin
```

!!! warning "Change the default password"

    The default password in `mongodb.sh` is for local development only.
    Always set a strong password in any environment beyond your own machine.

---

## Configuration

Set these environment variables to enable MongoDB integration:

```bash
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your-password
MONGODB_HOST=localhost      # default
MONGODB_PORT=27017          # default
MONGODB_DATABASE=the_data_packet  # default
```

Or pass them to Docker:

```bash
docker run --rm --env-file .env \
  -e MONGODB_USERNAME=admin \
  -e MONGODB_PASSWORD=your-password \
  -v "$(pwd)/output:/app/output" \
  ghcr.io/thewintershadow/the-data-packet:latest
```

---

## Inspecting stored data

=== ":fontawesome-brands-python: Python"

    ```python
    from pymongo import MongoClient

    client = MongoClient(
        "mongodb://admin:password123@localhost:27017/the_data_packet?authSource=admin"
    )
    db = client.the_data_packet

    # Articles used across all episodes
    articles = list(db.articles.find())
    print(f"Total articles tracked: {len(articles)}")

    # Episode history
    episodes = list(db.episodes.find())
    print(f"Total episodes generated: {len(episodes)}")

    # Most recent episode
    latest = db.episodes.find_one(sort=[("_id", -1)])
    print(f"Last run: {latest['execution_time_seconds']:.1f}s — success={latest['success']}")
    ```

=== ":simple-mongodb: MongoDB Shell"

    ```javascript
    // Open with: ./mongodb.sh shell

    use the_data_packet

    // Show collections
    show collections

    // Count documents
    db.articles.countDocuments()
    db.episodes.countDocuments()

    // Recent episodes (newest first)
    db.episodes.find().sort({ _id: -1 }).limit(5)

    // Articles from a specific source
    db.articles.find({ source: "techcrunch" })
    ```

---

## Data schema

=== "Articles"

    | Field | Type | Description |
    |---|---|---|
    | `url` | `string` | Article URL (unique index) |
    | `title` | `string` | Article title |
    | `source` | `string` | Source name (`wired`, `techcrunch`) |
    | `published_date` | `datetime` | Publication date |
    | `used_at` | `datetime` | When it was added to an episode |

=== "Episodes"

    | Field | Type | Description |
    |---|---|---|
    | `success` | `bool` | Whether the run completed successfully |
    | `number_of_articles` | `int` | Articles used |
    | `script_path` | `string` | Local path to script file |
    | `audio_path` | `string` | Local path to audio file |
    | `s3_audio_url` | `string` | Public S3 URL (if uploaded) |
    | `execution_time_seconds` | `float` | Wall-clock run time |
    | `error_message` | `string` | Error details if `success` is `false` |
    | `created_at` | `datetime` | Episode generation timestamp |

---

## Production setup

For production, use a managed MongoDB service rather than the local Docker script:

- [MongoDB Atlas](https://www.mongodb.com/atlas) — fully managed, free tier available
- [Amazon DocumentDB](https://aws.amazon.com/documentdb/) — MongoDB-compatible, AWS-native
- Self-hosted MongoDB with replica set for high availability

Set `MONGODB_HOST` to your managed instance hostname and provide the credentials via
environment variables or a secrets manager.

!!! tip "Use Atlas free tier for simple deployments"

    MongoDB Atlas M0 (free tier) is sufficient for most podcast generation workloads.
    It provides 512 MB of storage, which easily holds thousands of episode records.
