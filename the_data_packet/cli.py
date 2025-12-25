"""Command-line interface for The Data Packet."""

import argparse
import sys
from pathlib import Path

from the_data_packet.core import (
    ConfigurationError,
    get_config,
    get_logger,
    setup_logging,
)
from the_data_packet.workflows import PodcastPipeline


def main() -> None:
    """Main CLI function for podcast generation."""
    parser = argparse.ArgumentParser(
        description="Generate automated tech news podcasts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate complete podcast with environment variables
  the-data-packet --output ./episode

  # Generate script only with custom API keys
  the-data-packet --anthropic-key sk-ant-... --script-only --output ./scripts

  # Generate with custom show name and voices
  the-data-packet --show-name "Tech Brief" --voice-a charon --voice-b aoede

  # Generate from specific sources and categories
  the-data-packet --sources wired techcrunch --categories security ai --output ./multi-source

Environment Variables:
  ANTHROPIC_API_KEY    - Claude API key for script generation
  ELEVENLABS_API_KEY   - ElevenLabs API key for TTS audio generation
  S3_BUCKET_NAME       - S3 bucket for uploads (optional)
  AWS_ACCESS_KEY_ID    - AWS access key (optional)
  AWS_SECRET_ACCESS_KEY - AWS secret key (optional)
  MONGODB_USERNAME     - MongoDB username for episode tracking (optional)
  MONGODB_PASSWORD     - MongoDB password for episode tracking (optional)
        """,
    )

    # API Keys
    parser.add_argument(
        "--anthropic-key",
        help="Anthropic API key (overrides ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--elevenlabs-key",
        help="ElevenLabs API key (overrides ELEVENLABS_API_KEY env var)",
    )
    parser.add_argument(
        "--mongodb-username",
        help="MongoDB username for episode tracking and article deduplication (overrides MONGODB_USERNAME env var)",
    )
    parser.add_argument(
        "--mongodb-password",
        help="MongoDB password for episode tracking and article deduplication (overrides MONGODB_PASSWORD env var)",
    )

    # Content Options
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["wired"],
        choices=["wired", "techcrunch"],
        help="Article sources to use (default: wired)",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["security", "ai"],
        help="Article categories to fetch (default: security ai)",
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=1,
        help="Maximum articles per source (default: 1)",
    )

    # Generation Options
    parser.add_argument(
        "--script-only",
        action="store_true",
        help="Generate script only (skip audio)",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Generate audio only (requires existing script)",
    )

    # Audio Settings
    parser.add_argument(
        "--voice-a",
        default="XrExE9yKIg1WjnnlVkGX",
        help="ElevenLabs voice ID for first speaker (default: XrExE9yKIg1WjnnlVkGX - George)",
    )
    parser.add_argument(
        "--voice-b",
        default="IKne3meq5aSn9XLyUdCD",
        help="ElevenLabs voice ID for second speaker (default: IKne3meq5aSn9XLyUdCD - Rachel)",
    )

    # Output Settings
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./output"),
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--show-name",
        default="The Data Packet",
        help="Name of your podcast show (default: The Data Packet)",
    )

    # S3 Upload
    parser.add_argument(
        "--s3-bucket",
        help="S3 bucket for uploads (overrides S3_BUCKET_NAME env var)",
    )
    parser.add_argument(
        "--no-s3",
        action="store_true",
        help="Disable S3 uploads even if configured",
    )

    # Other Options
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )
    parser.add_argument(
        "--save-intermediate",
        action="store_true",
        help="Save intermediate files",
    )

    args = parser.parse_args()

    # Validate argument combinations
    if args.script_only and args.audio_only:
        print("Error: Cannot use both --script-only and --audio-only", file=sys.stderr)
        sys.exit(1)

    # Set up logging
    setup_logging(args.log_level)
    logger = get_logger(__name__)

    try:
        # Build configuration from arguments
        config_overrides = {
            "show_name": args.show_name,
            "output_directory": args.output,
            "article_sources": args.sources,
            "article_categories": args.categories,
            "max_articles_per_source": args.max_articles,
            "voice_a": args.voice_a,
            "voice_b": args.voice_b,
            "save_intermediate_files": args.save_intermediate,
            "log_level": args.log_level,
        }

        # API keys
        if args.anthropic_key:
            config_overrides["anthropic_api_key"] = args.anthropic_key
        if args.elevenlabs_key:
            config_overrides["elevenlabs_api_key"] = args.elevenlabs_key
        if args.mongodb_username:
            config_overrides["mongodb_username"] = args.mongodb_username
        if args.mongodb_password:
            config_overrides["mongodb_password"] = args.mongodb_password
        if args.s3_bucket:
            config_overrides["s3_bucket_name"] = args.s3_bucket

        # Generation options
        if args.script_only:
            config_overrides.update(
                {
                    "generate_script": True,
                    "generate_audio": False,
                }
            )
        elif args.audio_only:
            config_overrides.update(
                {
                    "generate_script": False,
                    "generate_audio": True,
                }
            )
        else:
            config_overrides.update(
                {
                    "generate_script": True,
                    "generate_audio": True,
                }
            )

        # Disable S3 if requested
        if args.no_s3:
            config_overrides["s3_bucket_name"] = None

        # Get configuration with overrides
        config = get_config(**config_overrides)

        logger.info(f"Starting {config.show_name} generation")
        logger.info(f"Sources: {config.article_sources}")
        logger.info(f"Categories: {config.article_categories}")
        logger.info(f"Output: {config.output_directory}")

        # Run pipeline
        pipeline = PodcastPipeline(config)
        result = pipeline.run()

        # Report results
        if result.success:
            print("✅ Podcast generation completed successfully!")
            print(f"⏱️  Execution time: {result.execution_time_seconds:.1f} seconds")
            print(f"📰 Articles collected: {result.articles_collected}")

            if result.script_generated and result.script_path:
                print(f"📝 Script saved: {result.script_path}")
                if result.s3_script_url:
                    print(f"🔗 Script URL: {result.s3_script_url}")

            if result.audio_generated and result.audio_path:
                print(f"🎧 Audio saved: {result.audio_path}")
                if result.s3_audio_url:
                    print(f"🔗 Audio URL: {result.s3_audio_url}")

        else:
            print("❌ Podcast generation failed!", file=sys.stderr)
            print(f"⏱️  Execution time: {result.execution_time_seconds:.1f} seconds")
            print(f"❗ Error: {result.error_message}", file=sys.stderr)
            sys.exit(1)

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\\n⏹️  Generation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
