Testing
=======

The Data Packet includes a comprehensive testing suite to ensure reliability and maintainability.

Test Structure
--------------

The test suite is organized into several modules, each focusing on a specific component:

**Core Tests:**
- ``test_core/test_config.py``: Configuration management tests
- ``test_core/test_exceptions.py``: Exception handling tests
- ``test_core/test_logging.py``: Logging system tests

**Generation Tests:**
- ``test_generation/test_script.py``: AI script generation tests
- ``test_generation/test_audio.py``: TTS audio generation tests
- ``test_generation/test_rss.py``: RSS feed generation tests

**Sources Tests:**
- ``test_sources/test_base.py``: Base article source tests
- ``test_sources/test_wired.py``: Wired.com source tests  
- ``test_sources/test_techcrunch.py``: TechCrunch source tests

**Workflow Tests:**
- ``test_workflows/test_podcast.py``: End-to-end pipeline tests

**Utilities Tests:**
- ``test_utils/test_s3.py``: AWS S3 storage tests
- ``test_cli.py``: Command-line interface tests

Test Framework
--------------

The package uses Python's built-in ``unittest`` framework with the following patterns:

- **Test Classes**: Each component has a dedicated test class inheriting from ``unittest.TestCase``
- **Setup Methods**: ``setUp()`` methods create mock dependencies and test data
- **Mock Objects**: Extensive use of ``unittest.mock`` for isolating components
- **Assertions**: Standard unittest assertions (``assertEqual``, ``assertIn``, etc.)

Running Tests
-------------

Using Hatch (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests  
   pytest tests/ -v
   
   # Run specific test module
   pytest tests/test_core/ -v
   
   # Run with coverage
   pytest --cov=the_data_packet tests/

Using Python Directly
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   python -m unittest discover tests -v
   
   # Run specific test
   python -m unittest tests.test_core.test_config.TestConfig.test_initialization -v

Test Coverage
-------------

The test suite achieves comprehensive coverage:

- **231 Total Tests**: Covering all major functionality with 100% pass rate
- **Core**: 45+ tests covering configuration, exceptions, and logging
- **Generation**: 60+ tests covering AI script generation, TTS audio, and RSS feeds
- **Sources**: 50+ tests covering article collection from multiple news sources
- **Workflows**: 35+ tests covering end-to-end pipeline orchestration
- **Utilities**: 25+ tests covering S3 storage and HTTP handling
- **CLI**: 15+ tests covering command-line interface and argument parsing

Key Testing Patterns
---------------------

Mock Usage
~~~~~~~~~~

Tests extensively use mocking to isolate components:

.. code-block:: python

   def setUp(self):
       self.scraper = WiredArticleScraper()
       self.scraper.rss_client = Mock()
       self.scraper.http_client = Mock()
       self.scraper.extractor = Mock()
       
       # Configure mock returns
       self.scraper.rss_client.get_latest_article_url.return_value = "https://example.com"
       self.scraper.extractor.extract.return_value = self.sample_article_data

Error Testing
~~~~~~~~~~~~~

Error conditions are thoroughly tested:

.. code-block:: python

   def test_http_error_handling(self):
       self.client.session.get.side_effect = requests.exceptions.Timeout()
       
       with self.assertRaises(RuntimeError) as cm:
           self.client.get_page("https://example.com")
       
       self.assertIn("timeout", str(cm.exception).lower())

Sample Data
~~~~~~~~~~~

Shared test data is defined in ``conftest.py``:

.. code-block:: python

   SAMPLE_ARTICLE_HTML = """
   <!DOCTYPE html>
   <html>
   <head><title>Test Article | WIRED</title></head>
   <body>
       <article><p>Test content</p></article>
   </body>
   </html>
   """

Test Categories
---------------

Unit Tests
~~~~~~~~~~

- **Models**: Data validation, serialization, edge cases
- **Clients**: HTTP requests, RSS parsing, timeout handling  
- **Extractors**: HTML parsing, fallback methods, malformed content
- **Individual Methods**: Each public method has dedicated tests

Integration Tests  
~~~~~~~~~~~~~~~~~

- **End-to-End Flows**: Complete scraping workflows
- **Component Integration**: How modules work together
- **Real-world Scenarios**: Handling actual webpage structures

CLI Tests
~~~~~~~~~

- **Argument Parsing**: Valid and invalid command combinations
- **Output Formatting**: JSON and text output verification
- **Error Handling**: Network errors, invalid URLs
- **Process Management**: Signal handling, exit codes

Best Practices
--------------

Writing New Tests
~~~~~~~~~~~~~~~~~

When adding new functionality:

1. **Create Test First**: Write tests before implementation (TDD)
2. **Use Descriptive Names**: Test method names should describe the scenario
3. **Test Edge Cases**: Include error conditions and boundary values  
4. **Mock External Dependencies**: Isolate the code under test
5. **Verify All Paths**: Test both success and failure scenarios

Example Test Structure:

.. code-block:: python

   class TestNewFeature(unittest.TestCase):
       def setUp(self):
           """Set up test fixtures."""
           # Create mocks and test data
           
       def test_successful_operation(self):
           """Test normal operation with valid input."""
           # Arrange, Act, Assert
           
       def test_error_handling(self):
           """Test error handling with invalid input."""
           # Test exception scenarios
           
       def test_edge_cases(self):
           """Test boundary conditions."""
           # Test limits and edge cases

Continuous Integration
----------------------

Tests are automatically run on:

- **Pre-commit**: Before code commits
- **Pull Requests**: Before merging changes  
- **Release Builds**: Before creating packages

The CI pipeline includes:

- **Type Checking**: mypy validation
- **Code Formatting**: black and isort verification
- **Test Execution**: Full test suite
- **Coverage Reporting**: Minimum coverage thresholds