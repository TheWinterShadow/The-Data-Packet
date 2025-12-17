"""Test runner for The Data Packet test suite.

This module provides a convenient way to run all tests for The Data Packet project.
It discovers and runs all tests in the tests/ directory using Python's unittest framework.

Usage:
    # Run all tests
    python -m tests.run_tests

    # Run tests with verbose output
    python -m tests.run_tests --verbose

    # Run specific test module
    python -m unittest tests.test_cli

    # Run specific test class
    python -m unittest tests.core.test_config.TestConfig

    # Run specific test method
    python -m unittest tests.core.test_config.TestConfig.test_default_config_creation

Test Structure:
    tests/
    ├── __init__.py              # Test package initialization
    ├── run_tests.py            # This file - test runner
    ├── test___about__.py       # Tests for __about__.py
    ├── test___init__.py        # Tests for __init__.py
    ├── test_cli.py             # Tests for cli.py
    ├── core/                   # Tests for core module
    │   ├── test___init__.py
    │   ├── test_config.py
    │   ├── test_exceptions.py
    │   └── test_logging.py
    ├── generation/             # Tests for generation module
    │   ├── test___init__.py
    │   ├── test_audio.py
    │   ├── test_rss.py
    │   └── test_script.py
    ├── sources/                # Tests for sources module
    │   ├── test___init__.py
    │   ├── test_base.py
    │   ├── test_techcrunch.py
    │   └── test_wired.py
    ├── utils/                  # Tests for utils module
    │   ├── test___init__.py
    │   ├── test_http.py
    │   └── test_s3.py
    └── workflows/              # Tests for workflows module
        ├── test___init__.py
        └── test_podcast.py

Test Coverage:
    - Package structure and imports
    - Configuration management and validation
    - Exception hierarchy and handling
    - Logging system setup and configuration
    - CLI argument parsing and execution
    - Audio generation with ElevenLabs TTS
    - RSS feed generation and management
    - Script generation with Claude AI
    - Article collection from news sources
    - HTTP client functionality
    - S3 storage backend integration
    - Complete podcast generation pipeline
"""

import sys
import unittest
from pathlib import Path


def run_tests(verbosity=1, pattern="test*.py"):
    """
    Discover and run all tests in the tests directory.

    Args:
        verbosity: Test output verbosity level (0=quiet, 1=normal, 2=verbose)
        pattern: Test file pattern to match (default: 'test*.py')

    Returns:
        TestResult object with test results
    """
    # Add the project root to Python path so imports work
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Discover tests starting from the tests directory
    tests_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(tests_dir), pattern=pattern, top_level_dir=str(project_root)
    )

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)

    return result


def main():
    """Main entry point for test runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run tests for The Data Packet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tests.run_tests                    # Run all tests with normal output
  python -m tests.run_tests --verbose          # Run all tests with verbose output
  python -m tests.run_tests --quiet            # Run all tests with minimal output
  python -m tests.run_tests --pattern "test_core*"  # Run only core tests
        """,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (show each test method)",
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Quiet output (minimal)"
    )

    parser.add_argument(
        "--pattern",
        "-p",
        default="test*.py",
        help="Test file pattern to match (default: test*.py)",
    )

    args = parser.parse_args()

    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    print("=" * 70)
    print("Running The Data Packet Test Suite")
    print("=" * 70)

    # Run the tests
    result = run_tests(verbosity=verbosity, pattern=args.pattern)

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, "skipped") else 0
    passed = total_tests - failures - errors - skipped

    print(f"Total tests run: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    if skipped > 0:
        print(f"Skipped: {skipped}")

    if failures > 0:
        print("\nFAILED TESTS:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if errors > 0:
        print("\nERROR TESTS:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    # Exit with appropriate code
    if failures > 0 or errors > 0:
        print(f"\n❌ Tests FAILED ({failures} failures, {errors} errors)")
        sys.exit(1)
    else:
        print(f"\n✅ All tests PASSED ({passed}/{total_tests})")
        sys.exit(0)


if __name__ == "__main__":
    main()
