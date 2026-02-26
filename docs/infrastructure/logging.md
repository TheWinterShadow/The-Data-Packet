---
title: Logging
description: Structured JSONL logging with S3 archival, Grafana Loki forwarding, and log analysis patterns.
icon: material/text-box-search-outline
---

# Logging

The Data Packet uses structured JSONL logging: machine-readable entries written to daily
files, with optional S3 archival and optional Grafana Loki forwarding.

---

## Log format

Each entry is a JSON object on its own line (JSONL):

```json
{
  "timestamp": "2025-12-27T14:35:02.566269",
  "level": "INFO",
  "logger": "the_data_packet.sources.techcrunch",
  "message": "Collected 5 new articles",
  "module": "techcrunch",
  "function": "collect_articles",
  "line": 123,
  "articles_found": 5,
  "source": "techcrunch",
  "collection_time": 1.2
}
```

Standard fields: `timestamp` · `level` · `logger` · `message` · `module` · `function` · `line`

Any `extra={}` kwargs in a log call become additional top-level JSON fields.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` |
| `LOG_DIRECTORY` | `output/logs` | Directory for JSONL files |
| `ENABLE_JSONL_LOGGING` | `true` | Write JSONL files |
| `ENABLE_S3_LOG_UPLOAD` | `true` | Upload completed daily files to S3 |
| `LOG_UPLOAD_INTERVAL` | `3600` | Seconds between upload checks |
| `REMOVE_LOGS_AFTER_UPLOAD` | `false` | Delete local files after upload |

---

## S3 upload structure

Log files are uploaded with a date-partitioned prefix — compatible with AWS Athena and
other partition-aware tools:

```
logs/
└── 2025/
    └── 12/
        └── 27/
            └── the-data-packet-2025-12-27.jsonl
```

---

## Python usage

=== "Basic"

    ```python
    from the_data_packet.core.logging import setup_logging, get_logger

    setup_logging()
    logger = get_logger(__name__)

    logger.info("Pipeline started")
    logger.warning("Config missing, using default")
    logger.error("API call failed")
    ```

=== "Structured extra fields"

    ```python
    logger.info("Articles collected", extra={
        "source": "techcrunch",
        "count": 3,
        "collection_time_ms": 450,
    })

    # Fields appear as top-level keys in the JSONL entry
    ```

=== "Exception context"

    ```python
    try:
        result = api_call()
    except Exception:
        logger.error("API call failed", exc_info=True, extra={
            "endpoint": "https://api.example.com",
            "retry_count": 3,
        })
    ```

=== "Custom setup"

    ```python
    # Console only (no JSONL files)
    setup_logging(enable_jsonl=False)

    # Disable S3 upload
    setup_logging(enable_s3_upload=False)

    # Full custom
    setup_logging(
        log_level="DEBUG",
        enable_jsonl=True,
        enable_s3_upload=False,
        log_dir="logs/debug",
    )
    ```

=== "Graceful shutdown"

    ```python
    from the_data_packet.core.logging import upload_current_logs, stop_s3_uploader
    import atexit

    setup_logging()
    atexit.register(stop_s3_uploader)  # uploads on exit

    # Or force upload immediately
    upload_current_logs()
    ```

---

## Log analysis

=== ":material-bash: jq"

    ```bash
    # Count entries by level
    jq -r '.level' logs.jsonl | sort | uniq -c

    # All errors
    jq -r 'select(.level=="ERROR") | .message' logs.jsonl

    # Slow operations (> 5 seconds)
    jq 'select(.processing_time > 5)' logs.jsonl

    # Filter by module
    jq 'select(.logger | contains("techcrunch"))' logs.jsonl
    ```

=== ":fontawesome-brands-python: Python"

    ```python
    import json
    from pathlib import Path

    logs = [
        json.loads(line)
        for line in Path("the-data-packet-2025-12-27.jsonl").read_text().splitlines()
    ]

    from collections import Counter
    print(Counter(log["level"] for log in logs))

    slow = [log for log in logs if log.get("processing_time", 0) > 5]
    ```

---

## Grafana Loki

Configure these variables to forward all log entries to Loki:

```bash
GRAFANA_LOKI_URL=https://loki.your-instance.com
GRAFANA_LOKI_USERNAME=your-username
GRAFANA_LOKI_PASSWORD=your-password
```

All structured `extra` fields are forwarded as Loki labels, enabling LogQL queries like:

```logql
{app="the-data-packet", level="ERROR"} | json | processing_time > 5
```

---

## Best practices

!!! tip "Always use structured logging"

    Pass extra context as `extra={}` kwargs rather than interpolating into message strings.
    This makes fields queryable and preserves clean message text.

    ```python
    # Good
    logger.info("Article processed", extra={
        "article_id": "123",
        "processing_time": 1.5,
        "word_count": 850,
    })

    # Avoid
    logger.info(f"Article 123 processed in 1.5s with 850 words")
    ```

!!! tip "Include timing data"

    Adding `processing_time` or `duration_ms` to log entries makes it trivial to identify
    performance regressions in production without any additional instrumentation.
