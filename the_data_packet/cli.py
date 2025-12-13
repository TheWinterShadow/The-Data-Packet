"""Command-line interface for the_data_packet."""

import argparse
import json
import logging
import sys

from the_data_packet.models import ArticleData
from the_data_packet.scrapers import WiredArticleScraper


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def format_article_output(article: ArticleData, format_type: str = "json") -> str:
    """Format article data for output."""
    if format_type == "json":
        return json.dumps(article.to_dict(), indent=2, ensure_ascii=False)
    elif format_type == "text":
        output = []
        output.append(f"Title: {article.title or 'N/A'}")
        output.append(f"Author: {article.author or 'N/A'}")
        output.append(f"Category: {article.category or 'N/A'}")
        output.append(f"URL: {article.url or 'N/A'}")
        output.append(
            f"Content Length: {len(article.content) if article.content else 0} characters"
        )
        if article.content:
            output.append("\\nContent:")
            output.append("-" * 50)
            output.append(article.content)
        return "\\n".join(output)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def main() -> None:
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Scrape articles from Wired.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s security                    # Get latest security article
  %(prog)s guide                       # Get latest guide article  
  %(prog)s both                        # Get both latest articles
  %(prog)s security --count 5          # Get 5 security articles
  %(prog)s --url https://wired.com/... # Scrape specific URL
  %(prog)s security --format text      # Output as text instead of JSON
        """,
    )

    parser.add_argument(
        "category",
        nargs="?",
        choices=["security", "guide", "both"],
        help="Article category to fetch (required unless using --url)",
    )

    parser.add_argument("--url", help="Specific article URL to scrape")

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of articles to fetch (default: 1, max: 10)",
    )

    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.url and not args.category:
        parser.error("Must specify either category or --url")

    if args.url and args.category:
        parser.error("Cannot specify both category and --url")

    if args.count < 1 or args.count > 10:
        parser.error("Count must be between 1 and 10")

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Initialize scraper
    scraper = WiredArticleScraper()

    try:
        if args.url:
            # Scrape specific URL
            logger.info(f"Scraping URL: {args.url}")
            article = scraper.scrape_article_from_url(args.url)
            print(format_article_output(article, args.format))

        elif args.category == "both":
            # Get both latest articles
            logger.info("Fetching both latest articles")
            both_articles = scraper.get_both_latest_articles()

            if args.format == "json":
                both_output = {
                    category: article.to_dict()
                    for category, article in both_articles.items()
                }
                print(json.dumps(both_output, indent=2, ensure_ascii=False))
            else:
                for category, article in both_articles.items():
                    print(f"\\n=== {category.upper()} ARTICLE ===")
                    print(format_article_output(article, "text"))

        else:
            # Get articles from specific category
            if args.count == 1:
                logger.info(f"Fetching latest {args.category} article")
                article = scraper.get_latest_article(args.category)
                print(format_article_output(article, args.format))
            else:
                logger.info(f"Fetching {args.count} {args.category} articles")
                article_list = scraper.get_multiple_articles(args.category, args.count)

                if args.format == "json":
                    list_output = [article.to_dict() for article in article_list]
                    print(json.dumps(list_output, indent=2, ensure_ascii=False))
                else:
                    for i, article in enumerate(article_list, 1):
                        print(f"\\n=== ARTICLE {i} ===")
                        print(format_article_output(article, "text"))

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
