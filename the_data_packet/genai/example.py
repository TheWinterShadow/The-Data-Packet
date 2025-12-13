"""
Example Usage: Daily News Podcast Generator

This shows how to use the PodcastGenerator to create podcast scripts.
"""

from the_data_packet.genai.generator import PodcastGenerator

# =============================================================================
# EXAMPLE 1: Basic Usage
# =============================================================================

def basic_example() -> None:
    """Simple example with 3 unrelated news articles."""

    print("EXAMPLE 1: Basic Usage")
    print("=" * 80)

    # Your daily news articles (completely unrelated is fine)
    articles = [
        """
        OpenAI Announces GPT-5 Release Date
        By Sarah Johnson | TechCrunch | December 11, 2024
        
        In a surprise announcement today, OpenAI confirmed that GPT-5 will launch 
        in March 2025. CEO Sam Altman stated in a blog post that the new model will 
        feature "significant improvements in reasoning, coding, and creative writing 
        capabilities."
        
        The announcement comes after months of speculation about OpenAI's next major 
        release. GPT-5 will reportedly feature a larger context window of 500,000 
        tokens and improved multimodal capabilities, allowing it to process video 
        and audio inputs alongside text and images.
        
        Pricing details were not disclosed, but Altman hinted that OpenAI is working 
        on "more accessible pricing tiers" for individual developers and small businesses. 
        The company also announced that GPT-4 will remain available with continued 
        support and updates.
        
        Industry analysts see this as OpenAI's move to maintain its competitive edge 
        against Anthropic's Claude and Google's Gemini models, both of which have 
        gained significant market share in recent months.
        """,

        """
        Apple Faces €500M EU Antitrust Fine Over App Store Practices
        By Michael Chen | Reuters | December 11, 2024
        
        The European Commission is preparing to fine Apple approximately €500 million 
        ($540 million) over its App Store practices, according to sources familiar 
        with the matter. The fine relates to Apple's restrictions on music streaming 
        apps, which prevent them from directing users to cheaper subscription options 
        outside the App Store.
        
        The investigation began in 2020 following a complaint by Spotify, which argued 
        that Apple's 30% commission and restrictive rules create an unfair competitive 
        advantage for Apple Music. The commission found that Apple's "anti-steering" 
        provisions violated EU competition law.
        
        Apple plans to appeal the decision, with a spokesperson stating that the 
        company "respectfully disagrees with the Commission's findings" and believes 
        the App Store has "created a level playing field" for all developers.
        
        This fine is part of broader EU scrutiny of major tech platforms under the 
        Digital Markets Act, which went into effect earlier this year. Apple, Google, 
        Amazon, and Meta have all faced similar investigations regarding their market 
        practices in Europe.
        """,

        """
        Study Finds AI Coding Assistants May Reduce Developer Productivity
        By Dr. Emily Rodriguez | Stanford Research | December 10, 2024
        
        A new study from Stanford University challenges the widespread assumption that 
        AI coding assistants improve developer productivity. The research, which tracked 
        200 software engineers over six months, found that those using AI tools like 
        GitHub Copilot and ChatGPT actually showed a 15% decrease in overall productivity 
        compared to a control group.
        
        Lead researcher Dr. Emily Rodriguez explained that while AI tools helped 
        developers write code faster, they introduced significant downstream costs. 
        "We found that AI-generated code required more debugging time, had more security 
        vulnerabilities, and created technical debt that took considerable effort to 
        resolve," Rodriguez stated.
        
        The study also noted concerning patterns of over-reliance on AI suggestions. 
        Junior developers, in particular, showed reduced problem-solving skills and 
        struggled when AI tools were unavailable. Senior developers fared better but 
        reported spending substantial time reviewing and correcting AI-generated code.
        
        However, the research did identify beneficial use cases. AI tools proved valuable 
        for boilerplate code, documentation, and learning new frameworks. The study 
        recommends that organizations develop clear guidelines for AI tool usage rather 
        than treating them as universal productivity enhancers.
        
        The findings have sparked debate in the developer community, with some 
        questioning the study's methodology while others see it as validation of 
        concerns about AI's role in software development.
        """
    ]

    # Initialize generator
    generator = PodcastGenerator(show_name="Tech Daily Brief")

    # Generate complete episode
    final_script = generator.generate_complete_episode(
        articles=articles,
        episode_date="Wednesday, December 11, 2024"
    )

    # Save to file
    generator.save_script(final_script, "example_episode.txt")

    # Print first 1000 characters to see what it looks like
    print("\n📄 SCRIPT PREVIEW (first 1000 chars):")
    print("-" * 80)
    print(final_script[:1000])
    print("...")
    print("-" * 80)


