import streamlit as st
import json
import os
import asyncio
import edge_tts
import base64

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide")

# كود CSS المطور لتحسين مظهر "أيقونة الإعدادات" وسطر النطق
st.markdown("""
    <style>
    /* إخفاء القوائم غير الضرورية */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    
    .stApp { background-color: #fcfdfe; }

    /* تصميم البطاقة التعليمية */
    .card {
        background: white;
        padding: 30px;
        border-radius: 25px;
        border-right: 15px solid #007bff;
        margin-bottom: 25px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.06);
        text-align: center;
        width: 100%;
    }

    .en-text { 
        font-size: 38px; 
        font-weight: 900; 
        color: #1e293b; 
        margin-bottom: 5px;
    }

    .ar-text { 
        font-size: 26px; 
        color: #10b981; 
        font-weight: 700; 
    }

    /* سطر النطق: تكبير الخط وتوضيحه بشكل فائق */
    .pron-box {
        background-color: #fff1f2;
        padding: 20px;
        border-radius: 18px;
        border: 3px dashed #f43f5e;
        color: #e11d48;
        font-size: 42px; /* خط ضخم وواضح جداً */
        font-weight: 900;
        margin-top: 20px;
        display: block;
        width: 100%;
        line-height: 1.2;
    }

    /* تنسيق زر الإعدادات (البوب أوفر) ليظهر كأيقونة احترافية */
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,123,255,0.4) !important;
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
    }

    audio {
        width: 100%;
        height: 50px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. وظائف الصوت والبيانات ---
DB_FILE = "data.json"
AUDIO_DIR = "audio_cache"
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

VOICES = {
    "🎙️ صوت رجالي واضح (Guy)": "en-US-GuyNeural",
    "🎙️ صوت نسائي هادئ (Ava)": "en-US-AvaNeural",
    "🎙️ صوت بريطاني فخم (Sonia)": "en-GB-SoniaNeural"
}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"categories": {}, "favorites": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

async def generate_voice(text, filename, voice_key, rate):
    # السرعة الآن مضبوطة لضمان الوضوح التام وعدم ضياع الحروف
    communicate = edge_tts.Communicate(text, VOICES[voice_key], rate=rate)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

def get_audio_html(file_path):
    """تشفير الصوت ليعمل فوراً على الآيفون والمتصفحات الأخرى"""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio controls preload="auto" style="border-radius:10px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 3. أيقونة الإعدادات العائمة (التي تظهر وتختفي) ---
# وضعت لك الإعدادات داخل Popover يظهر كأيقونة عائمة في أسفل الشاشة
with st.popover("⚙️"):
    st.markdown("### 🛠 إعدادات النطق")
    u_voice = st.selectbox("اختر المعلم:", list(VOICES.keys()))
    # ضبط السرعة لتبدأ من -30% لضمان نطق "رزين" وبطيء
    u_speed = st.slider("سرعة الصوت:", -50, 0, -30, step=5)
    st.divider()
    search_q = st.text_input("🔍 بحث سريع:")

# --- 4. واجهة المنصة ---
st.markdown("<h1 style='text-align: center; color: #007bff; font-family: Cairo; margin-bottom:40px;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)

if is_admin:
    st.title("🛠 لوحة الإدارة")
    new_c = st.text_input("اسم القسم:")
    if st.button("إضافة القسم"):
        data["categories"][new_c] = []; save_data(data); st.rerun()
    
    if categories:
        target = st.selectbox("إضافة إلى:", categories)
        raw = st.text_area("جملة | ترجمة | نطق (سطر جديد لكل جملة)")
        if st.button("حفظ"):
            for line in raw.strip().split('\n'):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
            save_data(data); st.success("تم الحفظ!"); st.rerun()
else:
    if categories:
        choice = st.selectbox("📖 اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        
        if 'search_q' in locals() and search_q:
            items = [i for i in items if search_q.lower() in i['en'].lower()]

        for idx, item in enumerate(items):
            # البطاقة مع سطر النطق الضخم
            st.markdown(f"""
            <div class="card">
                <div class="en-text">{item['en']}</div>
                <div class="ar-text">{item['ar']}</div>
                <div class="pron-box">{item['pron']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # معالجة الصوت للأيفون
            v_code = VOICES[u_voice].split('-')[2]
            # اسم ملف فريد يعتمد على المحتوى والسرعة والصوت
            safe_text = "".join(x for x in item['en'][:15] if x.isalnum())
            f_name = f"{safe_text}_{v_code}_{u_speed}.mp3"
            f_path = os.path.join(AUDIO_DIR, f_name)
            
            if not os.path.exists(f_path):
                with st.spinner("جاري معالجة الصوت..."):
                    asyncio.run(generate_voice(item['en'], f_name, u_voice, f"{u_speed}%"))
            
            st.markdown(get_audio_html(f_path), unsafe_allow_html=True)
            st.divider()
    else:
        st.info("المنصة جاهزة، بانتظار إضافة المحتوى من لوحة الإدارة.")
