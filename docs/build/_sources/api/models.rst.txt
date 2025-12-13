Data Models
===========

The data models module provides the core data structures used throughout the package.

ArticleData
-----------

.. autoclass:: the_data_packet.models.ArticleData
   :members:
   :inherited-members:
   :show-inheritance:

   .. automethod:: __init__
   
   The `ArticleData` class is the primary data container for scraped article information.
   It provides validation methods and convenient serialization options.
   
   **Example Usage:**
   
   .. code-block:: python
   
      from the_data_packet.models import ArticleData
      
      # Create an article instance
      article = ArticleData(
          title="Sample Article Title",
          author="John Doe",
          content="Article content here...",
          url="https://example.com/article",
          category="technology"
      )
      
      # Validate the article data
      if article.is_valid():
          print("Article data is complete")
      
      # Convert to dictionary for serialization
      article_dict = article.to_dict()
      
      # Create from dictionary
      article = ArticleData.from_dict(article_dict)

Module Functions
----------------

.. automodule:: the_data_packet.models
   :members:
   :undoc-members:
   :show-inheritance: