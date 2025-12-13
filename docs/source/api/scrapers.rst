Web Scrapers
============

The scrapers module provides high-level interfaces for orchestrating the article scraping process.

Wired Article Scraper
----------------------

.. autoclass:: the_data_packet.scrapers.WiredArticleScraper
   :members:
   :inherited-members:
   :show-inheritance:

   .. automethod:: __init__
   
   The `WiredArticleScraper` is the main orchestrator that combines RSS feeds, HTTP clients,
   and content extractors to provide a simple interface for scraping Wired articles.
   
   **Key Features:**
   
   - **Category Support**: Handles 'security' and 'guide' article categories
   - **Batch Operations**: Can fetch multiple articles at once
   - **Resource Management**: Automatic cleanup of HTTP sessions
   - **Error Handling**: Comprehensive error reporting and recovery
   
   **Example Usage:**
   
   .. code-block:: python
   
      from the_data_packet.scrapers import WiredArticleScraper
      
      # Create scraper with custom timeout
      scraper = WiredArticleScraper(timeout=60)
      
      # Get latest security article
      security_article = scraper.get_latest_article("security")
      
      # Get latest guide article  
      guide_article = scraper.get_latest_article("guide")
      
      # Get both latest articles at once
      both_articles = scraper.get_both_latest_articles()
      print(f"Security: {both_articles['security'].title}")
      print(f"Guide: {both_articles['guide'].title}")
      
      # Get multiple articles from a category
      articles = scraper.get_multiple_articles("security", limit=5)
      for i, article in enumerate(articles, 1):
          print(f"{i}. {article.title}")
      
      # Scrape a specific URL
      article = scraper.scrape_article_from_url(
          "https://www.wired.com/story/specific-article/",
          category="custom"
      )
      
      # Always clean up resources
      scraper.close()

Method Details
--------------

Latest Article Methods
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: the_data_packet.scrapers.WiredArticleScraper.get_latest_article

   Generic method for fetching the latest article from any supported category.

.. automethod:: the_data_packet.scrapers.WiredArticleScraper.get_latest_security_article

   Convenience method specifically for security articles.

.. automethod:: the_data_packet.scrapers.WiredArticleScraper.get_latest_guide_article

   Convenience method specifically for guide articles.

.. automethod:: the_data_packet.scrapers.WiredArticleScraper.get_both_latest_articles

   Efficiently fetches both latest security and guide articles.

Batch Operations
~~~~~~~~~~~~~~~~

.. automethod:: the_data_packet.scrapers.WiredArticleScraper.get_multiple_articles

   Fetches multiple articles from a category with configurable limits.

Direct URL Scraping
~~~~~~~~~~~~~~~~~~~~

.. automethod:: the_data_packet.scrapers.WiredArticleScraper.scrape_article_from_url

   Scrapes a specific article URL directly, bypassing RSS feeds.

Resource Management
~~~~~~~~~~~~~~~~~~~

.. automethod:: the_data_packet.scrapers.WiredArticleScraper.close

   Properly closes HTTP sessions and cleans up resources.

Module Functions
----------------

.. automodule:: the_data_packet.scrapers.wired_scraper
   :members:
   :undoc-members:
   :show-inheritance: