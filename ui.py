import streamlit as st
from youtube import build_youtube_agent

st.set_page_config(
    page_title="YouTube Video Analyzer",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Injected CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root palette ── */
:root {
    --red:      #FF2D2D;
    --red-dim:  #C41A1A;
    --dark:     #0A0A0A;
    --surface:  #111111;
    --card:     #181818;
    --border:   #252525;
    --muted:    #666666;
    --white:    #F5F5F5;
    --accent:   #FFD600;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    color: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
footer { display: none !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--red); border-radius: 2px; }

/* ── Hero banner ── */
.hero {
    position: relative;
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 55% at 50% -10%, rgba(255,45,45,0.22) 0%, transparent 70%),
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 59px,
            rgba(255,45,45,0.04) 60px
        ),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 59px,
            rgba(255,45,45,0.04) 60px
        );
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: var(--red);
    color: #fff;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 2px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3.2rem, 9vw, 6rem);
    letter-spacing: 0.05em;
    line-height: 0.95;
    margin: 0 0 0.5rem;
    color: var(--white);
    position: relative;
}
.hero-title span { color: var(--red); }
.hero-sub {
    font-size: 0.88rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.06em;
    margin-top: 0.6rem;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 0.5rem 0 2rem;
}

/* ── Input card ── */
.input-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem 2rem 1.6rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 40px rgba(0,0,0,0.5);
}
.input-label {
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.6rem;
    font-weight: 500;
}

/* Streamlit text input override */
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color .2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 3px rgba(255,45,45,0.12) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label { display: none !important; }

/* ── Button ── */
[data-testid="stButton"] button {
    background: var(--red) !important;
    color: #fff !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.12em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 2.2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: background .2s, transform .1s, box-shadow .2s !important;
    box-shadow: 0 4px 20px rgba(255,45,45,0.25) !important;
}
[data-testid="stButton"] button:hover {
    background: var(--red-dim) !important;
    box-shadow: 0 6px 28px rgba(255,45,45,0.4) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] button:active { transform: translateY(0) !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1.2rem 1.5rem !important;
    color: var(--muted) !important;
    font-size: 0.85rem !important;
}

/* ── Result card ── */
.result-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1.4rem;
}
.result-dot {
    width: 10px; height: 10px;
    background: var(--red);
    border-radius: 50%;
    box-shadow: 0 0 10px rgba(255,45,45,0.7);
    animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: .5; transform: scale(1.35); }
}
.result-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 0.14em;
    color: var(--white);
}
.result-body {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem 1.6rem;
    font-size: 0.88rem;
    line-height: 1.75;
    color: #C8C8C8;
}
.result-body h1,
.result-body h2,
.result-body h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: var(--white) !important;
    letter-spacing: 0.08em;
    margin-top: 1.4rem;
}
.result-body strong { color: var(--accent); font-weight: 500; }
.result-body hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.2rem 0;
}
.result-body ul, .result-body ol {
    padding-left: 1.3rem;
}
.result-body li { margin-bottom: 0.3rem; }

/* ── Footer ── */
.site-footer {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    font-size: 0.72rem;
    color: #333;
    letter-spacing: 0.08em;
}
.site-footer span { color: var(--red); }
</style>
""", unsafe_allow_html=True)


# ── Agent ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_agent():
    return build_youtube_agent()

agent = get_agent()


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">▶ AI-Powered Analysis</div>
    <div class="hero-title">YouTube<br><span>Analyzer</span></div>
    <div class="hero-sub">Drop a link. Get the full picture.</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Input card ─────────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<div class="input-label">🔗 &nbsp;Video URL</div>', unsafe_allow_html=True)
video_url = st.text_input("ENTER YOUTUBE VIDEO LINK", placeholder="https://www.youtube.com/watch?v=...")
button = st.button("⚡  ANALYZE VIDEO")
st.markdown('</div>', unsafe_allow_html=True)


# ── Analysis ───────────────────────────────────────────────────────────────────
if video_url and button:
    with st.spinner("Analyzing video — hang tight …"):
        response = agent.run(f"Analyze this Video {video_url}")

    st.markdown("""
    <div class="result-header">
        <div class="result-dot"></div>
        <div class="result-title">Analysis Report</div>
    </div>
    <div class="result-body">
    """, unsafe_allow_html=True)
    st.markdown(response.content)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="site-footer">Powered by <span>Claude AI</span> &nbsp;·&nbsp; YouTube Analyzer</div>', unsafe_allow_html=True)