"""Test configuration and shared test data.

This file contains shared constants and test data used across multiple test files.
With unittest, setUp methods in each test class handle mock creation instead of fixtures.
"""

# Sample HTML for testing
SAMPLE_ARTICLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Article Title | WIRED</title>
    <meta name="author" content="Test Author">
    <meta property="og:title" content="Test Article Title">
</head>
<body>
    <article>
        <h1>Test Article Title</h1>
        <p>This is the first paragraph of the article content.</p>
        <p>This is the second paragraph with more content.</p>
        <p>And this is the third paragraph to complete the article.</p>
        <p>Subscribe to WIRED</p>  <!-- Should be filtered out -->
    </article>
</body>
</html>
"""

# Sample RSS feed response
SAMPLE_RSS_FEED = """
<rss version="2.0">
    <channel>
        <title>WIRED - Security</title>
        <description>Latest security articles</description>
        <item>
            <title>Latest Security Article</title>
            <link>https://www.wired.com/story/latest-security-article/</link>
            <description>Latest security news</description>
        </item>
        <item>
            <title>Second Security Article</title>
            <link>https://www.wired.com/story/second-security-article/</link>
            <description>More security news</description>
        </item>
    </channel>
</rss>
"""
