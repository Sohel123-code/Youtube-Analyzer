from textwrap import dedent
import re
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
import requests
import yt_dlp
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

def get_transcript_ytdlp(video_url: str) -> tuple[str, str]:
    """Fallback method using yt-dlp to bypass IP blocks."""
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subs = info.get('subtitles', {})
            auto_subs = info.get('automatic_captions', {})
            
            # Combine manual and auto
            all_subs = {**auto_subs, **subs}
            if not all_subs:
                return "ERROR: No transcripts available (yt-dlp fallback).", ""
                
            # Try to get english first, otherwise get first available
            target_lang = 'en' if 'en' in all_subs else list(all_subs.keys())[0]
            sub_formats = all_subs[target_lang]
            
            # Get json3 format
            json3_url = next((s['url'] for s in sub_formats if s.get('ext') == 'json3'), None)
            if not json3_url:
                return "ERROR: Could not find json3 transcript format.", ""
                
            res = requests.get(json3_url).json()
            lines = []
            for event in res.get('events', []):
                if 'segs' in event:
                    text = "".join([seg.get('utf8', '') for seg in event['segs']]).strip()
                    if text and text != '\n':
                        start_ms = event.get('tStartMs', 0)
                        minutes = int(start_ms // 60000)
                        seconds = int((start_ms % 60000) // 1000)
                        lines.append(f"[{minutes:02d}:{seconds:02d}] {text}")
            
            return "\n".join(lines), target_lang
    except Exception as e:
        return f"ERROR: Fallback fetch failed: {str(e)}", ""

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
        error_msg = str(e)
        if "YouTube is blocking requests" in error_msg or "blocked by YouTube" in error_msg:
            # Use yt-dlp fallback
            return get_transcript_ytdlp(video_url)
        return f"ERROR: Could not fetch transcript. {error_msg}", ""


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