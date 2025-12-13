"""Command-line interface for The Data Packet podcast generator."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from the_data_packet.core import get_logger, setup_logging
from the_data_packet.workflows import PipelineConfig, PodcastPipeline


def main() -> None:
    """Main CLI function for podcast generation."""
    parser = argparse.ArgumentParser(
        description="Generate automated tech news podcasts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate complete podcast with environment variables
  podcast-generator --output ./episode

  # Generate script only with custom API keys
  podcast-generator --anthropic-key sk-ant-... --script-only --output ./scripts

  # Generate with custom show name and voices
  podcast-generator --show-name "Tech Brief" --voice-a Charon --voice-b Aoede

  # Generate from specific categories
  podcast-generator --categories security guide --output ./multi-category

Environment Variables:
  ANTHROPIC_API_KEY    - Claude API key for script generation
  GOOGLE_API_KEY       - Gemini API key for audio generation
  GEMINI_API_KEY       - Alternative name for Google API key
        """,
    )

    # API Keys
    parser.add_argument(
        "--anthropic-key",
        help="Anthropic API key (overrides ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--google-key",
        help="Google API key (overrides GOOGLE_API_KEY env var)",
    )

    # Output control
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="./output",
        help="Output directory for generated files (default: ./output)",
    )
    parser.add_argument(
        "--script-only",
        action="store_true",
        help="Generate script only, skip audio generation",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Generate audio from existing script file (requires --script-file)",
    )
    parser.add_argument(
        "--script-file",
        type=str,
        help="Path to existing script file for audio-only generation",
    )

    # Podcast configuration
    parser.add_argument(
        "--show-name",
        type=str,
        default="Tech Daily",
        help="Name of the podcast show (default: Tech Daily)",
    )
    parser.add_argument(
        "--episode-date",
        type=str,
        help="Episode date (default: current date)",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["security", "guide"],
        help="Article categories to scrape (default: security guide)",
    )

    # Audio configuration
    parser.add_argument(
        "--voice-a",
        type=str,
        default="Puck",
        help="Voice for host Alex (default: Puck)",
    )
    parser.add_argument(
        "--voice-b",
        type=str,
        default="Kore",
        help="Voice for host Sam (default: Kore)",
    )

    # Output files
    parser.add_argument(
        "--script-filename",
        type=str,
        default="episode_script.txt",
        help="Filename for generated script (default: episode_script.txt)",
    )
    parser.add_argument(
        "--audio-filename",
        type=str,
        default="episode.wav",
        help="Filename for generated audio (default: episode.wav)",
    )

    # Logging and debug
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output except errors",
    )

    # Validation and cleanup
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't clean up temporary files",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate results after generation",
    )

    args = parser.parse_args()

    # Setup logging
    if args.quiet:
        log_level = "ERROR"
    elif args.debug:
        log_level = "DEBUG"
    elif args.verbose:
        log_level = "INFO"
    else:
        log_level = "WARNING"

    setup_logging(level=log_level)
    logger = get_logger(__name__)

    try:
        # Handle audio-only mode
        if args.audio_only:
            if not args.script_file:
                print(
                    "❌ --script-file is required when using --audio-only",
                    file=sys.stderr,
                )
                sys.exit(1)

            script_path = Path(args.script_file)
            if not script_path.exists():
                print(f"❌ Script file not found: {script_path}", file=sys.stderr)
                sys.exit(1)

            # Read existing script
            with open(script_path, "r", encoding="utf-8") as f:
                script_content = f.read()

            # Generate audio only
            from the_data_packet.audio import GeminiTTSGenerator

            audio_gen = GeminiTTSGenerator(
                api_key=args.google_key, voice_a=args.voice_a, voice_b=args.voice_b
            )

            output_path = Path(args.output) / args.audio_filename
            result = audio_gen.generate_audio(script_content, output_path)

            print(f"✅ Audio generated: {result.output_file}")
            return

        # Create pipeline configuration
        config = PipelineConfig(
            episode_date=args.episode_date or datetime.now().strftime("%A, %B %d, %Y"),
            show_name=args.show_name,
            categories=args.categories,
            generate_script=True,
            generate_audio=not args.script_only,
            output_directory=Path(args.output),
            script_filename=args.script_filename,
            audio_filename=args.audio_filename,
            anthropic_api_key=args.anthropic_key,
            google_api_key=args.google_key,
            voice_a=args.voice_a,
            voice_b=args.voice_b,
            cleanup_temp_files=not args.no_cleanup,
            validate_results=args.validate,
        )

        # Validate configuration
        validation_errors = config.validate()
        if validation_errors:
            print("❌ Configuration errors:", file=sys.stderr)
            for error in validation_errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

        # Display configuration (if not quiet)
        if not args.quiet:
            print("🎙️ The Data Packet - Podcast Generator")
            print("=" * 50)
            print(f"Show Name: {config.show_name}")
            print(f"Episode Date: {config.episode_date}")
            print(f"Categories: {', '.join(config.categories)}")
            print(f"Generate Script: {'✅' if config.generate_script else '❌'}")
            print(f"Generate Audio: {'✅' if config.generate_audio else '❌'}")
            print(f"Output Directory: {config.output_directory}")
            print(f"Voices: {config.voice_a} & {config.voice_b}")
            print("=" * 50)

        # Create and run pipeline
        pipeline = PodcastPipeline(config)
        result = pipeline.run()

        # Display results
        if result.success:
            if not args.quiet:
                print("\n🎉 Podcast generation completed successfully!")
                print("📊 Results:")
                print(f"  Articles Scraped: {result.articles_scraped}")
                print(
                    f"  Script Generated: {'✅' if result.script_generated else '❌'}"
                )
                print(f"  Audio Generated: {'✅' if result.audio_generated else '❌'}")

                if result.script_path:
                    print(f"  📝 Script: {result.script_path}")
                if result.audio_path:
                    print(f"  🎵 Audio: {result.audio_path}")

                print(f"  ⏱️ Execution Time: {result.execution_time_seconds:.1f}s")

            # Output paths as JSON for programmatic use
            output_data = {
                "success": True,
                "script_path": str(result.script_path) if result.script_path else None,
                "audio_path": str(result.audio_path) if result.audio_path else None,
                "execution_time": result.execution_time_seconds,
            }

            if args.debug:
                print(f"\n📋 Output JSON: {json.dumps(output_data, indent=2)}")

        else:
            print(
                f"❌ Podcast generation failed: {result.error_message}", file=sys.stderr
            )
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ Generation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error during podcast generation")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
