import streamlit as st
import json
import os
import asyncio
import edge_tts
import random

# --- 1. إعدادات الصفحة والجمالية ---
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide", initial_sidebar_state="collapsed")

# كود CSS المطور لتحسين المظهر والخطوط
st.markdown("""
    <style>
    /* إخفاء زوائد المنصة */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    
    /* التصميم العام */
    .stApp {
        background-color: #f8f9fa;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='%23d1ecf1' fill-opacity='0.4'%3E%3Cpath d='M14 16h2v2h-2zM28 32h2v2h-2zM10 60h2v2h-2zM66 12h2v2h-2zM70 46h2v2h-2z'/%3E%3C/g%3E%3C/svg%3E");
    }
    
    /* نصوص لوحة الإدارة */
    label, .stMarkdown p, .stHeader h1 { color: #1a1a1a !important; font-weight: bold !important; }
    
    /* تصميم بطاقات الجمل */
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        border-right: 10px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .en-text { font-size: 30px; font-weight: 800; color: #004085; margin-bottom: 10px; }
    .ar-text { font-size: 24px; color: #28a745; direction: rtl; font-weight: 600; margin-bottom: 10px; }
    
    /* تعديل السطر الثالث (لفظ الكلمة بالعربي) كما طلبت */
    .pron-text { 
        font-size: 28px !important; 
        color: #dc3545 !important; 
        background-color: #fff3f3;
        padding: 5px 15px;
        border-radius: 10px;
        display: inline-block;
        font-weight: 900 !important;
        border: 1px dashed #dc3545;
    }
    
    /* تنسيق أيقونة الإعدادات المنبثقة */
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        background: #007bff !important;
        color: white !important;
        border: none !important;
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والصوت ---
DB_FILE = "data.json"
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

VOICES = {
    "🎙 رجل أمريكي (Guy)": "en-US-GuyNeural",
    "🎙 امرأة أمريكية (Ava)": "en-US-AvaNeural",
    "🎙 صوت بريطاني (Sonia)": "en-GB-SoniaNeural"
}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"categories": {}, "favorites": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

async def generate_voice(text, filename, voice_key, rate):
    # تم تعديل الـ rate ليكون أبطأ افتراضياً لضمان الوضوح وعدم بلع الحروف
    speed = f"{rate:+d}%"
    communicate = edge_tts.Communicate(text, VOICES[voice_key], rate=speed)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 3. أيقونة الإعدادات الذكية (تظهر وتختفي) ---
with st.sidebar:
    st.title("⚙️ خيارات العرض")
    app_mode = st.radio("النمط الحالي:", ["📚 مكتبة الجمل", "🧠 اختبار الذاكرة"])
    search_q = st.text_input("🔍 ابحث عن جملة...")

# أيقونة عائمة للإعدادات الصوتية (تظهر للطالب وتختفي عند الضغط خارجها)
with st.container():
    with st.popover("⚙️"):
        st.markdown("### 🎧 إعدادات الصوت")
        user_voice = st.selectbox("اختر المعلم:", list(VOICES.keys()), index=1)
        # جعلنا السرعة الافتراضية -10 لجعل النطق واضحاً جداً
        user_speed = st.slider("سرعة النطق (أقل يعني أوضح):", -50, 20, -10, step=5)
        st.info("هذه الإعدادات تطبق فوراً على جميع الجمل")
