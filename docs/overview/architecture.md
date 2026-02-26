---
title: Architecture
description: Layer diagram, module reference, data flow, and external dependency map for The Data Packet.
icon: material/sitemap
---

# Architecture

The Data Packet is structured as a layered Python application. Each layer has a single
responsibility and communicates through well-defined interfaces.

---

## Layer diagram

``` mermaid
graph TB
    CLI["CLI Interface<br/><code>cli.py</code>"]
    WF["Workflows<br/>PodcastPipeline · PodcastResult"]
    SRC["Sources<br/>WiredSource · TechCrunchSource"]
    GEN["Generation<br/>ScriptGenerator · AudioGenerator · RSSGenerator"]
    UTIL["Utils<br/>HTTPClient · S3Storage · MongoDBClient · LokiClient"]
    CORE["Core<br/>Config · Exceptions · Logging"]

    CLI --> WF
    WF --> SRC
    WF --> GEN
    WF --> UTIL
    SRC --> UTIL
    GEN --> UTIL
    SRC --> CORE
    GEN --> CORE
    UTIL --> CORE
    WF --> CORE
```

---

## Module reference

### `core/` — Foundation services

| Module | Class / Function | Responsibility |
|---|---|---|
| `config.py` | `Config`, `get_config()` | Unified config from env vars + overrides |
| `exceptions.py` | `TheDataPacketError` and subclasses | Custom exception hierarchy |
| `logging.py` | `setup_logging()`, `get_logger()` | JSONL logging with S3 upload |

**Exception hierarchy:**

``` mermaid
graph TD
    Base["TheDataPacketError"]
    Base --> ConfigurationError
    Base --> NetworkError
    Base --> ScrapingError
    Base --> AIGenerationError
    Base --> AudioGenerationError
    Base --> ValidationError
```

---

### `sources/` — Article collection

| Module | Class | Responsibility |
|---|---|---|
| `base.py` | `Article`, `ArticleSource` | Dataclass and abstract base for all sources |
| `wired.py` | `WiredSource` | RSS-based scraping of Wired.com |
| `techcrunch.py` | `TechCrunchSource` | Article collection from TechCrunch |

`ArticleSource` is an abstract base class. Adding a new news source means subclassing it
and implementing `collect_articles()`. See [Contributing](../contributing/index.md) for a
step-by-step guide.

**Supported categories:**

=== "Wired"

    | Category | URL path |
    |---|---|
    | `security` | `/category/security/` |
    | `science` | `/category/science/` |
    | `ai` | `/category/artificial-intelligence/` |

=== "TechCrunch"

    | Category | URL path |
    |---|---|
    | `ai` | `/category/artificial-intelligence/` |
    | `security` | `/category/security/` |

---

### `generation/` — Content creation

| Module | Class | Responsibility |
|---|---|---|
| `script.py` | `ScriptGenerator` | Claude API → structured dialogue script |
| `audio.py` | `AudioGenerator` | Google Cloud TTS Long Audio → `.wav` |
| `rss.py` | `RSSGenerator` | RSS 2.0 feed XML generation |

**Script generation flow:**

``` mermaid
sequenceDiagram
    participant WF as PodcastPipeline
    participant SG as ScriptGenerator
    participant CL as Claude API

    WF->>SG: generate_script(articles)
    loop For each article
        SG->>CL: generate_segment(article)
        CL-->>SG: dialogue segment
    end
    SG->>CL: generate_framework(segments)
    CL-->>SG: intro + transitions + outro
    SG-->>WF: assembled script
```

**Audio generation flow:**

``` mermaid
sequenceDiagram
    participant WF as PodcastPipeline
    participant AG as AudioGenerator
    participant TTS as Google Cloud TTS
    participant GCS as Cloud Storage

    WF->>AG: generate_audio(script)
    AG->>TTS: synthesize_long_audio(script)
    TTS->>GCS: store intermediate audio
    TTS-->>AG: operation ID
    loop Poll until complete
        AG->>TTS: check status
    end
    AG->>GCS: download audio
    AG-->>WF: local .wav path
```

---

### `utils/` — Infrastructure clients

| Module | Class | Responsibility |
|---|---|---|
| `http.py` | `HTTPClient` | Requests with retry, timeout, user-agent |
| `s3.py` | `S3Storage` | Upload files to AWS S3, return public URLs |
| `mongodb.py` | `MongoDBClient` | Store episode records, check article IDs |
| `loki.py` | `LokiClient` | Forward log entries to Grafana Loki |

---

### `workflows/` — Pipeline orchestration

`PodcastPipeline.run()` sequence:

``` mermaid
flowchart TD
    A["Collect articles\nfrom sources"] --> B{MongoDB\nconfigured?}
    B -->|yes| C["Deduplicate\nagainst MongoDB"]
    B -->|no| D
    C --> D["Generate script\nScriptGenerator"]
    D --> E["Synthesize audio\nAudioGenerator"]
    E --> F["Generate RSS feed\nRSSGenerator"]
    F --> G{S3\nconfigured?}
    G -->|yes| H["Upload to S3\nS3Storage"]
    G -->|no| I
    H --> I["Record episode\nMongoDBClient"]
    I --> J["Return PodcastResult"]
```

**`PodcastResult` fields:**

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Whether the pipeline completed without error |
| `number_of_articles_collected` | `int` | Articles used in this episode |
| `script_path` | `Path \| None` | Local path to generated script |
| `audio_path` | `Path \| None` | Local path to generated audio |
| `rss_path` | `Path \| None` | Local path to RSS feed |
| `s3_script_url` | `str \| None` | Public S3 URL for the script |
| `s3_audio_url` | `str \| None` | Public S3 URL for the audio |
| `execution_time_seconds` | `float` | Wall-clock time for the run |
| `error_message` | `str \| None` | Error details if `success` is `False` |

---

## Configuration resolution

Config values resolve in this order (highest priority first):

```
1. get_config(keyword=value)    ← Python API direct override
2. CLI flag                     ← --show-name, --male-voice, etc.
3. Environment variable         ← SHOW_NAME, MALE_VOICE, etc.
4. Built-in default             ← hardcoded in Config dataclass
```

This means you can mix any combination: set required secrets in env vars,
override per-run settings with CLI flags, all without a config file.

---

## External dependencies

!!! tip "Graceful degradation"

    Optional integrations (MongoDB, S3, Grafana Loki) degrade silently if not configured.
    The core script + audio pipeline works with only `ANTHROPIC_API_KEY` and `GCS_BUCKET_NAME`.

| Integration | Required | Env var |
|---|---|---|
| Anthropic Claude API | **Yes** | `ANTHROPIC_API_KEY` |
| Google Cloud TTS | **Yes** | `GCS_BUCKET_NAME` + credentials |
| AWS S3 | No | `S3_BUCKET_NAME` |
| MongoDB | No | `MONGODB_USERNAME` + `MONGODB_PASSWORD` |
| Grafana Loki | No | `GRAFANA_LOKI_URL` |
