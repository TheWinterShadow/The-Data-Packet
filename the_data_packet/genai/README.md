# Daily News Podcast Generator

Automatically generate conversational podcast scripts from news articles using Claude AI.

## 📁 Files

```
podcast_generator/
├── prompts.py      # All prompt templates (edit these to customize)
├── generator.py    # Main podcast generation logic
├── example.py      # Usage examples
└── README.md       # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install anthropic
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or in Python:
```python
import os
os.environ["ANTHROPIC_API_KEY"] = "your-api-key-here"
```

### 3. Run Basic Example

```python
from generator import PodcastGenerator

# Your articles
articles = [
    "Full text of article 1...",
    "Full text of article 2...",
    "Full text of article 3..."
]

# Generate podcast
generator = PodcastGenerator(show_name="Tech Daily")
script = generator.generate_complete_episode(articles)

# Save to file
generator.save_script(script)
```

## 📖 How It Works

### Three Simple Steps

**Step 1: Article → Segment Script + Summary**
- For each article, make one API call
- Returns: conversation script + summary
- Stores both for later use

**Step 2: All Summaries → Show Framework**
- Takes all summaries from Step 1
- Makes one API call
- Returns: intro, transitions, closing

**Step 3: Combine Everything**
- Assembles: intro + segment1 + transition1 + segment2 + ... + closing
- Returns: complete podcast script

### Visual Flow

```
Article 1 ──→ API Call ──→ Script 1 + Summary 1
Article 2 ──→ API Call ──→ Script 2 + Summary 2  
Article 3 ──→ API Call ──→ Script 3 + Summary 3
                                    ↓
                        All Summaries ──→ API Call ──→ Intro + Transitions + Closing
                                                           ↓
                                            Final Script = Intro + Script1 + Trans1 + 
                                                          Script2 + Trans2 + Script3 + Closing
```

## 💻 Usage Examples

### Example 1: Basic Usage

```python
from generator import PodcastGenerator

articles = [
    "Article text here...",
    "Another article...",
    "Third article..."
]

generator = PodcastGenerator(show_name="My Podcast")
script = generator.generate_complete_episode(articles)

print(script)
```

### Example 2: Step-by-Step Control

```python
from generator import PodcastGenerator

generator = PodcastGenerator(show_name="Tech News")

# Step 1: Generate each segment
for i, article in enumerate(articles):
    result = generator.generate_segment(article, segment_num=i+1)
    # result contains 'script' and 'summary'

# Step 2: Generate framework
framework = generator.generate_framework(episode_date="December 11, 2024")
# framework contains 'opening', 'transitions', 'closing'

# Step 3: Assemble
final_script = generator.assemble_final_script()

# Save
generator.save_script(final_script)
```

### Example 3: Custom Show Name and Date

```python
generator = PodcastGenerator(show_name="The Daily Brief")

script = generator.generate_complete_episode(
    articles=articles,
    episode_date="Wednesday, December 11, 2024"
)
```

## 🎨 Customization

### Modify Prompts

Edit `prompts.py` to customize:
- Host personalities (Alex and Sam)
- Conversation style
- Segment structure
- Show opening/closing format

### Change Show Format

In `prompts.py`, modify:
- `ARTICLE_TO_SEGMENT_PROMPT` for segment style
- `SUMMARIES_TO_FRAMEWORK_PROMPT` for show structure

### Adjust Segment Length

In `ARTICLE_TO_SEGMENT_PROMPT`, change:
```python
### Length
3-4 minutes of dialogue (450-650 words)
```

To your preferred length.

## 📝 Output Format

The final script includes:

```
================================================================================
PODCAST EPISODE SCRIPT
================================================================================

[Show opening with previews of all stories]

--------------------------------------------------------------------------------
SEGMENT 1
--------------------------------------------------------------------------------

Alex: [dialogue]
Sam: [dialogue]
...

--------------------------------------------------------------------------------
TRANSITION 1 → 2
--------------------------------------------------------------------------------

[Bridge to next story]

--------------------------------------------------------------------------------
SEGMENT 2
--------------------------------------------------------------------------------

[And so on...]

--------------------------------------------------------------------------------
CLOSING
--------------------------------------------------------------------------------

[Show wrap-up and sign-off]
```

## ⚙️ Advanced Configuration

### Parallel Processing

To speed up generation, you can run Step 1 in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

def generate_segment_wrapper(args):
    generator, article, num = args
    return generator.generate_segment(article, num)

generator = PodcastGenerator()

# Generate segments in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    args = [(generator, article, i+1) for i, article in enumerate(articles)]
    results = list(executor.map(generate_segment_wrapper, args))

# Then continue with Step 2 and 3
framework = generator.generate_framework()
final_script = generator.assemble_final_script()
```

### Error Handling

```python
try:
    script = generator.generate_complete_episode(articles)
    generator.save_script(script)
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Generation error: {e}")
    # Log, retry, or alert
```

### Custom File Naming

```python
from datetime import datetime

filename = f"podcast_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
generator.save_script(script, filename)
```

## 🎯 Best Practices

### Article Length
- **Ideal**: 200-800 words per article
- **Too short**: < 100 words (not enough to discuss)
- **Too long**: > 1500 words (segment will be too long)

### Number of Articles
- **Recommended**: 3-5 articles per episode
- **Minimum**: 2 articles
- **Maximum**: 7-8 articles (longer episodes, 25+ minutes)

### Article Quality
- Use full article text, not just headlines
- Include author, source, and date if available
- Make sure text is clean (no HTML tags, weird formatting)

### Show Format
- Stories can be completely unrelated (that's fine!)
- System handles topic shifts naturally
- Transitions acknowledge when stories are unrelated

## 🔧 Troubleshooting

### "API key required" Error
```bash
export ANTHROPIC_API_KEY="your-key"
```

### Parsing Errors
The system tries to parse responses, but if it fails:
- Check that `prompts.py` hasn't been modified incorrectly
- Response format may have changed - inspect the raw response
- File an issue with the error message

### Poor Quality Output
- Make sure articles have substantial content (not just headlines)
- Try adjusting prompts in `prompts.py`
- Check that your articles are in English (or modify prompts for other languages)

### Slow Generation
- Each segment takes 10-30 seconds
- Framework generation takes 20-40 seconds
- For 3 articles: expect 1.5-3 minutes total
- Use parallel processing for faster generation (see Advanced Configuration)

## 📊 Cost Estimate

Using Claude Sonnet 4:
- Step 1 (per article): ~500-1000 input tokens, ~600-1000 output tokens
- Step 2 (framework): ~800-1200 input tokens, ~800-1200 output tokens

**For 3-article episode:**
- Total input tokens: ~3500-5000
- Total output tokens: ~3000-4500
- Cost per episode: ~$0.15-0.25

## 🎙️ Next Steps

After generating your script:
1. Review and edit if needed
2. Send to TTS system (ElevenLabs, Google TTS, etc.)
3. Process audio segments
4. Upload to podcast hosting platform

## 📄 License

MIT License - Feel free to modify and use for your projects!

## 🤝 Contributing

Found a bug or have a suggestion? Please open an issue!

Want to improve the prompts? Edit `prompts.py` and submit a PR!