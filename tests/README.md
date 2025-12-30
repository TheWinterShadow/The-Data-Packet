# The Data Packet Test Suite

This directory contains comprehensive unit tests for The Data Packet project. The test suite is built using Python's `unittest` framework and provides extensive coverage of all modules and functionality.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── run_tests.py            # Test runner script
├── test___about__.py       # Tests for package metadata
├── test___init__.py        # Tests for main package
├── test_cli.py             # Tests for command-line interface
├── core/                   # Tests for core module
│   ├── test___init__.py    # Core module imports
│   ├── test_config.py      # Configuration management
│   ├── test_exceptions.py  # Exception hierarchy
│   └── test_logging.py     # Logging system
├── generation/             # Tests for content generation
│   ├── test___init__.py    # Generation module imports
│   ├── test_audio.py       # Google Cloud TTS audio generation
│   ├── test_rss.py         # RSS feed generation
│   └── test_script.py      # Claude AI script generation
├── sources/                # Tests for article collection
│   ├── test___init__.py    # Sources module imports
│   ├── test_base.py        # Base article and source classes
│   ├── test_techcrunch.py  # TechCrunch article collection
│   └── test_wired.py       # Wired article collection
├── utils/                  # Tests for utility modules
│   ├── test___init__.py    # Utils module imports
│   ├── test_http.py        # HTTP client functionality
│   └── test_s3.py          # AWS S3 storage integration
└── workflows/              # Tests for complete workflows
    ├── test___init__.py    # Workflows module imports
    └── test_podcast.py     # Complete podcast generation pipeline
```

## Running Tests

### Run All Tests

```bash
# From project root directory
python -m tests.run_tests

# With verbose output
python -m tests.run_tests --verbose

# With minimal output  
python -m tests.run_tests --quiet
```

### Run Specific Tests

```bash
# Run a specific test module
python -m unittest tests.test_cli

# Run a specific test class
python -m unittest tests.core.test_config.TestConfig

# Run a specific test method
python -m unittest tests.core.test_config.TestConfig.test_default_config_creation

# Run all tests in a directory
python -m unittest discover tests/core

# Run tests matching a pattern
python -m tests.run_tests --pattern "test_core*"
```

### Using pytest (Alternative)

If you prefer pytest, you can also run tests with:

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_cli.py

# Run tests with coverage
pip install pytest-cov
pytest --cov=the_data_packet tests/
```

## Test Coverage

The test suite covers the following areas:

### Package Structure Tests
- Package imports and exports
- Module initialization
- Version information and metadata

### Configuration Management Tests
- Environment variable loading
- Configuration validation
- Default value handling
- Override mechanisms
- Error conditions

### Exception Handling Tests
- Exception hierarchy correctness
- Custom exception behavior
- Error message formatting
- Exception inheritance

### Logging System Tests
- Log level configuration
- Third-party library noise reduction
- Logger instance creation
- Log formatting

### CLI Tests
- Argument parsing
- Command execution
- Error handling
- Configuration override
- Pipeline orchestration

### Generation Module Tests

#### Audio Generation (Google Cloud TTS)
- TTS client initialization
- Voice validation and SSML generation
- Script parsing for multi-speaker content
- Long Audio Synthesis workflow
- GCS integration and file management
- Error handling and retries

#### RSS Feed Generation
- Episode creation from articles
- RSS XML generation
- Feed validation
- S3 integration
- Episode numbering

#### Script Generation (Claude AI)
- API client initialization
- Article processing
- Script structure generation
- Content optimization for TTS
- Response parsing and validation

### Source Module Tests

#### Base Classes
- Article data validation
- ArticleSource abstract interface
- Category validation
- Content quality checks

#### Specific Sources
- TechCrunch RSS integration
- Wired RSS integration
- Article extraction
- Content cleaning

### Utility Module Tests

#### HTTP Client
- Request handling
- Error handling
- Session management
- BeautifulSoup integration

#### S3 Storage
- AWS client initialization
- File upload functionality
- Error handling
- Credential validation

### Workflow Tests

#### Podcast Pipeline
- Complete workflow orchestration
- Step-by-step execution
- Error recovery
- Result aggregation
- Configuration validation

## Test Features

### Mocking and Isolation
- Extensive use of `unittest.mock` for API isolation
- External service mocking (Google Cloud TTS, Claude, AWS)
- File system operation mocking
- Network request mocking

### Error Testing
- Network failure scenarios
- API rate limiting
- Invalid configuration
- Missing dependencies
- File system errors

### Edge Cases
- Empty inputs
- Malformed data
- Boundary conditions
- Resource limits

### Integration Testing
- Module interaction testing
- Configuration propagation
- Error bubbling
- Resource cleanup

## Writing New Tests

When adding new functionality, follow these guidelines for tests:

### Test File Naming
- Test files should match the source file: `test_<module_name>.py`
- Place tests in the same relative directory structure as source
- Use descriptive test method names: `test_<functionality>_<condition>`

### Test Structure
```python
import unittest
from unittest.mock import Mock, patch
from the_data_packet.module import ClassUnderTest

class TestClassUnderTest(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_config = Mock()
        # Initialize common test data
    
    def test_functionality_success_case(self):
        """Test successful execution of functionality."""
        # Arrange
        # Act  
        # Assert
    
    def test_functionality_error_case(self):
        """Test error handling in functionality."""
        # Arrange error conditions
        # Act and expect exception
        # Assert error message/type

if __name__ == '__main__':
    unittest.main()
```

### Mocking Guidelines
- Mock external dependencies (APIs, file system, network)
- Use `@patch` decorators for dependency injection
- Create realistic mock responses
- Test both success and failure scenarios

### Test Data
- Use realistic but minimal test data
- Create reusable test fixtures in `setUp()`
- Use descriptive variable names
- Keep test data in the test file unless shared

## Continuous Integration

The test suite is designed to run in CI/CD environments:

### GitHub Actions
```yaml
- name: Run tests
  run: |
    python -m pip install -e .
    python -m tests.run_tests
```

### Docker Testing
```bash
# Build test image
docker build -t the-data-packet-tests .

# Run tests in container
docker run --rm the-data-packet-tests python -m tests.run_tests
```

### Requirements
The test suite requires:
- Python 3.8+ 
- All project dependencies
- Internet connection for external API mocking validation
- Temporary directory access for file operations

### Environment Variables
Some tests may require environment variables for configuration testing:
- `ANTHROPIC_API_KEY` (can be mock value)
- `GCS_BUCKET_NAME` (can be mock value)
- `GOOGLE_CREDENTIALS_PATH` (can be mock path) 
- `AWS_ACCESS_KEY_ID` (can be mock value)
- `AWS_SECRET_ACCESS_KEY` (can be mock value)

## Test Results

Test output includes:
- Individual test results (pass/fail/error/skip)
- Execution time for each test
- Summary statistics
- Detailed failure/error information
- Exit code (0 for success, 1 for failure)

The test runner provides clear feedback and is designed for both local development and automated testing environments.