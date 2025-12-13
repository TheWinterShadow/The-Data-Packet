# The Data Packet

A Python package for scraping and extracting article data from Wired.com, with support for Docker containerization.

## Features

- **RSS Feed Integration**: Automatically fetch the latest article URLs from Wired.com RSS feeds
- **Content Extraction**: Extract article titles, authors, and content with intelligent filtering
- **Multiple Categories**: Support for security and guide article categories
- **Batch Processing**: Scrape multiple articles in a single operation
- **CLI Interface**: Command-line tool for easy integration into workflows
- **Docker Ready**: Pre-built Docker configuration for containerized deployment
- **Comprehensive Testing**: Full test suite with >95% coverage
- **Type Hints**: Complete type annotations for better IDE support

## Installation

### From Source

```bash
git clone https://github.com/TheWinterShadow/the_data_packet.git
cd the_data_packet
pip install .
```

### Development Installation

```bash
git clone https://github.com/TheWinterShadow/the_data_packet.git
cd the_data_packet
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from the_data_packet import WiredArticleScraper

# Initialize the scraper
scraper = WiredArticleScraper()

# Get the latest security article
security_article = scraper.get_latest_security_article()
print(f"Title: {security_article.title}")
print(f"Author: {security_article.author}")
print(f"Content: {security_article.content[:200]}...")

# Get both latest articles
articles = scraper.get_both_latest_articles()
for category, article in articles.items():
    print(f"{category}: {article.title}")

# Get multiple articles
security_articles = scraper.get_multiple_articles("security", limit=5)
for article in security_articles:
    print(f"- {article.title}")

# Clean up
scraper.close()
```

### Command Line Interface

The package includes a CLI tool accessible via the `wired-scraper` command:

```bash
# Get latest security article
wired-scraper security

# Get latest guide article  
wired-scraper guide

# Get both latest articles
wired-scraper both

# Get multiple articles
wired-scraper security --count 5

# Scrape a specific URL
wired-scraper --url "https://www.wired.com/story/example-article/"

# Output as text instead of JSON
wired-scraper security --format text

# Enable verbose logging
wired-scraper security --verbose
```

### Docker Usage

Build and run the Docker container:

```bash
# Build the image
docker build -t wired-scraper .

# Run the container (outputs to ./output directory)
docker run -v $(pwd)/output:/app/output wired-scraper

# Run with custom command
docker run -v $(pwd)/output:/app/output wired-scraper python -m the_data_packet.cli security --format text

# Interactive mode
docker run -it wired-scraper bash
```

## API Reference

### WiredArticleScraper

Main scraper class for extracting articles from Wired.com.

```python
class WiredArticleScraper:
    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None)
    def get_latest_article(self, category: str) -> ArticleData
    def get_latest_security_article(self) -> ArticleData  
    def get_latest_guide_article(self) -> ArticleData
    def get_both_latest_articles(self) -> Dict[str, ArticleData]
    def get_multiple_articles(self, category: str, limit: int = 5) -> List[ArticleData]
    def scrape_article_from_url(self, url: str, category: Optional[str] = None) -> ArticleData
    def close(self)
```

### ArticleData

Data model for article information.

```python
@dataclass
class ArticleData:
    title: Optional[str] = None
    author: Optional[str] = None  
    content: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    
    def is_valid(self) -> bool
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> "ArticleData"
```

## Package Structure

```
the_data_packet/
├── __init__.py          # Main package exports
├── __about__.py         # Version information  
├── cli.py              # Command-line interface
├── clients/            # HTTP and RSS clients
│   ├── __init__.py
│   ├── http_client.py  # HTTP request handling
│   └── rss_client.py   # RSS feed parsing
├── extractors/         # Content extraction
│   ├── __init__.py
│   └── wired_extractor.py  # Wired.com content extractor
├── models/             # Data models
│   ├── __init__.py
│   └── article.py      # ArticleData model
└── scrapers/           # Main scraper logic
    ├── __init__.py
    └── wired_scraper.py    # WiredArticleScraper class
```

## Configuration

The package uses sensible defaults but can be configured:

```python
# Custom timeout and User-Agent
scraper = WiredArticleScraper(
    timeout=60,
    user_agent="MyBot/1.0"
)

# Access individual components
from the_data_packet.clients import RSSClient, HTTPClient
from the_data_packet.extractors import WiredContentExtractor

rss_client = RSSClient()
http_client = HTTPClient(timeout=30)
extractor = WiredContentExtractor()
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=the_data_packet --cov-report=html

# Run specific test file
pytest tests/test_models.py -v
```

### Code Quality

```bash
# Format code
black the_data_packet/ tests/

# Sort imports
isort the_data_packet/ tests/

# Lint code  
flake8 the_data_packet/ tests/

# Type checking
mypy the_data_packet/

# Security scan
bandit -r the_data_packet/
```

## Error Handling

The package includes comprehensive error handling:

```python
from the_data_packet import WiredArticleScraper
from the_data_packet.models import ArticleData

scraper = WiredArticleScraper()

try:
    article = scraper.get_latest_security_article()
    if not article.is_valid():
        print("Warning: Article data may be incomplete")
except RuntimeError as e:
    print(f"Scraping failed: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
finally:
    scraper.close()
```

## Logging

Configure logging to monitor scraping operations:

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

scraper = WiredArticleScraper()
# Now all operations will be logged
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run code quality checks (`black`, `isort`, `flake8`, `mypy`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0

- Initial release
- Support for security and guide article categories
- Full CLI interface
- Docker containerization
- Comprehensive test suite
- Complete type annotations
