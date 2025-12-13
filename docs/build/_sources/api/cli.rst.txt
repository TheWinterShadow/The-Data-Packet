Command Line Interface
======================

The CLI module provides a command-line interface for interacting with the scraper functionality.

Main Functions
--------------

.. autofunction:: the_data_packet.cli.main

   The main entry point for the command-line interface. This function handles argument
   parsing, logging setup, and orchestrates the scraping operations based on user input.

.. autofunction:: the_data_packet.cli.format_article_output

   Formats article data for output in either JSON or human-readable text format.

.. autofunction:: the_data_packet.cli.setup_logging

   Configures logging for the CLI application with optional verbose output.

CLI Usage Examples
------------------

Basic Commands
~~~~~~~~~~~~~~

Get the latest security article:

.. code-block:: bash

   wired-scraper security

Get the latest guide article:

.. code-block:: bash

   wired-scraper guide

Get both latest articles:

.. code-block:: bash

   wired-scraper both

Advanced Options
~~~~~~~~~~~~~~~~

Get multiple articles from a category:

.. code-block:: bash

   wired-scraper security --count 5

Output in text format instead of JSON:

.. code-block:: bash

   wired-scraper security --format text

Scrape a specific article URL:

.. code-block:: bash

   wired-scraper --url "https://www.wired.com/story/example-article/"

Enable verbose logging:

.. code-block:: bash

   wired-scraper security --verbose

Command-Line Arguments
----------------------

Positional Arguments
~~~~~~~~~~~~~~~~~~~~

- ``category``: Article category to fetch (choices: security, guide, both)
  
  - **security**: Latest cybersecurity and privacy articles
  - **guide**: Latest how-to guides and tutorials  
  - **both**: Both latest security and guide articles

Optional Arguments
~~~~~~~~~~~~~~~~~~

- ``--url URL``: Specific article URL to scrape (cannot be used with category)
- ``--count COUNT``: Number of articles to fetch (default: 1, max: 10)
- ``--format FORMAT``: Output format (choices: json, text; default: json)
- ``--verbose, -v``: Enable verbose logging output
- ``--help, -h``: Show help message and exit

Output Formats
--------------

JSON Format (Default)
~~~~~~~~~~~~~~~~~~~~~~

The default JSON format provides structured data that can be easily parsed:

.. code-block:: json

   {
     "title": "Example Article Title",
     "author": "Jane Doe", 
     "content": "Article content here...",
     "url": "https://www.wired.com/story/example/",
     "category": "security",
     "published_date": "2024-01-15T10:30:00Z"
   }

Text Format
~~~~~~~~~~~

The text format provides human-readable output:

.. code-block:: text

   Title: Example Article Title
   Author: Jane Doe
   Category: security
   URL: https://www.wired.com/story/example/
   Content Length: 1,234 characters

   Content:
   --------------------------------------------------
   Article content here...

Error Handling
--------------

The CLI provides comprehensive error handling:

- **Network Errors**: Graceful handling of connection issues
- **Invalid URLs**: Clear error messages for malformed URLs
- **Rate Limiting**: Automatic retries with backoff
- **Invalid Arguments**: Helpful usage messages
- **Keyboard Interrupts**: Clean shutdown on Ctrl+C

Exit Codes
~~~~~~~~~~

- **0**: Success
- **1**: Error occurred during execution
- **2**: Invalid command-line arguments

Module Reference
----------------

.. automodule:: the_data_packet.cli
   :members:
   :undoc-members:
   :show-inheritance: