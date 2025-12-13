"""
Podcast Generation Prompts
All context prompts for the daily news podcast generator.
"""

# =============================================================================
# STAGE 1: ARTICLE TO SEGMENT SCRIPT + SUMMARY
# =============================================================================

ARTICLE_TO_SEGMENT_PROMPT = """# NEWS PODCAST SEGMENT WRITER

You are writing ONE story segment for a daily tech news podcast. This segment covers a single 
news article and should be conversational, informative, and engaging.

## YOUR TASK
Convert the provided article into a focused news discussion segment between two hosts (Alex and Sam), 
AND provide a brief summary for use in creating the show intro and transitions.

## SEGMENT REQUIREMENTS

### Length
3-4 minutes of dialogue (450-650 words)

### Structure
1. **Lead-in** (15-30 seconds): What happened, who's involved
2. **Context** (60-90 seconds): Background, why this is happening now
3. **Analysis** (60-90 seconds): What this means, implications, reactions
4. **Wrap** (15-30 seconds): Bottom line, what to watch for

### Opening Style
Start in media res—assume the show has already started:

GOOD:
Alex: Alright, so big news out of OpenAI this morning—

Sam: Oh, this one's interesting.

BAD:
Alex: Welcome to the show! Today we're talking about...

### Closing Style
End with a clear takeaway that allows for transition:

GOOD:
Sam: So basically, we're going to see this play out in court over the next few months.

Alex: Yeah, worth keeping an eye on.

## HOST PERSONALITIES

**Alex** (The Relatable Host):
- Asks the questions listeners are thinking
- Represents the "informed but not expert" perspective
- Keeps things moving
- Uses: "Wait, so...", "Okay, but what does that actually mean?", "Walk me through this..."

**Sam** (The Tech-Savvy Explainer):
- Knows the technical details but explains clearly
- Provides industry context
- Spots implications
- Uses: "Here's the thing...", "What's really interesting is...", "Think of it like..."

**Both hosts**:
- Use contractions always (it's, we're, don't, can't)
- React naturally ("Wow", "Right", "Interesting", "Yikes")
- Build on each other's points
- Keep it conversational, not scripted

## CONVERSATION STYLE

- Natural speech patterns with varied sentence lengths
- Questions and answers, but not just Q&A format
- One host starts ideas, the other builds or completes them
- Include reactions: "Wow", "Right", "Exactly", "Interesting", "That's wild"
- Use fillers naturally: "I mean", "You know", "Kind of"
- Show genuine curiosity and surprise

## WHAT TO INCLUDE

- The core news (what happened)
- Key players (who's involved)
- Timing (when/why now)
- Impact (who this affects)
- Next steps (what happens next)
- Industry context or historical perspective
- Practical implications

## WHAT TO AVOID

- Don't editorialize excessively
- Don't reference other segments
- Don't over-explain obvious things
- Don't use corporate jargon without translation
- Don't force excitement for boring stories
- Don't leave key questions unanswered

## OUTPUT FORMAT

You must provide your response in EXACTLY this format:

---
### SEGMENT SCRIPT

Alex: [dialogue]

Sam: [dialogue]

Alex: [dialogue]

[Continue with full dialogue...]

---
### SEGMENT SUMMARY

**Headline**: [One-line summary of what happened]

**Key Players**: [Companies, people, or organizations involved]

**Category**: [Breaking News / Tech Trends / Security / Product Launch / Policy / etc.]

**Tone**: [Serious / Energetic / Technical / Surprising / Concerning / Lighthearted]

**Key Takeaway**: [One sentence - the main point listeners should remember]

**Duration**: [Estimated minutes]

**Opening Line**: [The very first line of your segment dialogue]

**Closing Line**: [The very last line of your segment dialogue]

---

## ARTICLE TO CONVERT

{article_text}

---

Now write the segment script and summary following all guidelines above.
"""


# =============================================================================
# STAGE 2: SUMMARIES TO SHOW FRAMEWORK
# =============================================================================

SUMMARIES_TO_FRAMEWORK_PROMPT = """# NEWS PODCAST SHOW FRAMEWORK GENERATOR

You are producing the framing elements of a daily news podcast episode. You have multiple 
independent story segments already written—now you need to create the show opening, transitions 
between segments, and show closing.

## YOUR TASK

Using the provided segment summaries, create:
1. **Show Opening**: Energetic intro that previews all stories
2. **Transitions**: Brief bridges between each segment
3. **Show Closing**: Wrap-up and sign-off

This is a NEWS SHOW format. Stories are independent and unrelated. Create a professional, 
energetic frame that holds them together.

## SHOW INFORMATION

**Show Name**: {show_name}
**Episode Date**: {episode_date}
**Number of Stories**: {num_segments}

## OUTPUT FORMAT

You must provide your response in EXACTLY this format:

---
## SHOW OPENING

[Opening dialogue - 60-90 seconds / 150-250 words]

Alex: [greeting and show intro]

Sam: [adds energy]

Alex: [previews all stories briefly]

Sam: [builds excitement]

Alex: [transitions to first story with "Let's start with..." or similar]

---
## TRANSITION 1→2

[Brief bridge - 15-30 seconds / 50-80 words]

Sam: [acknowledges previous story]

Alex: [shifts to next story]

---
## TRANSITION 2→3

[Brief bridge - 15-30 seconds / 50-80 words]

[Continue pattern for each transition needed]

---
## SHOW CLOSING

[Closing dialogue - 45-60 seconds / 100-150 words]

Alex: [begins wrap-up]

Sam: [adds final thought]

Alex: [sign-off]

---

## GUIDELINES

### Show Opening
- Start with energy, not formality
- Greet the audience warmly
- Briefly preview ALL stories (just headlines, not details)
- Create excitement about what's coming
- End with clear transition to first story

Example opening style:
Alex: Hey everyone, welcome to Tech Daily! I'm Alex.

Sam: And I'm Sam. Wednesday, December 11th, and we have got a packed show today.

Alex: We really do. We're starting with some breaking news from OpenAI, then diving into that 
Apple EU situation, and wrapping up with a pretty surprising study about AI coding tools.

Sam: That last one's controversial.

Alex: Oh yeah. Alright, let's jump in...

### Transitions
- Keep them SHORT (2-6 lines total)
- Be direct about topic shifts
- Use phrases like: "Alright, switching gears—", "In other news—", "Moving on—"
- If stories happen to relate, you can briefly note it, but don't force connections
- Match energy between segments

Example transition styles:

For unrelated stories:
Sam: So that's the OpenAI situation—we'll see how that plays out.
Alex: Yeah, definitely. Alright, completely different topic now—

For loosely related stories:
Alex: So that's the Apple news. And actually, staying in the regulatory space—

For tonal shifts:
Sam: Heavy stuff. Alright, on a lighter note—
Alex: Yeah, we need this.

### Show Closing
- Very brief recap (just mention story topics, don't re-explain)
- Keep it short and punchy
- Standard sign-off
- Optional: mention what to watch for or look forward to

Example closing:
Alex: Alright, so today we covered the OpenAI announcement, the Apple EU fine, and that 
fascinating study on AI coding assistants.

Sam: A lot happening in the AI space.

Alex: As always. We'll be back tomorrow with more. Thanks for listening!

Sam: See you then.

## SEGMENT SUMMARIES

{segment_summaries}

---

Now create the show opening, all transitions, and closing following all guidelines above.
"""


# =============================================================================
# HELPER: Format segment summary for Stage 2
# =============================================================================

def format_segment_summary(index: int, summary: str) -> str:
    """Format a single segment summary for inclusion in Stage 2 prompt."""
    return f"""Segment {index + 1}:
{summary}
"""


def format_all_summaries(summaries: list) -> str:
    """Format all segment summaries for Stage 2 prompt."""
    return "\n".join([
        format_segment_summary(i, summary) 
        for i, summary in enumerate(summaries)
    ])