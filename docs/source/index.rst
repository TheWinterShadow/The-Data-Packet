The Data Packet Documentation
===============================

Welcome to The Data Packet's documentation!

**The Data Packet** is an AI-powered automated podcast generation system that transforms tech news articles into engaging podcast content. It combines web scraping, AI script generation, and text-to-speech to create complete podcast episodes from start to finish.

What It Does
------------

The Data Packet automates the entire podcast creation workflow:

1. **📰 Article Collection**: Scrapes latest tech news from Wired.com via RSS feeds
2. **🤖 Script Generation**: Uses Anthropic Claude AI to create engaging dialogue scripts 
3. **🎙️ Audio Production**: Generates multi-speaker audio using Google Gemini TTS
4. **📦 Podcast Distribution**: Creates RSS feeds and uploads to AWS S3 for hosting
5. **🔄 Complete Automation**: Runs the entire pipeline with a single command

Key Features
------------

- **🐳 Docker-First Deployment**: Run anywhere with consistent environment
- **🤖 AI-Powered Content**: Claude for natural dialogue, Gemini for realistic voices
- **⚙️ Highly Configurable**: Multiple voices, show formats, and content categories
- **🔒 Production Ready**: Robust error handling, logging, and security
- **📊 Monitoring & Analytics**: Comprehensive logging and status tracking
- **🚀 CI/CD Integration**: GitHub Actions for automated builds and releases

Quick Start
-----------

Docker Deployment (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Pull the latest image
   docker pull ghcr.io/thewintershadow/the-data-packet:latest

   # Run with your API keys
   docker run --rm \\
     -e ANTHROPIC_API_KEY="your-claude-key" \\
     -e GOOGLE_API_KEY="your-gemini-key" \\
     -v "$(pwd)/output:/app/output" \\
     ghcr.io/thewintershadow/the-data-packet:latest

Python Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install the-data-packet

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from the_data_packet import PodcastPipeline
   
   # Create and run the complete pipeline
   pipeline = PodcastPipeline()
   result = pipeline.run()
   
   if result.success:
       print(f"Podcast generated: {result.audio_path}")
       print(f"RSS feed: {result.rss_path}")

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate complete podcast episode
   the-data-packet --output ./episode
   
   # Generate script only
   the-data-packet --script-only --output ./scripts
   
   # Custom configuration
   the-data-packet \\
     --show-name "Tech Brief" \\
     --voice-a charon \\
     --voice-b aoede \\
     --categories security guide

Architecture Overview
--------------------

The Data Packet is built with a modular architecture:

- **Core**: Configuration, exceptions, logging
- **Sources**: Article collection from news websites  
- **Generation**: AI script and audio generation
- **Storage**: AWS S3 integration for hosting
- **Workflows**: End-to-end pipeline orchestration
- **Utils**: HTTP clients, helper functions

Package Structure
-----------------

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   api/core
   api/sources  
   api/generation
   api/storage
   api/workflows
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