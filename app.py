import streamlit as st
import json
import os
import asyncio
import edge_tts
import random
import base64

# --- 1. إعدادات الصفحة والجمالية (تعديل العرض) ---
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide", initial_sidebar_state="expanded")

# كود CSS المطور للجعل الكلمات في سطر واحد وإصلاح العرض
st.markdown("""
    <style>
    /* إخفاء الزوائد */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    
    /* الخلفية الحيوية */
    .stApp {
        background-color: #f0faff;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cg fill='%23d0efff' fill-opacity='0.5'%3E%3Cpath d='M30 30h2v2h-2z'/%3E%3C/g%3E%3C/svg%3E");
    }

    /* تصميم البطاقة العرضية (Horizontal Card) */
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 20px;
        border-left: 10px solid #007bff;
        margin-bottom: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column; /* ترتيب العناصر تحت بعض لكن بعرض كامل السطر */
        width: 100%;
    }

    /* جعل الكلمات الإنجليزية والعربية في سطر واحد قدر الإمكان */
    .text-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap; /* للسماح بالنزول في حال كانت الجملة طويلة جداً */
        gap: 15px;
    }

    .en-text { font-size: 28px; font-weight: 800; color: #1a1a1a; flex: 1; min-width: 250px; }
    .ar-text { font-size: 22px; color: #007bff; direction: rtl; font-weight: 600; flex: 1; text-align: right; }
    
    /* سطر النطق (كبير وواضح) */
    .pron-box {
        margin-top: 15px;
        background-color: #fff0f3;
        padding: 10px 20px;
        border-radius: 12px;
        border: 1px dashed #ff4d6d;
        color: #ff4d6d;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
    }

    /* نصوص الإدارة سوداء */
    label, p, span, .stSelectbox label { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. وظائف الصوت المتقدمة (حل مشكلة الآيفون) ---
DB_FILE = "data.json"
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

VOICES = {
    "🎙️ رجل أمريكي (Guy)": "en-US-GuyNeural",
    "🎙️ امرأة أمريكية (Ava)": "en-US-AvaNeural",
    "🎙️ صوت بريطاني (Sonia)": "en-GB-SoniaNeural"
}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"categories": {}, "favorites": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

async def generate_voice(text, filename, voice_key, rate):
    communicate = edge_tts.Communicate(text, VOICES[voice_key], rate=rate)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

# وظيفة تشفير الصوت ليعمل على الآيفون
def get_audio_html(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio controls style="width: 100%; height: 40px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚙️ الإعدادات</h2>", unsafe_allow_html=True)
    u_voice = st.selectbox("اختر الصوت:", list(VOICES.keys()))
    u_speed = st.slider("سرعة النطق (يفضل -15%):", -50, 10, -15, step=5)
    st.divider()
    app_mode = st.radio("النمط:", ["📚 تعلم", "🧠 اختبار"])
    search_q = st.text_input("🔍 بحث:")

# --- 4. لوحة الإدارة ---
if is_admin:
    st.title("🛠 لوحة الإدارة")
    t1, t2 = st.tabs(["إضافة", "إدارة"])
    with t1:
        new_c = st.text_input("قسم جديد:")
        if st.button("حفظ القسم"):
            data["categories"][new_c] = []; save_data(data); st.rerun()
        if categories:
            target = st.selectbox("إضافة إلى:", categories)
            raw = st.text_area("جملة | ترجمة | نطق")
            if st.button("🚀 حفظ"):
                for line in raw.strip().split('\n'):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3:
                        data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
                save_data(data); st.success("تم الحفظ!"); st.rerun()
    with t2:
        if categories:
            cat_del = st.selectbox("حذف قسم:", categories)
            if st.button("🔥 حذف القسم نهائياً"):
                del data["categories"][cat_del]; save_data(data); st.rerun()

# --- 5. واجهة الطالب (العرض العرضي) ---
else:
    st.markdown("<h1 style='text-align: center; color: #007bff;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    if categories:
        choice = st.selectbox("اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        
        if search_q:
            items = [i for i in items if search_q.lower() in i['en'].lower()]

        for idx, item in enumerate(items):
            # البطاقة العرضية
            st.markdown(f"""
            <div class="card">
                <div class="text-row">
                    <div class="en-text">{item['en']}</div>
                    <div class="ar-text">{item['ar']}</div>
                </div>
                <div class="pron-box">{item['pron']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # منطق الصوت المطور للآيفون
            v_tag = VOICES[u_voice].split('-')[2]
            f_name = f"{item['en'][:10].replace(' ','_').lower()}_{v_tag}_{u_speed}.mp3"
            f_path = os.path.join(AUDIO_DIR, f_name)
            
            if not os.path.exists(f_path):
                asyncio.run(generate_voice(item['en'], f_name, u_voice, f"{u_speed}%"))
            
            # عرض مشغل الصوت بطريقة HTML (الحل السحري للآيفون)
            st.markdown(get_audio_html(f_path), unsafe_allow_html=True)
            st.divider()
    else:
        st.info("أهلاً بك! استخدم ?admin=true للإدارة.")
