# The Data Packet - Documentation

This directory contains comprehensive documentation for The Data Packet project.

## 📚 Documentation Index

### Quick Start Guides
- **[Usage Guide](USAGE.md)** - Complete usage instructions, CLI commands, and examples
- **[Docker Setup](DOCKER.md)** - Docker installation, configuration, and deployment
- **[MongoDB Configuration](MONGODB.md)** - Database setup and connection details

### Advanced Configuration  
- **[Enhanced Logging](LOGGING.md)** - JSONL logging with S3 upload capabilities

## 🚀 Quick Links

| Topic | File | Description |
|-------|------|-------------|
| Getting Started | [USAGE.md](USAGE.md) | Complete setup and usage instructions |
| Container Deployment | [DOCKER.md](DOCKER.md) | Docker build and deployment guide |
| Database Setup | [MONGODB.md](MONGODB.md) | MongoDB configuration and connection |
| Observability | [LOGGING.md](LOGGING.md) | Structured logging and S3 integration |

## 🏗️ Sphinx Documentation

For auto-generated API documentation and advanced topics:

### Building Documentation

```bash
# Build documentation
hatch run dev:docs

# Clean build (rebuild everything)  
hatch run dev:docs-clean

# Serve documentation locally on port 8000
hatch run dev:docs-serve
```

### Structure

- `source/` - Documentation source files
  - `conf.py` - Sphinx configuration
  - `index.rst` - Main documentation page
  - `installation.rst` - Installation instructions
  - `usage.rst` - Usage examples and CLI reference
  - `api.rst` - API documentation (auto-generated)
  - `development.rst` - Development and contributing guide
  - `_static/` - Static files (CSS, images, etc.)
  - `_templates/` - Custom Sphinx templates
- `build/` - Generated HTML documentation (gitignored)

### Viewing Documentation

After building, open `build/index.html` in your browser or use the serve command:

```bash
hatch run dev:docs-serve
```

Then visit http://localhost:8000

## 📝 Documentation Format

The documentation uses reStructuredText (.rst) format and supports:

- Code blocks with syntax highlighting
- Cross-references to API documentation  
- Intersphinx links to Python, boto3, and click documentation
- MyST parser for Markdown support

## Theme

Uses the [Furo](https://pradyunsg.me/furo/) theme for a modern, clean appearance.
