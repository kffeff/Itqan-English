import streamlit as st
import streamlit.components.v1 as components
import os, asyncio, edge_tts, base64, hashlib, random, time
from supabase import create_client, Client

# ══════════════════════════════════════════════════════
# 1. Page config + Theme
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide", page_icon="🎓")

if "dark_mode" not in st.session_state: st.session_state.dark_mode = False
DK      = st.session_state.dark_mode
BG      = "#0f172a" if DK else "#f0f4ff"
CARD_BG = "#1e293b" if DK else "#ffffff"
TEXT    = "#f1f5f9" if DK else "#1e293b"
SUB     = "#94a3b8" if DK else "#64748b"
BORDER  = "#334155" if DK else "#e2e8f0"
INPUT_BG= "#334155" if DK else "#1e293b"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
#MainMenu,footer,header,.stDeployButton,[data-testid='stSidebar'],[data-testid='stSidebarCollapseButton']{{display:none!important;visibility:hidden!important;}}
.stApp{{background-color:{BG};font-family:'Cairo',sans-serif;}}
.card{{background:{CARD_BG};padding:32px 28px 24px;border-radius:22px;border-right:10px solid #2563eb;
    margin-bottom:10px;box-shadow:0 8px 32px rgba(37,99,235,0.12);text-align:center;width:100%;
    transition:transform 0.18s ease,box-shadow 0.18s ease;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 18px 48px rgba(37,99,235,0.2);}}
