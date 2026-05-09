from textwrap import dedent
from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
from agno.tools.youtube import YouTubeTools

load_dotenv()


# 🔹 Function to build agent
def build_youtube_agent():
    return Agent(
        name="YouTube Agent",
        model = Groq(id="llama-3.1-70b-versatile"),
        tools=[YouTubeTools()],
        instructions=dedent("""\
You are an expert YouTube content analyst and insight extractor 🎓
Your goal is NOT just to summarize — but to extract maximum value from the video.

Follow this structured analysis:

━━━━━━━━━━━━━━━━━━━━━━
1. 🎥 Video Overview
- Title, duration, and content type
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
- Focus on “what user can APPLY”

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
- No hallucinated timestamps

Final Goal:
Turn the video into a structured knowledge resource.
"""),
        add_datetime_to_context=True,
        markdown=True,
    )



# 🔹 Run agent (only when executed directly, not when imported)
if __name__ == "__main__":
    youtube_agent = build_youtube_agent()
    youtube_agent.print_response(
        "Analyze this video: https://youtu.be/5VEwOBQJGaM?si=pBTvgDgtNcIKSQhi",
        stream=True,
    )