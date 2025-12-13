The Data Packet Documentation
===============================

Welcome to The Data Packet's documentation!

**The Data Packet** is a Python package for scraping and extracting article data from Wired.com. It provides a clean, object-oriented interface for fetching the latest articles from specific categories, extracting content with proper parsing, and outputting structured data.

Features
--------

- 🔍 **RSS Feed Integration**: Fetch latest article URLs from Wired's RSS feeds
- 🌐 **Smart Content Extraction**: Extract titles, authors, and content with fallback methods
- 📱 **Multiple Output Formats**: Support for JSON and human-readable text output
- 🛡️ **Robust Error Handling**: Graceful handling of network issues and parsing errors
- 🧪 **Comprehensive Testing**: Full test suite with 86+ tests using unittest framework
- 📋 **Type Safety**: Complete type annotations with mypy compatibility
- 🎯 **CLI Interface**: Command-line tool for easy article fetching

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install the-data-packet

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from the_data_packet import WiredArticleScraper
   
   # Create a scraper instance
   scraper = WiredArticleScraper()
   
   # Get the latest security article
   article = scraper.get_latest_article("security")
   print(f"Title: {article.title}")
   print(f"Author: {article.author}")
   
   # Get both latest articles (security and guide)
   articles = scraper.get_both_latest_articles()
   
   # Clean up resources
   scraper.close()

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Get latest security article
   wired-scraper security
   
   # Get both latest articles
   wired-scraper both
   
   # Get multiple articles
   wired-scraper security --count 5
   
   # Scrape specific URL
   wired-scraper --url "https://www.wired.com/story/example/"

Package Structure
-----------------

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   api/models
   api/clients
   api/extractors
   api/scrapers
   api/cli

.. toctree::
   :maxdepth: 1
   :caption: Development:

   development/testing
   development/contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`