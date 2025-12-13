Testing
=======

The Data Packet includes a comprehensive testing suite to ensure reliability and maintainability.

Test Structure
--------------

The test suite is organized into several modules, each focusing on a specific component:

- ``test_models.py``: Tests for the ArticleData model
- ``test_clients.py``: Tests for HTTP and RSS clients  
- ``test_extractors.py``: Tests for content extraction logic
- ``test_scrapers.py``: Tests for the main scraper orchestration
- ``test_integration.py``: End-to-end integration tests
- ``test_cli.py``: Tests for the command-line interface

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
   hatch test
   
   # Run specific test file
   hatch run python -m unittest tests.test_models -v
   
   # Run with coverage
   hatch run test-cov

Using Python Directly
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   python -m unittest discover tests -v
   
   # Run specific test
   python -m unittest tests.test_models.TestArticleData.test_initialization -v

Test Coverage
-------------

The test suite achieves comprehensive coverage:

- **86 Total Tests**: Covering all major functionality
- **Models**: 12 tests covering data validation and serialization
- **Clients**: 17 tests covering HTTP/RSS operations and error handling
- **Extractors**: 18 tests covering content parsing with various inputs
- **Scrapers**: 20 tests covering orchestration and batch operations  
- **Integration**: 6 tests covering end-to-end workflows
- **CLI**: 15 tests covering command parsing and output formatting

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