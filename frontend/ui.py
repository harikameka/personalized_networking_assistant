# ============================================================================
# Personalized Networking Assistant — Streamlit Frontend
# ============================================================================
# Premium dark-mode glassmorphic dashboard with 7 interactive pages.
#
# Run with:  streamlit run frontend/ui.py
# Requires:  FastAPI backend running on http://localhost:8000
# ============================================================================

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
API_BASE = "http://127.0.0.1:8000/api"
SESSION_ID = str(uuid.uuid4())[:8]


# ============================================================================
#  CSS DESIGN SYSTEM
# ============================================================================

def inject_custom_css() -> None:
    """
    Inject the full custom CSS design system.  This creates a premium
    SaaS-grade dark-mode interface with glassmorphism, gradient buttons,
    hover animations, and modern typography.
    """
    st.markdown(
        """
        <style>
        /* ── Google Font ─────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        /* ── CSS Variables ───────────────────────────────────────────── */
        :root {
            --bg-primary: #0a0a1a;
            --bg-secondary: #111128;
            --bg-card: rgba(255, 255, 255, 0.04);
            --bg-card-hover: rgba(255, 255, 255, 0.08);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-border-hover: rgba(255, 255, 255, 0.15);
            --text-primary: #e8e8f0;
            --text-secondary: #9898b0;
            --text-muted: #6868808;
            --accent-blue: #6c63ff;
            --accent-purple: #9b59b6;
            --accent-cyan: #00d2ff;
            --accent-pink: #ff6b9d;
            --accent-green: #00e676;
            --accent-orange: #ff9800;
            --gradient-primary: linear-gradient(135deg, #6c63ff 0%, #00d2ff 100%);
            --gradient-warm: linear-gradient(135deg, #ff6b9d 0%, #ff9800 100%);
            --gradient-cool: linear-gradient(135deg, #00d2ff 0%, #00e676 100%);
            --gradient-bg: linear-gradient(160deg, #0a0a1a 0%, #111128 40%, #16213e 100%);
            --radius-sm: 8px;
            --radius-md: 14px;
            --radius-lg: 20px;
            --radius-xl: 28px;
            --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.35);
            --shadow-glow: 0 0 30px rgba(108, 99, 255, 0.15);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* ── Global Resets ───────────────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {
            background: var(--gradient-bg) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ── Hide Streamlit Chrome ───────────────────────────────────── */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {
            background: transparent !important;
            backdrop-filter: blur(20px);
        }
        [data-testid="stToolbar"] {display: none;}

        /* ── Sidebar ─────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(17,17,40,0.95) 0%, rgba(10,10,26,0.98) 100%) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--glass-border);
        }
        [data-testid="stSidebar"] .stRadio > label {
            color: var(--text-secondary) !important;
            font-size: 0.8rem !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
        }
        [data-testid="stSidebar"] .stRadio > div {
            gap: 2px !important;
        }
        [data-testid="stSidebar"] .stRadio > div > label {
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: var(--radius-sm) !important;
            padding: 10px 16px !important;
            color: var(--text-secondary) !important;
            font-size: 0.95rem !important;
            font-weight: 500;
            transition: var(--transition);
            cursor: pointer;
        }
        [data-testid="stSidebar"] .stRadio > div > label:hover {
            background: var(--bg-card-hover) !important;
            border-color: var(--glass-border-hover) !important;
            color: var(--text-primary) !important;
        }
        [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
        [data-testid="stSidebar"] .stRadio > div [data-checked="true"] {
            background: rgba(108, 99, 255, 0.12) !important;
            border-color: rgba(108, 99, 255, 0.4) !important;
            color: var(--accent-blue) !important;
        }

        /* ── Glass Cards ─────────────────────────────────────────────── */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: var(--shadow-card);
            transition: var(--transition);
        }
        .glass-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--glass-border-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow-card), var(--shadow-glow);
        }

        /* ── Stat Cards ──────────────────────────────────────────────── */
        .stat-card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 24px;
            text-align: center;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--gradient-primary);
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-card), var(--shadow-glow);
            border-color: var(--glass-border-hover);
        }
        .stat-icon {
            font-size: 2rem;
            margin-bottom: 8px;
        }
        .stat-value {
            font-size: 2.2rem;
            font-weight: 800;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* ── Hero Section ────────────────────────────────────────────── */
        .hero-section {
            text-align: center;
            padding: 60px 20px 40px;
            position: relative;
        }
        .hero-section::before {
            content: '';
            position: absolute;
            top: -60px; left: 50%;
            transform: translateX(-50%);
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(108,99,255,0.12) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero-title {
            font-size: 3.2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #e8e8f0 0%, #6c63ff 50%, #00d2ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
            line-height: 1.15;
        }
        .hero-subtitle {
            color: var(--text-secondary);
            font-size: 1.15rem;
            font-weight: 400;
            max-width: 640px;
            margin: 0 auto 36px;
            line-height: 1.6;
        }

        /* ── Feature Cards Grid ──────────────────────────────────────── */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 18px;
            margin-top: 24px;
        }
        .feature-card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 28px 22px;
            transition: var(--transition);
            text-align: left;
        }
        .feature-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--glass-border-hover);
            transform: translateY(-3px);
            box-shadow: var(--shadow-card), var(--shadow-glow);
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 14px;
            display: block;
        }
        .feature-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        .feature-desc {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.55;
        }

        /* ── Result Cards ────────────────────────────────────────────── */
        .result-card {
            background: linear-gradient(135deg, rgba(108,99,255,0.06) 0%, rgba(0,210,255,0.04) 100%);
            border: 1px solid rgba(108,99,255,0.2);
            border-radius: var(--radius-md);
            padding: 22px;
            margin-bottom: 14px;
            transition: var(--transition);
        }
        .result-card:hover {
            border-color: rgba(108,99,255,0.4);
            background: linear-gradient(135deg, rgba(108,99,255,0.1) 0%, rgba(0,210,255,0.06) 100%);
            transform: translateY(-2px);
        }
        .result-number {
            display: inline-block;
            background: var(--gradient-primary);
            color: white;
            width: 28px; height: 28px;
            border-radius: 50%;
            text-align: center;
            line-height: 28px;
            font-size: 0.85rem;
            font-weight: 700;
            margin-right: 12px;
        }

        /* ── Category Badges ─────────────────────────────────────────── */
        .badge {
            display: inline-block;
            padding: 5px 14px;
            border-radius: 50px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 4px 4px 4px 0;
        }
        .badge-blue { background: rgba(108,99,255,0.15); color: #8b83ff; border: 1px solid rgba(108,99,255,0.3); }
        .badge-cyan { background: rgba(0,210,255,0.12); color: #33deff; border: 1px solid rgba(0,210,255,0.3); }
        .badge-green { background: rgba(0,230,118,0.12); color: #33eb93; border: 1px solid rgba(0,230,118,0.3); }
        .badge-pink { background: rgba(255,107,157,0.12); color: #ff8db7; border: 1px solid rgba(255,107,157,0.3); }
        .badge-orange { background: rgba(255,152,0,0.12); color: #ffb333; border: 1px solid rgba(255,152,0,0.3); }

        /* ── Buttons ─────────────────────────────────────────────────── */
        .stButton > button {
            background: var(--gradient-primary) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
            padding: 10px 28px !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            letter-spacing: 0.3px;
            transition: var(--transition) !important;
            box-shadow: 0 4px 15px rgba(108,99,255,0.25);
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px rgba(108,99,255,0.4) !important;
        }
        .stButton > button:active {
            transform: translateY(0) !important;
        }

        /* ── Inputs ──────────────────────────────────────────────────── */
        /* Input Fields */
.stTextInput input,
.stTextArea textarea,
textarea,
input {
    background-color: #1e1e2f !important;
    color: #ffffff !important;
    caret-color: #00d2ff !important;
    border: 1px solid #6c63ff !important;
    border-radius: 8px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #9ca3af !important;
    opacity: 1;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
textarea:focus,
input:focus {
    border: 2px solid #00d2ff !important;
    outline: none !important;
    box-shadow: 0 0 10px rgba(0,210,255,.4) !important;
}
        /* ── Expanders ───────────────────────────────────────────────── */
        .streamlit-expanderHeader {
            background: var(--bg-card) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }
        .streamlit-expanderContent {
            background: rgba(255,255,255,0.02) !important;
            border: 1px solid var(--glass-border) !important;
            border-top: none !important;
        }

        /* ── Metrics ─────────────────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-md) !important;
            padding: 18px !important;
            transition: var(--transition);
        }
        [data-testid="stMetric"]:hover {
            border-color: var(--glass-border-hover) !important;
            transform: translateY(-2px);
        }
        [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
        }

        /* ── DataFrame / Tables ──────────────────────────────────────── */
        .stDataFrame {
            border-radius: var(--radius-md) !important;
            overflow: hidden;
        }
        [data-testid="stDataFrame"] > div {
            background: var(--bg-card) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-md) !important;
        }

        /* ── Scrollbar ───────────────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(108,99,255,0.3);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(108,99,255,0.5);
        }

        /* ── Section Headers ─────────────────────────────────────────── */
        .section-header {
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--text-primary);
            margin-bottom: 6px;
            margin-top: 10px;
        }
        .section-subheader {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 24px;
            line-height: 1.5;
        }

        /* ── Dividers ────────────────────────────────────────────────── */
        hr {
            border: none;
            height: 1px;
            background: var(--glass-border);
            margin: 32px 0;
        }

        /* ── Tabs ────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: var(--bg-card);
            border-radius: var(--radius-sm);
            padding: 4px;
            border: 1px solid var(--glass-border);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: var(--radius-sm);
            padding: 8px 20px;
            color: var(--text-secondary);
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(108,99,255,0.15) !important;
            color: var(--accent-blue) !important;
        }

        /* ── Progress bar ────────────────────────────────────────────── */
        .stProgress > div > div {
            background: var(--gradient-primary) !important;
            border-radius: 10px;
        }

        /* ── Toast / Success / Error ─────────────────────────────────── */
        .stAlert {
            background: var(--bg-card) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: var(--radius-sm) !important;
        }

        /* ── Animations ──────────────────────────────────────────────── */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50%      { opacity: 0.6; }
        }
        .animate-in {
            animation: fadeInUp 0.5s ease-out;
        }
        .pulse {
            animation: pulse 2s ease-in-out infinite;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
#  HELPER FUNCTIONS
# ============================================================================

def api_call(method: str, endpoint: str, payload: dict | None = None) -> dict | list | None:
    """
    Make a request to the FastAPI backend.  Returns parsed JSON on success,
    None on failure.
    """
    url = f"{API_BASE}{endpoint}"
    try:
        if method.upper() == "GET":
            resp = requests.get(url, timeout=60)
        elif method.upper() == "POST":
            resp = requests.post(url, json=payload, timeout=60)
        elif method.upper() == "DELETE":
            resp = requests.delete(url, timeout=60)
        else:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to the backend. Make sure the FastAPI server is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The backend might be busy processing.")
        return None
    except Exception as exc:
        st.error(f"❌ API Error: {exc}")
        return None


def render_badge(text: str, variant: str = "blue") -> str:
    """Return HTML for a styled badge."""
    return f'<span class="badge badge-{variant}">{text}</span>'


def render_stat_card(icon: str, value: str, label: str) -> str:
    """Return HTML for a stat card."""
    return f"""
    <div class="stat-card">
        <div class="stat-icon">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


# ============================================================================
#  PAGE: HOME
# ============================================================================

def page_home() -> None:
    """Render the Home dashboard with hero, stats, features, and activity."""

    # ── Hero Section ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-section animate-in">
            <div class="hero-title">🎯 Personalized Networking Assistant</div>
            <div class="hero-subtitle">
                AI-powered conversation intelligence for professional networking.
                Generate smart starters, verify facts, and track your networking journey
                — all in one premium dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Quick Action Buttons ────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🎯 Generate Starters", use_container_width=True):
            st.session_state["nav"] = "🎯 Smart Prompt Generator"
            st.rerun()
    with col2:
        if st.button("🔍 Fact Check", use_container_width=True):
            st.session_state["nav"] = "🔍 Wikipedia Fact Checker"
            st.rerun()
    with col3:
        if st.button("📜 View History", use_container_width=True):
            st.session_state["nav"] = "📜 Conversation History"
            st.rerun()
    with col4:
        if st.button("⭐ Give Feedback", use_container_width=True):
            st.session_state["nav"] = "⭐ Feedback"
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Live Stats ──────────────────────────────────────────────────────
    stats = api_call("GET", "/stats")
    if stats:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(render_stat_card("💬", str(stats.get("total_conversations", 0)), "Conversations"), unsafe_allow_html=True)
        with c2:
            st.markdown(render_stat_card("🚀", str(stats.get("total_starters_generated", 0)), "Starters Generated"), unsafe_allow_html=True)
        with c3:
            st.markdown(render_stat_card("⭐", str(stats.get("average_rating", 0)), "Avg Rating"), unsafe_allow_html=True)
        with c4:
            st.markdown(render_stat_card("📝", str(stats.get("total_feedback", 0)), "Feedback Entries"), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Feature Cards ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">✨ Core Features</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Everything you need to master professional networking</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="features-grid">
            <div class="feature-card">
                <span class="feature-icon">🧠</span>
                <div class="feature-title">AI Event Analysis</div>
                <div class="feature-desc">DistilBERT zero-shot classification extracts contextual themes from any event description in seconds.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">💡</span>
                <div class="feature-title">Smart Conversation Starters</div>
                <div class="feature-desc">GPT-2 generates tailored networking openers aligned with your interests and the event context.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔍</span>
                <div class="feature-title">Wikipedia Fact Check</div>
                <div class="feature-desc">Instantly verify topics with reliable Wikipedia summaries before your next conversation.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📊</span>
                <div class="feature-title">Analytics Dashboard</div>
                <div class="feature-desc">Track your networking patterns with real-time metrics, charts, and progress insights.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📜</span>
                <div class="feature-title">Conversation History</div>
                <div class="feature-desc">Review, search, filter, and export your past conversation strategies to refine your approach.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">⭐</span>
                <div class="feature-title">Feedback Loop</div>
                <div class="feature-desc">Rate suggestions and provide feedback to continuously improve personalization quality.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Recent Activity ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">🕐 Recent Activity</div>', unsafe_allow_html=True)
    history = api_call("GET", "/history")
    if history and len(history) > 0:
        for entry in reversed(history[-5:]):
            ts = entry.get("timestamp", "")[:19]
            desc = entry.get("event_description", "")[:80]
            cats = ", ".join(entry.get("categories", []))
            st.markdown(
                f"""
                <div class="glass-card" style="padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:600; color:var(--text-primary); margin-bottom:4px;">{desc}{'…' if len(entry.get('event_description', '')) > 80 else ''}</div>
                            <div style="font-size:0.85rem; color:var(--text-secondary);">{cats}</div>
                        </div>
                        <div style="color:var(--text-muted); font-size:0.8rem; white-space:nowrap;">{ts}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center; padding:40px;">
                <div style="font-size:2.5rem; margin-bottom:12px;">🌟</div>
                <div style="color:var(--text-secondary);">No activity yet. Generate your first conversation starters to get started!</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================================
#  PAGE: SMART PROMPT GENERATOR
# ============================================================================

def page_generator() -> None:
    """Render the conversation-starter generator page."""

    st.markdown('<div class="section-header animate-in">🎯 Smart Prompt Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Describe your event and interests — our AI will craft perfect conversation openers</div>', unsafe_allow_html=True)

    # ── Input Form ──────────────────────────────────────────────────────
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        event_desc = st.text_area(
            "📋 Event Description",
            placeholder="e.g., AI for Sustainable Cities summit focusing on urban tech and green infrastructure",
            height=120,
            key="gen_event",
        )
        interests_input = st.text_input(
            "🎯 Your Interests (comma-separated)",
            placeholder="e.g., climate change, urban planning, smart cities",
            key="gen_interests",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Action Buttons ──────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        generate_btn = st.button("🚀 Generate Conversation Starters", use_container_width=True, key="btn_generate")
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True, key="btn_clear")
    with col3:
        export_btn = st.button("📥 Export", use_container_width=True, key="btn_export")

    # ── Clear ───────────────────────────────────────────────────────────
    if clear_btn:
        for key in ["gen_results", "gen_categories"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # ── Generate ────────────────────────────────────────────────────────
    if generate_btn:
        if not event_desc or not interests_input:
            st.warning("⚠️ Please fill in both the event description and your interests.")
            return

        interests = [i.strip() for i in interests_input.split(",") if i.strip()]

        with st.spinner(""):
            # Show a custom loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown(
                """
                <div class="glass-card" style="text-align:center; padding:40px;">
                    <div class="pulse" style="font-size:3rem;">🧠</div>
                    <div style="color:var(--text-secondary); margin-top:12px; font-weight:500;">
                        Analyzing event context & generating starters…
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            result = api_call("POST", "/generate", {
                "event_description": event_desc,
                "user_interests": interests,
            })
            loading_placeholder.empty()

        if result:
            st.session_state["gen_results"] = result.get("conversation_starters", [])
            st.session_state["gen_categories"] = result.get("categories", [])

    # ── Display Results ─────────────────────────────────────────────────
    if "gen_categories" in st.session_state and st.session_state["gen_categories"]:
        st.markdown("<hr>", unsafe_allow_html=True)

        # Categories
        st.markdown('<div class="section-header" style="font-size:1.2rem;">📂 Detected Categories</div>', unsafe_allow_html=True)
        badge_colors = ["blue", "cyan", "green", "pink", "orange"]
        badges_html = " ".join(
            render_badge(cat, badge_colors[i % len(badge_colors)])
            for i, cat in enumerate(st.session_state["gen_categories"])
        )
        st.markdown(f'<div style="margin-bottom:24px;">{badges_html}</div>', unsafe_allow_html=True)

        # Starters
        st.markdown('<div class="section-header" style="font-size:1.2rem;">💬 Conversation Starters</div>', unsafe_allow_html=True)
        starters = st.session_state.get("gen_results", [])
        for i, starter in enumerate(starters, 1):
            with st.expander(f"💡 Starter #{i}", expanded=True):
                st.markdown(
                    f"""
                    <div class="result-card">
                        <span class="result-number">{i}</span>
                        <span style="color:var(--text-primary); font-size:1rem; line-height:1.6;">{starter}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Copy button (uses st.code for copyability)
                st.code(starter, language=None)

    # ── Export ──────────────────────────────────────────────────────────
    if export_btn and "gen_results" in st.session_state:
        export_data = {
            "categories": st.session_state.get("gen_categories", []),
            "conversation_starters": st.session_state.get("gen_results", []),
            "exported_at": datetime.now().isoformat(),
        }
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"conversation_starters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )


# ============================================================================
#  PAGE: FACT CHECKER
# ============================================================================

def page_fact_checker() -> None:
    """Render the Wikipedia fact-check page."""

    st.markdown('<div class="section-header animate-in">🔍 Wikipedia Fact Checker</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Quickly verify topics with reliable Wikipedia summaries</div>', unsafe_allow_html=True)

    # ── Search Form ─────────────────────────────────────────────────────
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "🔎 Search Topic",
            placeholder="e.g., Blockchain in healthcare, Artificial Intelligence, Climate Change",
            key="fc_query",
            label_visibility="collapsed",
        )
    with col2:
        search_btn = st.button("🔍 Search", use_container_width=True, key="btn_search")

    # ── Perform Search ──────────────────────────────────────────────────
    if search_btn and query:
        with st.spinner(""):
            loading = st.empty()
            loading.markdown(
                """
                <div class="glass-card" style="text-align:center; padding:40px;">
                    <div class="pulse" style="font-size:3rem;">🔍</div>
                    <div style="color:var(--text-secondary); margin-top:12px;">Searching Wikipedia…</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            result = api_call("POST", "/fact-check", {"query": query})
            loading.empty()

        if result:
            st.session_state["fc_result"] = result

    # ── Display Result ──────────────────────────────────────────────────
    if "fc_result" in st.session_state:
        result = st.session_state["fc_result"]
        status = result.get("status", "error")

        # Status badge
        if status == "found":
            status_color = "green"
            status_icon = "✅"
        elif status == "not_found":
            status_color = "orange"
            status_icon = "⚠️"
        else:
            status_color = "pink"
            status_icon = "❌"

        st.markdown("<hr>", unsafe_allow_html=True)

        # Main result card
        st.markdown(
            f"""
            <div class="glass-card animate-in">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                    <div style="font-size:1.4rem; font-weight:700; color:var(--text-primary);">
                        {result.get('title', 'Unknown')}
                    </div>
                    {render_badge(f"{status_icon} {status.upper()}", status_color)}
                </div>
                <div style="color:var(--text-secondary); line-height:1.7; font-size:0.95rem; margin-bottom:16px;">
                    {result.get('summary', 'No summary available.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # URL link
        url = result.get("url", "")
        if url:
            st.markdown(
                f"""
                <div class="glass-card" style="padding:16px;">
                    <div style="font-weight:600; color:var(--text-primary); margin-bottom:8px;">🔗 Wikipedia URL</div>
                    <a href="{url}" target="_blank" style="color:var(--accent-cyan); text-decoration:none; word-break:break-all;">
                        {url}
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Related topics
        related = result.get("related_topics", [])
        if related:
            st.markdown(
                f"""
                <div class="glass-card" style="padding:16px;">
                    <div style="font-weight:600; color:var(--text-primary); margin-bottom:8px;">🏷️ Related Topics</div>
                    <div>{"  ".join(render_badge(t, "cyan") for t in related)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================================
#  PAGE: CONVERSATION HISTORY
# ============================================================================

def page_history() -> None:
    """Render the conversation history page with table, search, and export."""

    st.markdown('<div class="section-header animate-in">📜 Conversation History</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Review, search, and export your past conversation strategies</div>', unsafe_allow_html=True)

    history = api_call("GET", "/history")

    if not history:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center; padding:50px;">
                <div style="font-size:3rem; margin-bottom:12px;">📭</div>
                <div style="color:var(--text-secondary); font-size:1.1rem;">No conversation history yet.</div>
                <div style="color:var(--text-muted); font-size:0.9rem; margin-top:6px;">Generate your first conversation starters to see them here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Controls ────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_term = st.text_input("🔎 Search history", placeholder="Filter by keyword…", key="hist_search", label_visibility="collapsed")
    with col2:
        export_csv = st.button("📥 Export CSV", use_container_width=True, key="btn_export_csv")
    with col3:
        delete_all = st.button("🗑️ Clear All", use_container_width=True, key="btn_delete_hist")

    # ── Filter ──────────────────────────────────────────────────────────
    if search_term:
        term = search_term.lower()
        history = [
            h for h in history
            if term in h.get("event_description", "").lower()
            or term in " ".join(h.get("categories", [])).lower()
            or term in " ".join(h.get("interests", [])).lower()
        ]

    # ── DataFrame ───────────────────────────────────────────────────────
    df_data = []
    for h in history:
        df_data.append({
            "Timestamp": h.get("timestamp", "")[:19],
            "Event": h.get("event_description", "")[:60],
            "Interests": ", ".join(h.get("interests", [])),
            "Categories": ", ".join(h.get("categories", [])),
            "Starters": len(h.get("conversation_starters", [])),
        })

    df = pd.DataFrame(df_data)
    if not df.empty:
        st.markdown(f'<div style="color:var(--text-secondary); margin-bottom:12px;">Showing <strong>{len(df)}</strong> entries</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Detailed View ───────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="font-size:1.2rem;">📋 Detailed View</div>', unsafe_allow_html=True)

        for i, entry in enumerate(reversed(history[-10:])):
            with st.expander(
                f"🗓️ {entry.get('timestamp', '')[:19]} — {entry.get('event_description', '')[:50]}…"
            ):
                st.markdown("**Event:**")
                st.write(entry.get("event_description", ""))
                st.markdown("**Interests:**")
                interests_badges = " ".join(render_badge(i, "blue") for i in entry.get("interests", []))
                st.markdown(interests_badges, unsafe_allow_html=True)
                st.markdown("**Categories:**")
                cat_badges = " ".join(render_badge(c, "cyan") for c in entry.get("categories", []))
                st.markdown(cat_badges, unsafe_allow_html=True)
                st.markdown("**Generated Starters:**")
                for j, s in enumerate(entry.get("conversation_starters", []), 1):
                    st.markdown(f"> **{j}.** {s}")

    # ── Export CSV ──────────────────────────────────────────────────────
    if export_csv and not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    # ── Delete All ──────────────────────────────────────────────────────
    if delete_all:
        result = api_call("DELETE", "/history")
        if result:
            st.success(f"✅ Cleared {result.get('deleted', 0)} history entries.")
            time.sleep(1)
            st.rerun()


# ============================================================================
#  PAGE: ANALYTICS DASHBOARD
# ============================================================================

def page_analytics() -> None:
    """Render the analytics dashboard with metrics, charts, and progress."""

    st.markdown('<div class="section-header animate-in">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Track your networking progress and AI usage patterns</div>', unsafe_allow_html=True)

    stats = api_call("GET", "/stats")
    history = api_call("GET", "/history")
    feedback = api_call("GET", "/feedback")

    if not stats:
        st.info("📊 Analytics will appear here once you start using the assistant.")
        return

    # ── Key Metrics ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="💬 Total Conversations",
            value=stats.get("total_conversations", 0),
        )
    with c2:
        st.metric(
            label="🚀 Starters Generated",
            value=stats.get("total_starters_generated", 0),
        )
    with c3:
        st.metric(
            label="⭐ Avg Rating",
            value=f"{stats.get('average_rating', 0):.1f} / 5",
        )
    with c4:
        st.metric(
            label="📝 Feedback Count",
            value=stats.get("total_feedback", 0),
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Charts ──────────────────────────────────────────────────────────
    if history and len(history) > 0:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-header" style="font-size:1.1rem;">📈 Activity Over Time</div>', unsafe_allow_html=True)
            # Build a simple date-count series
            dates = []
            for h in history:
                ts = h.get("timestamp", "")[:10]
                dates.append(ts)
            date_df = pd.DataFrame({"date": dates})
            date_counts = date_df["date"].value_counts().sort_index().reset_index()
            date_counts.columns = ["Date", "Conversations"]
            st.bar_chart(date_counts.set_index("Date"), use_container_width=True)

        with col2:
            st.markdown('<div class="section-header" style="font-size:1.1rem;">🏷️ Top Categories</div>', unsafe_allow_html=True)
            all_cats = []
            for h in history:
                all_cats.extend(h.get("categories", []))
            if all_cats:
                cat_df = pd.DataFrame({"category": all_cats})
                cat_counts = cat_df["category"].value_counts().head(8).reset_index()
                cat_counts.columns = ["Category", "Count"]
                st.bar_chart(cat_counts.set_index("Category"), use_container_width=True)
            else:
                st.info("No category data yet.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Progress Indicators ─────────────────────────────────────────────
    st.markdown('<div class="section-header" style="font-size:1.1rem;">📊 Progress</div>', unsafe_allow_html=True)

    total_conv = stats.get("total_conversations", 0)
    goal = max(total_conv, 20)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="font-weight:600; color:var(--text-primary); margin-bottom:8px;">
                    🎯 Conversation Goal
                </div>
                <div style="color:var(--text-secondary); font-size:0.9rem; margin-bottom:12px;">
                    {total_conv} of {goal} conversations
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(min(total_conv / goal, 1.0))

    with col2:
        avg = stats.get("average_rating", 0)
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="font-weight:600; color:var(--text-primary); margin-bottom:8px;">
                    ⭐ Satisfaction Score
                </div>
                <div style="color:var(--text-secondary); font-size:0.9rem; margin-bottom:12px;">
                    {avg:.1f} / 5.0 average rating
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(min(avg / 5.0, 1.0))

    # ── Feedback Breakdown ──────────────────────────────────────────────
    if feedback and len(feedback) > 0:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="font-size:1.1rem;">⭐ Rating Distribution</div>', unsafe_allow_html=True)

        ratings = [f.get("rating", 0) for f in feedback]
        rating_df = pd.DataFrame({"Rating": ratings})
        rating_counts = rating_df["Rating"].value_counts().sort_index().reset_index()
        rating_counts.columns = ["Stars", "Count"]
        st.bar_chart(rating_counts.set_index("Stars"), use_container_width=True)


# ============================================================================
#  PAGE: FEEDBACK
# ============================================================================

def page_feedback() -> None:
    """Render the feedback submission and history page."""

    st.markdown('<div class="section-header animate-in">⭐ Feedback</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subheader">Rate your experience and help us improve the assistant</div>', unsafe_allow_html=True)

    # ── Emoji Rating ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="glass-card" style="text-align:center; padding:32px;">
            <div style="font-size:1.2rem; font-weight:600; color:var(--text-primary); margin-bottom:16px;">
                How would you rate your experience?
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Star rating via columns
    star_cols = st.columns(5)
    star_labels = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    rating_descriptions = ["Poor", "Fair", "Good", "Very Good", "Excellent"]

    if "fb_rating" not in st.session_state:
        st.session_state["fb_rating"] = 0

    for i, col in enumerate(star_cols):
        with col:
            if st.button(
                f"{'⭐' * (i + 1)}",
                key=f"star_{i+1}",
                use_container_width=True,
            ):
                st.session_state["fb_rating"] = i + 1

    if st.session_state["fb_rating"] > 0:
        r = st.session_state["fb_rating"]
        st.markdown(
            f"""
            <div style="text-align:center; color:var(--accent-cyan); font-weight:600; font-size:1.1rem; margin:12px 0;">
                {rating_descriptions[r-1]} ({r}/5)
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Comment ─────────────────────────────────────────────────────────
    comment = st.text_area(
        "💬 Comments (optional)",
        placeholder="Tell us what you liked or what we can improve…",
        height=120,
        key="fb_comment",
    )

    # ── Submit ──────────────────────────────────────────────────────────
    if st.button("📤 Submit Feedback", use_container_width=True, key="btn_submit_fb"):
        if st.session_state["fb_rating"] == 0:
            st.warning("⚠️ Please select a rating before submitting.")
        else:
            result = api_call("POST", "/feedback", {
                "rating": st.session_state["fb_rating"],
                "comment": comment or "",
                "session_id": SESSION_ID,
            })
            if result:
                st.success("🎉 Thank you for your feedback!")
                st.session_state["fb_rating"] = 0
                time.sleep(1)
                st.rerun()

    # ── Previous Feedback ───────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header" style="font-size:1.2rem;">📋 Previous Feedback</div>', unsafe_allow_html=True)

    feedback = api_call("GET", "/feedback")
    if feedback and len(feedback) > 0:
        for entry in reversed(feedback[-10:]):
            rating = entry.get("rating", 0)
            stars = "⭐" * rating
            ts = entry.get("timestamp", "")[:19]
            cmt = entry.get("comment", "")
            st.markdown(
                f"""
                <div class="glass-card" style="padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-size:1.2rem;">{stars}</div>
                        <div style="color:var(--text-muted); font-size:0.8rem;">{ts}</div>
                    </div>
                    <div style="color:var(--text-secondary); font-size:0.9rem;">{cmt if cmt else '<em>No comment</em>'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center; padding:30px;">
                <div style="color:var(--text-secondary);">No feedback submitted yet.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================================
#  PAGE: SETTINGS & ABOUT
# ============================================================================

def page_settings() -> None:
    """Render the settings and about page."""

    st.markdown('<div class="section-header animate-in">⚙️ Settings & About</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⚙️ Configuration", "ℹ️ About"])

    with tab1:
        st.markdown('<div class="section-header" style="font-size:1.2rem;">🔧 Backend Configuration</div>', unsafe_allow_html=True)

        # Display current configuration
        health = api_call("GET", "/health")
        if health:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                        <div>
                            <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Status</div>
                            <div style="color:var(--accent-green); font-weight:600; margin-top:4px;">🟢 {health.get('status', 'unknown').upper()}</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Version</div>
                            <div style="color:var(--text-primary); font-weight:600; margin-top:4px;">{health.get('version', '-')}</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">API Endpoint</div>
                            <div style="color:var(--accent-cyan); font-weight:600; margin-top:4px;">{API_BASE}</div>
                        </div>
                        <div>
                            <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Session ID</div>
                            <div style="color:var(--text-primary); font-weight:600; margin-top:4px;">{SESSION_ID}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.error("⚠️ Backend is not reachable.")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="font-size:1.2rem;">🤖 AI Models</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="glass-card">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                    <div>
                        <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Classifier</div>
                        <div style="color:var(--text-primary); font-weight:600; margin-top:4px;">typeform/distilbert-base-uncased-mnli</div>
                        <div style="color:var(--text-secondary); font-size:0.85rem; margin-top:2px;">Zero-shot classification</div>
                    </div>
                    <div>
                        <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Generator</div>
                        <div style="color:var(--text-primary); font-weight:600; margin-top:4px;">GPT-2</div>
                        <div style="color:var(--text-secondary); font-size:0.85rem; margin-top:2px;">Text generation</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-header" style="font-size:1.2rem;">🗄️ Storage</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="glass-card">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                    <div>
                        <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">History File</div>
                        <div style="color:var(--text-primary); font-weight:600; margin-top:4px;">data/history.json</div>
                    </div>
                    <div>
                        <div style="color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Feedback File</div>
                        <div style="color:var(--text-primary); font-weight:600; margin-top:4px;">data/feedback.json</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab2:
        st.markdown(
            """
            <div class="glass-card animate-in" style="text-align:center; padding:48px;">
                <div style="font-size:4rem; margin-bottom:16px;">🎯</div>
                <div style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg, #e8e8f0 0%, #6c63ff 50%, #00d2ff 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:12px;">
                    Personalized Networking Assistant
                </div>
                <div style="color:var(--text-secondary); font-size:1rem; max-width:500px; margin:0 auto; line-height:1.7;">
                    An AI-powered platform that helps professionals generate smart,
                    tailored conversation starters for networking events. Built with
                    DistilBERT, GPT-2, FastAPI, and Streamlit.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="features-grid">
                <div class="feature-card">
                    <span class="feature-icon">⚡</span>
                    <div class="feature-title">Tech Stack</div>
                    <div class="feature-desc">FastAPI · Streamlit · Transformers · PyTorch · Pydantic · Pandas</div>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">🏗️</span>
                    <div class="feature-title">Architecture</div>
                    <div class="feature-desc">Clean 3-tier decoupled pattern with separate backend services, routers, and frontend.</div>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">🔒</span>
                    <div class="feature-title">Data Privacy</div>
                    <div class="feature-desc">All data stored locally in JSON files. No external data collection or tracking.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================================
#  MAIN APPLICATION
# ============================================================================

def main() -> None:
    """Application entry point — configures the page and routes navigation."""

    # ── Page Configuration ──────────────────────────────────────────────
    st.set_page_config(
        page_title="Networking Assistant",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Inject CSS Design System ────────────────────────────────────────
    inject_custom_css()

    # ── Sidebar Navigation ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding:24px 0 20px;">
                <div style="font-size:2.2rem;">🎯</div>
                <div style="font-size:1.1rem; font-weight:800; background:linear-gradient(135deg, #e8e8f0, #6c63ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-top:4px;">
                    Networking<br/>Assistant
                </div>
                <div style="color:var(--text-muted); font-size:0.7rem; margin-top:6px; letter-spacing:1px; text-transform:uppercase;">
                    AI-Powered v1.0
                </div>
            </div>
            <hr style="margin:0 0 12px; border-color:rgba(255,255,255,0.06);">
            """,
            unsafe_allow_html=True,
        )

        # Navigation radio
        pages = [
            "🏠 Home",
            "🎯 Smart Prompt Generator",
            "🔍 Wikipedia Fact Checker",
            "📜 Conversation History",
            "📊 Analytics Dashboard",
            "⭐ Feedback",
            "⚙️ Settings & About",
        ]

        # Respect programmatic navigation
        default_idx = 0
        if "nav" in st.session_state:
            for i, p in enumerate(pages):
                if p == st.session_state["nav"]:
                    default_idx = i
                    break

        selection = st.radio(
            "NAVIGATION",
            pages,
            index=default_idx,
            key="sidebar_nav",
        )

        # Keep nav state in sync
        st.session_state["nav"] = selection

        # Sidebar footer
        st.markdown(
            """
            <div style="position:fixed; bottom:24px; padding:0 16px;">
                <hr style="border-color:rgba(255,255,255,0.06); margin-bottom:12px;">
                <div style="color:var(--text-muted); font-size:0.72rem; text-align:center; line-height:1.5;">
                    Built with ❤️ using<br/>
                    FastAPI · Streamlit · HuggingFace
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Page Router ─────────────────────────────────────────────────────
    page_map = {
        "🏠 Home": page_home,
        "🎯 Smart Prompt Generator": page_generator,
        "🔍 Wikipedia Fact Checker": page_fact_checker,
        "📜 Conversation History": page_history,
        "📊 Analytics Dashboard": page_analytics,
        "⭐ Feedback": page_feedback,
        "⚙️ Settings & About": page_settings,
    }

    page_fn = page_map.get(selection, page_home)
    page_fn()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
