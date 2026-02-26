---
title: Contributing
description: How to report bugs, request features, and contribute code or documentation to The Data Packet.
icon: material/source-pull
---

# Contributing

Contributions to The Data Packet are welcome. This page covers the contribution process;
[Development Setup](development.md) covers the local dev environment.

---

## Ways to contribute

<div class="grid cards" markdown>

-   :material-bug-outline: **Bug reports**

    ---

    Open an [issue](https://github.com/TheWinterShadow/The-Data-Packet/issues) with steps
    to reproduce, expected behaviour, and actual behaviour.

-   :material-lightbulb-outline: **Feature requests**

    ---

    Open an issue describing the use case and proposed solution. Discuss approach before
    writing code for significant changes.

-   :material-source-pull: **Pull requests**

    ---

    Bug fixes, new article sources, documentation improvements. All PRs require passing
    CI (format, type check, tests).

-   :material-book-edit-outline: **Documentation**

    ---

    Corrections, clearer explanations, additional examples. Docs live in `docs/` and are
    written in Markdown.

</div>

---

## Contribution process

1. **Open an issue first** for significant changes — agree on approach before writing code.
2. **Fork the repository** and create a feature branch from `main`.
3. **Write tests** for any new functionality.
4. **Run the full quality check** before submitting:

    ```bash
    hatch run format
    hatch run format-check
    hatch run typecheck
    hatch run test
    ```

5. **Open a pull request** against `main` with a clear description.

---

## Adding a new article source

The source system is designed for extension. To add a new source:

**1. Create the module**

```python title="the_data_packet/sources/your_source.py"
from the_data_packet.sources.base import Article, ArticleSource

class YourSource(ArticleSource):
    def collect_articles(
        self,
        categories: list[str],
        max_articles: int,
    ) -> list[Article]:
        # Fetch and return Article objects
        ...
```

**2. Register it**

Add to `the_data_packet/sources/__init__.py` and the `--sources` choices in `cli.py`.

**3. Add tests**

```bash
tests/sources/test_your_source.py
```

---

## Code standards

| Standard | Tool | Config |
|---|---|---|
| Formatting | `black` | line length 88, target py3.9 |
| Import order | `isort` | black-compatible profile |
| Linting | `flake8` | max line length 120 |
| Type hints | `mypy` | strict, ignore missing imports |
| Docstrings | Google style | all public classes and functions |

---

## Reporting security issues

Open a [security vulnerability report](https://github.com/TheWinterShadow/The-Data-Packet/issues/new?template=security.yml)
on GitHub. For high-severity issues where public disclosure would be harmful before a fix is available, use
[GitHub's private security advisory](https://github.com/TheWinterShadow/The-Data-Packet/security/advisories/new) instead.

Either way, include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
