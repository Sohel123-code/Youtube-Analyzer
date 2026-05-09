from textwrap import dedent
import re
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()


def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def get_transcript(video_url: str) -> tuple[str, str]:
    """Fetch transcript/captions for a YouTube video.
    Returns (transcript_text, language) tuple.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        return "ERROR: Could not extract video ID from the URL.", ""
    try:
        ytt_api = YouTubeTranscriptApi()

        # List all available transcripts and pick the best one
        transcript_list = ytt_api.list(video_id)

        # Priority: English manual → English auto → any manual → any auto
        selected = None
        lang = ""
        for t in transcript_list:
            if t.language_code.startswith("en"):
                selected = t
                lang = t.language
                break
        if not selected:
            # Pick the first available transcript (any language)
            for t in transcript_list:
                selected = t
                lang = t.language
                break

        if not selected:
            return "ERROR: No transcripts available for this video.", ""

        transcript = ytt_api.fetch(video_id, languages=[selected.language_code])

        # Format transcript with timestamps
        lines = []
        for entry in transcript:
            minutes = int(entry.start // 60)
            seconds = int(entry.start % 60)
            lines.append(f"[{minutes:02d}:{seconds:02d}] {entry.text}")
        return "\n".join(lines), lang
    except Exception as e:
        return f"ERROR: Could not fetch transcript. {str(e)}", ""


ANALYSIS_INSTRUCTIONS = dedent("""\
You are an expert YouTube content analyst and insight extractor 🎓
Your goal is NOT just to summarize — but to extract maximum value from the video.

You will be given the full transcript of a YouTube video with timestamps.
Base ALL your analysis strictly on the transcript provided. Do NOT make up content.

Follow this structured analysis:

━━━━━━━━━━━━━━━━━━━━━━
1. 🎥 Video Overview
- Title (infer from content), duration, and content type
- Creator intent (educational, promotional, vlog, etc.)
- Target audience (beginner / intermediate / advanced)

━━━━━━━━━━━━━━━━━━━━━━
2. ⏱️ Smart Timestamps (HIGH QUALITY)
- Create meaningful timestamps based on topic transitions
- Format: [start_time - end_time] → Insightful description
- Explain what user learns in each segment
- Highlight demonstrations and practical parts

━━━━━━━━━━━━━━━━━━━━━━
3. 📌 Key Takeaways (MOST IMPORTANT)
- Extract actionable insights (not generic summary)
- Mention exact moments if possible
- Focus on "what user can APPLY"

━━━━━━━━━━━━━━━━━━━━━━
4. 🔥 Best Moments
- Identify most valuable part of video
- Identify most engaging / interesting moment
- Mention timestamps with reason

━━━━━━━━━━━━━━━━━━━━━━
5. 📚 Structured Learning Notes
- Convert content into clean bullet notes
- Make it useful for revision / study
- Keep it simple and clear

━━━━━━━━━━━━━━━━━━━━━━
6. 🧠 Hidden Insights (ADVANCED)
- Identify techniques, patterns, or strategies used

━━━━━━━━━━━━━━━━━━━━━━
7. 📊 Content Quality Analysis
- Beginner Friendly: ⭐ (1–5)
- Practical Value: ⭐ (1–5)
- Depth of Content: ⭐ (1–5)
- Engagement Level: ⭐ (1–5)

━━━━━━━━━━━━━━━━━━━━━━
8. ⚖️ Pros and Cons

━━━━━━━━━━━━━━━━━━━━━━
9. 👤 Personalized Insight

━━━━━━━━━━━━━━━━━━━━━━
10. 🔗 Next Learning Suggestions

Style Guidelines:
- Clean markdown
- Practical insights only
- Only use timestamps that exist in the actual transcript

Final Goal:
Turn the video into a structured knowledge resource.
""")


# 🔹 Function to build agent (no tools — transcript is fetched in Python)
def build_youtube_agent():
    return Agent(
        name="YouTube Agent",
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions=ANALYSIS_INSTRUCTIONS,
        add_datetime_to_context=True,
        markdown=True,
    )


def analyze_video(agent: Agent, video_url: str):
    """Fetch transcript and run analysis."""
    transcript, lang = get_transcript(video_url)
    if transcript.startswith("ERROR:"):
        return transcript

    prompt = f"Analyze this YouTube video.\n\nVideo URL: {video_url}\nTranscript Language: {lang}\n\n--- TRANSCRIPT ---\n{transcript}\n--- END TRANSCRIPT ---"
    response = agent.run(prompt)
    return response.content


# 🔹 Run agent (only when executed directly, not when imported)
if __name__ == "__main__":
    youtube_agent = build_youtube_agent()
    result = analyze_video(youtube_agent, "https://youtu.be/5VEwOBQJGaM?si=pBTvgDgtNcIKSQhi")
    print(result)