# =============================================================================
# EXAMPLE 2: Step-by-Step (Manual Control)
# =============================================================================

def step_by_step_example() -> None:
    """Example showing manual control of each step."""

    print("\n\nEXAMPLE 2: Step-by-Step Manual Control")
    print("=" * 80)

    articles = [
        "Article 1 text here...",
        "Article 2 text here..."
    ]

    generator = PodcastGenerator(show_name="My Tech News")

    # Step 1: Generate segments one by one
    print("\nSTEP 1: Generating segments...")
    for i, article in enumerate(articles, start=1):
        result = generator.generate_segment(article, segment_num=i)
        print(f"  Segment {i} script length: {len(result['script'])} chars")
        print(f"  Segment {i} summary length: {len(result['summary'])} chars")

    # Step 2: Generate framework
    print("\nSTEP 2: Generating framework...")
    framework = generator.generate_framework(episode_date="December 11, 2024")
    print(f"  Opening length: {len(framework['opening'])} chars")
    print(f"  Transitions: {len(framework['transitions'])}")
    print(f"  Closing length: {len(framework['closing'])} chars")

    # Step 3: Assemble
    print("\nSTEP 3: Assembling final script...")
    final_script = generator.assemble_final_script()
    print(f"  Total script length: {len(final_script)} chars")

    # Save
    generator.save_script(final_script, "manual_episode.txt")


# =============================================================================
# EXAMPLE 3: Production Workflow
# =============================================================================

def production_workflow() -> None:
    """Example showing a realistic daily production workflow."""

    print("\n\nEXAMPLE 3: Production Workflow")
    print("=" * 80)

    # In production, you'd get these from your news aggregation system
    articles = fetch_todays_articles()  # Your function

    # Filter/select articles (e.g., top 4-6 stories)
    selected_articles = articles[:5]

    # Generate podcast
    generator = PodcastGenerator(show_name="Tech Today")

    try:
        final_script = generator.generate_complete_episode(
            articles=selected_articles
        )

        # Save with dated filename
        from datetime import datetime
        filename = f"podcast_{datetime.now().strftime('%Y%m%d')}.txt"
        generator.save_script(final_script, filename)

        print(f"✅ Success! Episode ready for TTS processing.")

        # Now you would send this script to your TTS system
        # send_to_tts(final_script)

    except Exception as e:
        print(f"❌ Error generating episode: {e}")
        # Handle error (log, alert, etc.)


def fetch_todays_articles() -> list[str]:
    """Placeholder for your article fetching logic."""
    # In production, this would fetch from your news sources
    return [
        "Article 1 text...",
        "Article 2 text...",
        "Article 3 text..."
    ]


# =============================================================================
# EXAMPLE 4: Testing with Short Articles
# =============================================================================

def quick_test() -> None:
    """Quick test with minimal articles."""

    print("\n\nEXAMPLE 4: Quick Test")
    print("=" * 80)

    # Very short articles for testing
    test_articles = [
        """
        Google Launches New Gemini Model
        Google announced Gemini 2.0 today with improved reasoning capabilities.
        The model will be available through Google Cloud next month.
        """,

        """
        Tesla Recalls 2 Million Vehicles
        Tesla is recalling 2 million vehicles due to a software issue with the
        Autopilot system. The fix will be delivered via over-the-air update.
        """
    ]

    generator = PodcastGenerator(show_name="Tech Quick Takes")

    final_script = generator.generate_complete_episode(test_articles)

    print("\n📄 FULL SCRIPT:")
    print("=" * 80)
    print(final_script)
    print("=" * 80)


# =============================================================================
# RUN EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Run the basic example
    # NOTE: Make sure ANTHROPIC_API_KEY environment variable is set!

    try:
        # Run basic example (recommended to start)
        basic_example()

        # Uncomment to run other examples:
        # step_by_step_example()
        # production_workflow()
        # quick_test()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. ANTHROPIC_API_KEY environment variable is set")
        print("  2. You have the anthropic package installed: pip install anthropic")
