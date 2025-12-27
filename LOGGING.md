# Enhanced JSONL Logging with S3 Upload

This document describes the enhanced logging system that writes structured JSON logs to `.jsonl` files and automatically uploads them to S3.

## Features

- **Structured JSONL Logging**: All log entries are written as JSON lines to daily log files
- **Automatic S3 Upload**: Completed daily log files are automatically uploaded to S3
- **Rich Metadata**: Each log entry includes timestamp, module, function, line number, and custom fields
- **Background Processing**: S3 uploads happen in a background thread without blocking the application
- **Configurable**: All aspects can be configured via environment variables or code
- **Thread-Safe**: Safe for use in multi-threaded applications

## Quick Start

```python
from the_data_packet.core.logging import setup_logging, get_logger

# Setup logging with default settings
setup_logging()

# Get a logger for your module
logger = get_logger(__name__)

# Basic logging
logger.info("Application started")
logger.warning("Configuration missing, using defaults")
logger.error("Failed to connect to database")

# Structured logging with metadata
logger.info("User action completed", extra={
    "user_id": "user123",
    "action": "article_read",
    "processing_time": 1.23,
    "metadata": {"source": "mobile_app"}
})
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_DIRECTORY` | Directory for JSONL log files | `output/logs` |
| `ENABLE_JSONL_LOGGING` | Enable JSONL file logging | `true` |
| `ENABLE_S3_LOG_UPLOAD` | Enable S3 upload of logs | `true` |
| `LOG_UPLOAD_INTERVAL` | Upload interval in seconds | `3600` |
| `REMOVE_LOGS_AFTER_UPLOAD` | Remove local logs after S3 upload | `false` |

### Code Configuration

```python
# Disable JSONL logging (console only)
setup_logging(enable_jsonl=False)

# Custom log directory
setup_logging(log_dir="custom/log/path")

# Disable S3 upload
setup_logging(enable_s3_upload=False)

# Custom configuration
setup_logging(
    log_level="DEBUG",
    enable_jsonl=True,
    enable_s3_upload=False,
    log_dir="logs/debug"
)
```

## Log File Format

Each log entry is a single JSON object on its own line (JSONL format):

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

### Standard Fields

- `timestamp`: ISO format timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger`: Logger name (typically module name)
- `message`: Log message
- `module`: Python module name
- `function`: Function name where log was called
- `line`: Line number where log was called

### Custom Fields

Any additional data passed via the `extra` parameter in logging calls will be included as additional JSON fields.

## S3 Upload

### Setup

Ensure your AWS credentials and S3 bucket are configured:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export S3_BUCKET_NAME="your-log-bucket"
export AWS_REGION="us-east-1"
```

### Upload Structure

Log files are uploaded to S3 with the following structure:
```
logs/
├── 2025/
│   └── 12/
│       └── 27/
│           └── the-data-packet-2025-12-27.jsonl
└── 2025/
    └── 12/
        └── 26/
            └── the-data-packet-2025-12-26.jsonl
```

### Manual Upload

```python
from the_data_packet.core.logging import upload_current_logs

# Force upload of completed log files
upload_current_logs()
```

### Cleanup

```python
from the_data_packet.core.logging import stop_s3_uploader

# Gracefully stop the S3 upload service
stop_s3_uploader()
```

## Best Practices

### 1. Use Structured Logging

```python
# Good: Structured data
logger.info("Article processed", extra={
    "article_id": "123",
    "processing_time": 1.5,
    "word_count": 850
})

# Avoid: String concatenation
logger.info(f"Article 123 processed in 1.5s with 850 words")
```

### 2. Use Appropriate Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning messages for recoverable issues
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical errors that may cause shutdown

### 3. Include Context

```python
logger.error("API request failed", extra={
    "api_endpoint": "https://api.example.com/data",
    "status_code": 500,
    "retry_count": 3,
    "error_details": str(error)
})
```

### 4. Exception Logging

```python
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True, extra={
        "operation": "data_processing",
        "input_size": len(data)
    })
```

## Log Analysis

JSONL format makes logs easy to analyze with standard tools:

### Command Line Tools

```bash
# Count log entries by level
grep -o '"level":"[^"]*"' logs.jsonl | sort | uniq -c

# Extract all error messages
jq -r 'select(.level=="ERROR") | .message' logs.jsonl

# Find logs from specific module
jq 'select(.logger | contains("techcrunch"))' logs.jsonl
```

### Python Analysis

```python
import json

with open('the-data-packet-2025-12-27.jsonl', 'r') as f:
    logs = [json.loads(line) for line in f]

# Count by level
from collections import Counter
levels = Counter(log['level'] for log in logs)
print(levels)

# Find slow operations
slow_ops = [log for log in logs 
           if 'processing_time' in log and log['processing_time'] > 5.0]
```

## Troubleshooting

### No Log Files Created

1. Check if JSONL logging is enabled: `ENABLE_JSONL_LOGGING=true`
2. Verify log directory permissions
3. Check for errors in console output

### S3 Upload Failures

1. Verify AWS credentials are configured
2. Check S3 bucket name and permissions
3. Ensure network connectivity to AWS
4. Review error messages in logs

### High Log Volume

1. Adjust log level to reduce verbosity
2. Consider shorter upload intervals
3. Enable log removal after upload: `REMOVE_LOGS_AFTER_UPLOAD=true`
4. Filter out noisy third-party library logs

## Integration Examples

### In Main Application

```python
from the_data_packet.core.logging import setup_logging, stop_s3_uploader
import atexit

def main():
    # Setup logging at application start
    setup_logging()
    
    # Ensure graceful shutdown
    atexit.register(stop_s3_uploader)
    
    # Your application code here
    run_application()

if __name__ == "__main__":
    main()
```

### In CLI Tools

```python
import click
from the_data_packet.core.logging import setup_logging, get_logger

@click.command()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--no-s3', is_flag=True, help='Disable S3 upload')
def cli_command(debug, no_s3):
    """CLI tool with enhanced logging."""
    setup_logging(
        log_level="DEBUG" if debug else "INFO",
        enable_s3_upload=not no_s3
    )
    
    logger = get_logger(__name__)
    logger.info("CLI command started", extra={
        "debug_mode": debug,
        "s3_enabled": not no_s3
    })
    
    # Your CLI logic here
```

This enhanced logging system provides comprehensive observability for The Data Packet application while maintaining performance and reliability.