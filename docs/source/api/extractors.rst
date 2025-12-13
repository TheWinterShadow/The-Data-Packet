Content Extractors
==================

The extractors module handles parsing and extracting structured data from raw HTML content.

Wired Content Extractor
------------------------

.. autoclass:: the_data_packet.extractors.WiredContentExtractor
   :members:
   :inherited-members:
   :show-inheritance:

   .. automethod:: __init__
   
   The `WiredContentExtractor` is specialized for extracting article data from Wired.com
   pages. It uses multiple extraction strategies with fallbacks to ensure robust parsing.
   
   **Extraction Methods:**
   
   - **Title Extraction**: Tries page title, H1 tags, and OpenGraph meta tags
   - **Author Extraction**: Searches meta tags, JSON-LD structured data, and byline elements
   - **Content Extraction**: Identifies article content areas and filters promotional text
   
   **Example Usage:**
   
   .. code-block:: python
   
      from the_data_packet.extractors import WiredContentExtractor
      from the_data_packet.clients import HTTPClient
      
      # Create extractor
      extractor = WiredContentExtractor()
      
      # Get a webpage
      client = HTTPClient()
      soup = client.get_page("https://www.wired.com/story/example/")
      
      # Extract article data
      article = extractor.extract(soup, url="https://www.wired.com/story/example/")
      
      print(f"Title: {article.title}")
      print(f"Author: {article.author}")
      print(f"Content length: {len(article.content)} characters")
      
      # Clean up
      client.close()

Private Methods
---------------

The extractor uses several private methods for robust content extraction:

.. automethod:: the_data_packet.extractors.WiredContentExtractor._extract_title
   
   Extracts article titles using multiple fallback strategies.

.. automethod:: the_data_packet.extractors.WiredContentExtractor._extract_author
   
   Extracts author information from various page elements.

.. automethod:: the_data_packet.extractors.WiredContentExtractor._extract_content
   
   Extracts the main article content while filtering out promotional text.

.. automethod:: the_data_packet.extractors.WiredContentExtractor._extract_author_from_json_ld
   
   Parses JSON-LD structured data to extract author information.

Module Functions
----------------

.. automodule:: the_data_packet.extractors.wired_extractor
   :members:
   :undoc-members:
   :show-inheritance: