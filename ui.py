import streamlit as st
from youtube import build_youtube_agent, analyze_video

st.set_page_config(
    page_title="YouTube Video Analyzer",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Injected CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

/* ── Root palette ── */
:root {
    --red:      #FF2D2D;
    --red-dim:  #C41A1A;
    --red-glow: rgba(255,45,45,0.35);
    --dark:     #0A0A0A;
    --surface:  #111111;
    --card:     #161616;
    --border:   #1E1E1E;
    --muted:    #555555;
    --white:    #F5F5F5;
    --accent:   #FFD600;
}

/* ── Keyframes ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes slideDown {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 15px rgba(255,45,45,0.15), 0 0 40px rgba(255,45,45,0.05); }
    50%      { box-shadow: 0 0 25px rgba(255,45,45,0.3),  0 0 60px rgba(255,45,45,0.1); }
}
@keyframes dotPulse {
    0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 10px var(--red-glow); }
    50%      { opacity: .5; transform: scale(1.4); box-shadow: 0 0 20px var(--red-glow); }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes borderGlow {
    0%, 100% { border-color: var(--border); }
    50%      { border-color: rgba(255,45,45,0.3); }
}
@keyframes floatIn {
    from { opacity: 0; transform: translateY(16px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
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

/* Hide empty Streamlit containers */
[data-testid="stMarkdownContainer"]:empty,
[data-testid="stMarkdownContainer"] > div:empty {
    display: none !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--red), var(--red-dim));
    border-radius: 3px;
}

/* ── Hero banner ── */
.hero {
    position: relative;
    text-align: center;
    padding: 4rem 1rem 2.5rem;
    overflow: hidden;
    animation: fadeIn 0.8s ease-out;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 60% at 50% -15%, rgba(255,45,45,0.18) 0%, transparent 70%),
        radial-gradient(circle at 20% 80%, rgba(255,45,45,0.04) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(255,45,45,0.04) 0%, transparent 50%);
    pointer-events: none;
    animation: fadeIn 1.2s ease-out;
}
.hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        repeating-linear-gradient(90deg, transparent, transparent 59px, rgba(255,45,45,0.025) 60px),
        repeating-linear-gradient(0deg, transparent, transparent 59px, rgba(255,45,45,0.025) 60px);
    pointer-events: none;
    opacity: 0;
    animation: fadeIn 2s ease-out 0.5s forwards;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--red), #FF5252);
    color: #fff;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 3px;
    margin-bottom: 1.4rem;
    animation: fadeInUp 0.6s ease-out 0.2s both;
    box-shadow: 0 2px 12px rgba(255,45,45,0.3);
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3.2rem, 9vw, 6.5rem);
    letter-spacing: 0.05em;
    line-height: 0.92;
    margin: 0 0 0.6rem;
    color: var(--white);
    position: relative;
    animation: fadeInUp 0.7s ease-out 0.35s both;
}
.hero-title span {
    color: var(--red);
    text-shadow: 0 0 40px rgba(255,45,45,0.25);
}
.hero-sub {
    font-size: 0.88rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.08em;
    margin-top: 0.7rem;
    animation: fadeInUp 0.7s ease-out 0.5s both;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,45,45,0.2), var(--border), rgba(255,45,45,0.2), transparent);
    margin: 0.5rem 0 2rem;
    animation: fadeIn 1s ease-out 0.6s both;
}

/* ── Input section ── */
.input-wrap {
    animation: fadeInUp 0.6s ease-out 0.65s both;
}
.input-label {
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
    font-weight: 500;
    transition: color 0.3s ease;
}

/* Streamlit text input */
[data-testid="stTextInput"] {
    transition: all 0.3s ease;
}
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.8rem 1.1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 3px rgba(255,45,45,0.1), 0 4px 20px rgba(255,45,45,0.08) !important;
    outline: none !important;
    background: #131313 !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: #383838 !important;
    transition: color 0.3s ease;
}
[data-testid="stTextInput"] input:focus::placeholder {
    color: #4a4a4a !important;
}
[data-testid="stTextInput"] label { display: none !important; }

/* ── Button ── */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, var(--red), #E52525) !important;
    color: #fff !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.14em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2.2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(255,45,45,0.2), 0 1px 3px rgba(0,0,0,0.3) !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #E52525, var(--red-dim)) !important;
    box-shadow: 0 6px 30px rgba(255,45,45,0.35), 0 2px 8px rgba(0,0,0,0.4) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stButton"] button:active {
    transform: translateY(0) scale(0.98) !important;
    box-shadow: 0 2px 10px rgba(255,45,45,0.2) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.5rem !important;
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    animation: borderGlow 2s ease-in-out infinite, floatIn 0.4s ease-out !important;
}

/* ── Result section ── */
.result-wrap {
    animation: fadeInUp 0.5s ease-out;
}
.result-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1rem;
}
.result-dot {
    width: 10px; height: 10px;
    background: var(--red);
    border-radius: 50%;
    animation: dotPulse 1.8s ease-in-out infinite;
}
.result-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.15rem;
    letter-spacing: 0.15em;
    color: var(--white);
}

/* Target the container wrapping the result markdown */
div[data-testid="stVerticalBlock"]:has(#result-anchor) {
    background: linear-gradient(180deg, var(--surface), #0E0E0E);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.8rem 2rem;
    font-size: 1.05rem; /* Slightly larger text */
    font-weight: 400;   /* Bolder text */
    line-height: 1.8;
    color: #E8E8E8;     /* Brighter color */
    animation: floatIn 0.6s ease-out 0.1s both;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}

div[data-testid="stVerticalBlock"]:has(#result-anchor) h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: var(--white) !important;
    letter-spacing: 0.1em;
    margin-top: 1.8rem;
    margin-bottom: 0.6rem;
    font-size: 1.8rem !important;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) h2 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: var(--white) !important;
    letter-spacing: 0.08em;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    font-size: 1.5rem !important;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: #ddd !important;
    letter-spacing: 0.06em;
    margin-top: 1.2rem;
    font-size: 1.2rem !important;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) strong {
    color: var(--accent);
    font-weight: 600; /* Even bolder for strong text */
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) em {
    color: #aaa;
    font-style: italic;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.4rem 0;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) ul,
div[data-testid="stVerticalBlock"]:has(#result-anchor) ol {
    padding-left: 1.3rem;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) li {
    margin-bottom: 0.35rem;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) code {
    background: rgba(255,45,45,0.08);
    color: #FF6B6B;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.9rem;
}
div[data-testid="stVerticalBlock"]:has(#result-anchor) blockquote {
    border-left: 3px solid var(--red);
    padding-left: 1rem;
    margin: 1rem 0;
    color: #999;
    font-style: italic;
}

/* ── Footer ── */
.site-footer {
    text-align: center;
    padding: 3rem 0 1.5rem;
    font-size: 0.7rem;
    color: #2a2a2a;
    letter-spacing: 0.1em;
    animation: fadeIn 1s ease-out 1s both;
}
.site-footer span { color: var(--red); }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MOBILE RESPONSIVE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
@media (max-width: 768px) {
    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"] {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .hero {
        padding: 2.5rem 0.5rem 1.5rem;
    }
    .hero-title {
        font-size: clamp(2.4rem, 13vw, 4.2rem);
    }
    .hero-sub {
        font-size: 0.78rem;
    }
    .hero-badge {
        font-size: 0.55rem;
        padding: 0.25rem 0.7rem;
    }
    .divider {
        margin: 0.3rem 0 1.2rem;
    }
    [data-testid="stTextInput"] input {
        font-size: 0.84rem !important;
        padding: 0.7rem 0.9rem !important;
        border-radius: 8px !important;
    }
    [data-testid="stButton"] button {
        font-size: 1rem !important;
        padding: 0.65rem 1.2rem !important;
        border-radius: 8px !important;
    }
    .result-body {
        padding: 1.2rem 1rem;
        font-size: 0.83rem;
        line-height: 1.7;
        word-wrap: break-word;
        overflow-wrap: break-word;
        border-radius: 10px;
    }
    .result-body h1 { font-size: 1.3rem !important; }
    .result-body h2 { font-size: 1.1rem !important; }
    .result-body h3 { font-size: 0.95rem !important; }
    .result-body ul, .result-body ol {
        padding-left: 1rem;
    }
    .site-footer {
        padding: 2rem 0 1rem;
        font-size: 0.62rem;
    }
}

@media (max-width: 400px) {
    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"] {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .hero {
        padding: 1.8rem 0.3rem 1rem;
    }
    .hero-title {
        font-size: 2.2rem;
    }
    .result-body {
        padding: 0.9rem 0.75rem;
        font-size: 0.78rem;
    }
}
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


# ── Input section ──────────────────────────────────────────────────────────────
st.markdown('<div class="input-wrap"><div class="input-label">🔗 &nbsp;Video URL</div></div>', unsafe_allow_html=True)
video_url = st.text_input("ENTER YOUTUBE VIDEO LINK", placeholder="https://www.youtube.com/watch?v=...")
button = st.button("⚡  ANALYZE VIDEO")


# ── Analysis ───────────────────────────────────────────────────────────────────
if video_url and button:
    with st.spinner("Fetching transcript & analyzing video — hang tight …"):
        result = analyze_video(agent, video_url)

    if result.startswith("ERROR:"):
        st.error(result)
    else:
        st.markdown("""
        <div class="result-wrap">
            <div class="result-header">
                <div class="result-dot"></div>
                <div class="result-title">Analysis Report</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div id="result-anchor"></div>', unsafe_allow_html=True)
            st.markdown(result)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="site-footer">Powered by <span>Groq AI</span> &nbsp;·&nbsp; YouTube Analyzer</div>', unsafe_allow_html=True)