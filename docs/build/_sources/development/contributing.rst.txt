Contributing
============

We welcome contributions to The Data Packet! This guide will help you get started with contributing to the project.

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.9 or higher
- Git
- Hatch (recommended for dependency management)

Installation
~~~~~~~~~~~~

1. **Fork and Clone the Repository**

   .. code-block:: bash

      git clone https://github.com/YourUsername/The-Data-Packet.git
      cd The-Data-Packet

2. **Install Hatch** (if not already installed)

   .. code-block:: bash

      pip install hatch

3. **Create Development Environment**

   .. code-block:: bash

      hatch env create dev

4. **Install Pre-commit Hooks** (optional but recommended)

   .. code-block:: bash

      hatch run dev:pre-commit install

Development Workflow
--------------------

Code Quality
~~~~~~~~~~~~

The project maintains high code quality standards:

.. code-block:: bash

   # Run all quality checks
   hatch run dev:python -m black the_data_packet tests
   hatch run dev:python -m isort the_data_packet tests  
   hatch run dev:python -m mypy --exclude 'docs' the_data_packet

Testing
~~~~~~~

.. code-block:: bash

   # Run all tests
   hatch test
   
   # Run with coverage
   hatch run test-cov
   
   # Run specific test file
   hatch run dev:python -m unittest tests.test_models -v

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Build documentation
   hatch run dev:docs
   
   # Serve documentation locally
   hatch run dev:docs-serve

Complete Build Pipeline
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run the full build pipeline (code quality, tests, docs, packaging)
   bb  # This is an alias for the complete build process

Making Changes
--------------

Code Style Guidelines
~~~~~~~~~~~~~~~~~~~~~

- **PEP 8 Compliance**: Code must follow PEP 8 style guidelines
- **Type Hints**: All public APIs must have complete type annotations
- **Docstrings**: All public classes and methods must have comprehensive docstrings
- **Import Sorting**: Use isort for consistent import organization

Example Function:

.. code-block:: python

   def extract_article_data(soup: BeautifulSoup, url: str) -> ArticleData:
       """
       Extract article data from a BeautifulSoup object.
       
       Args:
           soup: Parsed HTML content
           url: The article URL
           
       Returns:
           ArticleData object with extracted information
           
       Raises:
           ValueError: If the HTML structure is invalid
           RuntimeError: If extraction fails
       """
       # Implementation here

Testing Requirements
~~~~~~~~~~~~~~~~~~~~

- **New Features**: Must include comprehensive tests
- **Bug Fixes**: Must include regression tests  
- **Coverage**: Maintain or improve test coverage
- **Documentation**: Update documentation for API changes

Commit Guidelines
~~~~~~~~~~~~~~~~~

Use clear, descriptive commit messages:

.. code-block:: text

   feat: add support for extracting article publication dates
   
   - Parse publication dates from meta tags and JSON-LD
   - Add date validation and formatting
   - Include tests for various date formats
   
   Fixes #123

Types of Contributions
----------------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, please include:

- **Clear Description**: What happened vs what you expected
- **Reproduction Steps**: Minimal example to reproduce the issue  
- **Environment**: Python version, OS, package version
- **Error Messages**: Full traceback if applicable

Feature Requests
~~~~~~~~~~~~~~~~

For new features:

- **Use Case**: Describe the problem this solves
- **Proposed Solution**: How you envision it working
- **Alternatives**: Other approaches you considered
- **Breaking Changes**: Whether this affects existing APIs

Code Contributions
~~~~~~~~~~~~~~~~~~

1. **Check Issues**: Look for existing issues or create a new one
2. **Create Branch**: Use descriptive branch names (``feature/add-date-parsing``)
3. **Write Tests**: Include comprehensive tests for your changes
4. **Update Documentation**: Add or update relevant documentation
5. **Submit PR**: Create a pull request with detailed description

Pull Request Process
--------------------

PR Requirements
~~~~~~~~~~~~~~~

Before submitting a pull request:

- [ ] Tests pass locally (``hatch test``)
- [ ] Code follows style guidelines (``black``, ``isort``, ``mypy``)
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes

Review Process
~~~~~~~~~~~~~~

1. **Automated Checks**: CI pipeline runs tests and quality checks
2. **Code Review**: Maintainers review the code for quality and design
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, maintainers will merge the PR

Release Process
---------------

The project follows semantic versioning (SemVer):

- **Major**: Breaking changes to public APIs
- **Minor**: New features without breaking changes  
- **Patch**: Bug fixes and internal improvements

Project Structure
-----------------

.. code-block:: text

   The-Data-Packet/
   ├── the_data_packet/          # Main package source code
   │   ├── __init__.py           # Package initialization and public API
   │   ├── models/               # Data models
   │   ├── clients/              # HTTP and RSS clients
   │   ├── extractors/           # Content extraction logic
   │   ├── scrapers/             # Main scraper orchestration
   │   └── cli.py                # Command-line interface
   ├── tests/                    # Test suite
   │   ├── test_*.py             # Test modules
   │   └── conftest.py           # Shared test configuration
   ├── docs/                     # Documentation
   │   └── source/               # Sphinx documentation source
   ├── pyproject.toml            # Project configuration
   └── README.md                 # Project overview

Key Files
~~~~~~~~~

- ``pyproject.toml``: Project metadata, dependencies, and tool configuration
- ``the_data_packet/__init__.py``: Public API exports  
- ``tests/conftest.py``: Shared test fixtures and configuration
- ``docs/source/conf.py``: Sphinx documentation configuration

Architecture Guidelines
------------------------

Design Principles
~~~~~~~~~~~~~~~~~

- **Single Responsibility**: Each class has a clear, focused purpose
- **Dependency Injection**: Components accept dependencies via constructor
- **Error Handling**: Graceful degradation with informative error messages
- **Resource Management**: Proper cleanup of network resources
- **Type Safety**: Complete type annotations for better maintainability

Component Boundaries
~~~~~~~~~~~~~~~~~~~~

- **Models**: Pure data containers with validation
- **Clients**: External service interactions (HTTP, RSS)
- **Extractors**: HTML parsing and content extraction
- **Scrapers**: High-level orchestration of components
- **CLI**: User interface and argument handling

Getting Help
------------

If you need help with development:

- **Documentation**: Check the API documentation first
- **Issues**: Search existing issues for similar questions
- **Discussions**: Use GitHub Discussions for general questions
- **Code Examples**: Look at the test suite for usage examples

Thank you for contributing to The Data Packet! 🎉