.en-text{{font-size:40px;font-weight:900;color:{TEXT};margin-bottom:6px;}}
.ar-text{{font-size:26px;color:#059669;font-weight:700;margin-bottom:4px;font-family:'Cairo',sans-serif;}}
.pron-box{{background:linear-gradient(135deg,#fff1f2 0%,#ffe4e6 100%);padding:14px 18px;
    border-radius:16px;border:3px dashed #f43f5e;color:#e11d48;font-size:clamp(22px,5vw,46px);
    font-weight:900;margin-top:14px;display:block;width:100%;line-height:1.4;
    font-family:'Cairo',sans-serif;word-break:break-word;overflow-wrap:break-word;}}
@media(max-width:600px){{
    .pron-box{{font-size:clamp(18px,4.5vw,28px)!important;padding:10px 12px;}}
    .en-text{{font-size:clamp(22px,6vw,32px)!important;}}
    .ar-text{{font-size:clamp(16px,4vw,22px)!important;}}
    .card{{padding:20px 16px 16px!important;}}
    .quiz-en{{font-size:clamp(22px,6vw,36px)!important;}}
}}
.quiz-card{{background:{CARD_BG};padding:40px 32px;border-radius:24px;border-top:8px solid #7c3aed;
    margin-bottom:16px;box-shadow:0 10px 40px rgba(124,58,237,0.15);text-align:center;width:100%;}}
.quiz-en{{font-size:44px;font-weight:900;color:{TEXT};margin-bottom:8px;}}
.quiz-ar{{font-size:38px;font-weight:900;color:#059669;margin-bottom:8px;font-family:'Cairo',sans-serif;}}
.quiz-hint{{font-size:18px;color:{SUB};font-family:'Cairo',sans-serif;margin-bottom:20px;}}
.quiz-correct{{background:linear-gradient(135deg,#d1fae5,#a7f3d0);border:3px solid #059669;
    border-radius:16px;padding:20px;margin-top:16px;font-size:28px;font-weight:900;
    color:#065f46;font-family:'Cairo',sans-serif;}}
.quiz-wrong{{background:linear-gradient(135deg,#fee2e2,#fecaca);border:3px solid #dc2626;
    border-radius:16px;padding:20px;margin-top:16px;font-size:22px;font-weight:700;
    color:#7f1d1d;font-family:'Cairo',sans-serif;}}
.quiz-reveal{{background:linear-gradient(135deg,#ede9fe,#ddd6fe);border:3px solid #7c3aed;
    border-radius:16px;padding:20px;margin-top:16px;font-family:'Cairo',sans-serif;}}
.quiz-score{{background:linear-gradient(135deg,#1e293b,#0f172a);border-radius:24px;padding:40px;
    text-align:center;color:white;font-family:'Cairo',sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.35);}}
.score-number{{font-size:80px;font-weight:900;color:#fbbf24;line-height:1;}}
.score-label{{font-size:24px;color:#94a3b8;margin-top:8px;}}
.score-msg{{font-size:30px;font-weight:900;margin-top:20px;}}
.q-counter{{font-size:16px;color:{SUB};font-family:'Cairo',sans-serif;text-align:left;margin-bottom:4px;}}
.progress-bar-wrap{{background:{BORDER};border-radius:99px;height:12px;width:100%;margin:12px 0;}}
.progress-bar-fill{{background:linear-gradient(90deg,#7c3aed,#2563eb);height:12px;border-radius:99px;transition:width 0.4s ease;}}
.timer-box{{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:white;border-radius:16px;
    padding:12px 24px;font-size:28px;font-weight:900;text-align:center;margin-bottom:16px;
    font-family:'Cairo',sans-serif;box-shadow:0 4px 20px rgba(124,58,237,0.4);}}
.timer-warn{{background:linear-gradient(135deg,#ef4444,#dc2626)!important;}}
.mcq-opt{{width:100%;padding:16px 20px;border-radius:14px;border:2px solid {BORDER};
    background:{CARD_BG};font-size:22px;font-weight:700;font-family:'Cairo',sans-serif;
    margin:6px 0;text-align:center;display:block;}}
.mcq-opt-correct{{background:linear-gradient(135deg,#d1fae5,#a7f3d0)!important;border-color:#059669!important;color:#065f46!important;}}
.mcq-opt-wrong{{background:linear-gradient(135deg,#fee2e2,#fecaca)!important;border-color:#dc2626!important;color:#7f1d1d!important;}}
.mcq-opt-neutral{{opacity:0.45;}}
.repeat-badge{{background:linear-gradient(135deg,#f59e0b,#d97706);color:white;
    border-radius:99px;padding:4px 14px;font-size:14px;font-weight:700;
    font-family:'Cairo',sans-serif;display:inline-block;margin-bottom:8px;}}

/* ══════ زر الإعدادات ══════ */
div[data-testid="stPopover"]{{
    position:fixed!important;
    bottom:30px!important;
    right:30px!important;
    z-index:9999!important;
    width:56px!important;
    height:56px!important;
}}
div[data-testid="stPopover"]>button{{
    border-radius:50%!important;
    width:56px!important;
    height:56px!important;
    min-height:56px!important;
    background:linear-gradient(135deg,#2563eb,#1d4ed8)!important;
    border:none!important;
    box-shadow:0 6px 24px rgba(37,99,255,0.45)!important;
    overflow:visible!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    cursor:pointer!important;
    padding:0!important;
    position:relative!important;
}}
div[data-testid="stPopover"]>button::after{{
    content:'⚙'!important;
    font-size:26px!important;
    color:white!important;
    position:absolute!important;
    top:50%!important;
    left:50%!important;
    transform:translate(-50%,-50%)!important;
    line-height:1!important;
    pointer-events:none!important;
}}
div[data-testid="stPopover"]>button *{{
    opacity:0!important;
    font-size:0!important;
    color:transparent!important;
    position:absolute!important;
    width:0!important;
    height:0!important;
    overflow:hidden!important;
    pointer-events:none!important;
    margin:0!important;
    padding:0!important;
}}
/* ══════════════════════════════════════════════════════ */

div[data-testid="stPopoverBody"] label,div[data-testid="stPopoverBody"] p,
div[data-testid="stPopoverBody"] h3,div[data-testid="stPopoverBody"] .stMarkdown p,
div[data-testid="stPopoverBody"] .stSlider label,
div[data-testid="stPopoverBody"] .stSlider span{{color:#ffffff!important;}}
div[data-testid="stPopoverBody"] input{{background-color:#334155!important;color:#ffffff!important;
    border:2px solid #2563eb!important;border-radius:10px!important;}}
div[data-testid="stPopoverBody"] div[data-baseweb="select"]>div{{background-color:#334155!important;
    border:2px solid #2563eb!important;border-radius:10px!important;}}
div[data-testid="stPopoverBody"] div[data-baseweb="select"] span,
div[data-testid="stPopoverBody"] div[data-baseweb="select"] div{{color:#ffffff!important;}}
.platform-title{{text-align:center;color:#2563eb;font-family:'Cairo',sans-serif;font-size:42px;font-weight:900;margin-bottom:8px;}}
.platform-subtitle{{text-align:center;color:{SUB};font-family:'Cairo',sans-serif;font-size:18px;margin-bottom:30px;}}
hr{{border:none;border-top:2px solid {BORDER};margin:4px 0 20px;}}
label,.stTextInput label,.stTextArea label,.stSelectbox label,.stSlider label,
.stTabs [data-baseweb="tab"],h1,h2,h3,h4,p,div[data-testid="stText"],.stMarkdown p,
.stAlert p,.stInfo p{{color:{TEXT}!important;font-weight:600;}}
.stTabs [data-baseweb="tab"][aria-selected="true"]{{color:#2563eb!important;}}
button, button *, button p, button span, button div,
.stButton button, .stButton button * {{color:#ffffff!important;font-family:'Cairo',sans-serif!important;font-weight:700!important;}}
.stButton>button{{background:#1e293b!important;border:2px solid #334155!important;border-radius:10px!important;}}
.stButton>button:hover{{background:#2d3f55!important;border
