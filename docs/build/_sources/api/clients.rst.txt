Client Modules
==============

The clients module provides HTTP and RSS feed functionality for fetching data from external sources.

HTTP Client
-----------

.. autoclass:: the_data_packet.clients.HTTPClient
   :members:
   :inherited-members:
   :show-inheritance:

   .. automethod:: __init__
   
   The `HTTPClient` handles all HTTP requests to fetch web pages. It includes automatic
   retries, proper error handling, and session management.
   
   **Example Usage:**
   
   .. code-block:: python
   
      from the_data_packet.clients import HTTPClient
      
      # Create client with custom settings
      client = HTTPClient(timeout=60, user_agent="MyBot/1.0")
      
      # Get a webpage as BeautifulSoup object
      soup = client.get_page("https://www.wired.com/story/example/")
      
      # Get raw HTML content
      html = client.get_raw_content("https://www.wired.com/story/example/")
      
      # Clean up resources
      client.close()

RSS Client
----------

.. autoclass:: the_data_packet.clients.RSSClient
   :members:
   :inherited-members:
   :show-inheritance:

   .. automethod:: __init__
   
   The `RSSClient` interacts with Wired's RSS feeds to discover the latest articles
   in different categories.
   
   **Example Usage:**
   
   .. code-block:: python
   
      from the_data_packet.clients import RSSClient
      
      client = RSSClient()
      
      # Get the latest article URL from security feed
      url = client.get_latest_article_url("security")
      
      # Get multiple article URLs
      urls = client.get_article_urls("guide", limit=5)
      
      # Check supported categories
      categories = client.get_supported_categories()

Client Base Classes
-------------------

.. automodule:: the_data_packet.clients.rss_client
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: the_data_packet.clients.http_client
   :members:
   :undoc-members:
   :show-inheritance: