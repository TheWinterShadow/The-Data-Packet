The Data Packet Documentation
===============================

Welcome to The Data Packet's documentation!

**The Data Packet** is an AI-powered automated podcast generation system that transforms tech news articles into engaging podcast content. It combines web scraping, AI script generation, and text-to-speech to create complete podcast episodes from start to finish.

What It Does
------------

The Data Packet automates the entire podcast creation workflow:

1. **📰 Article Collection**: Scrapes latest tech news from Wired.com and TechCrunch via RSS feeds
2. **🤖 Script Generation**: Uses Anthropic Claude AI to create engaging dialogue scripts 
3. **🎙️ Audio Production**: Generates multi-speaker audio using Google Cloud Text-to-Speech Long Audio Synthesis
4. **�️ Episode Tracking**: Optional MongoDB integration for article deduplication and episode metadata
5. **📦 Podcast Distribution**: Creates RSS feeds and uploads to AWS S3 for hosting
6. **🔄 Complete Automation**: Runs the entire pipeline with a single command

Key Features
------------

- **🐳 Docker-First Deployment**: Run anywhere with consistent environment
- **🤖 AI-Powered Content**: Claude for natural dialogue, Google Cloud TTS for professional voices
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
     -e GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json" \\
     -e GCS_BUCKET_NAME="your-audio-bucket" \\
     -v "$(pwd)/output:/app/output" \\
     -v "$(pwd)/credentials.json:/path/to/credentials.json" \\
     ghcr.io/thewintershadow/the-data-packet:latest

Python Installation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install the-data-packet

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from the_data_packet import PodcastPipeline, get_config
   
   # Create configuration and run the complete pipeline
   config = get_config(show_name="Tech Brief", max_articles_per_source=1)
   pipeline = PodcastPipeline(config)
   result = pipeline.run()
   
   if result.success:
       print(f"Podcast generated: {result.audio_path}")
       if result.rss_path:
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
     --voice-a en-US-Studio-MultiSpeaker-R \\
     --voice-b en-US-Studio-MultiSpeaker-S \\
     --gcs-bucket-name your-audio-bucket \\
     --sources wired techcrunch \\
     --categories security ai

Architecture Overview
---------------------

The Data Packet is built with a modular architecture:

- **Core**: Configuration, exceptions, logging
- **Sources**: Article collection from news websites  
- **Generation**: AI script and audio generation
- **Utils**: MongoDB integration, S3 storage, HTTP clients
- **Workflows**: End-to-end pipeline orchestration

Package Structure
-----------------

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   api/core
   api/sources  
   api/generation
   api/utils
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