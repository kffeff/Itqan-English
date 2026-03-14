import streamlit as st
import json
import os
import asyncio
import edge_tts
import base64
import hashlib

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide")

st.markdown("""
    <style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    .stApp { background-color: #fcfdfe; }

    /* تصميم البطاقة */
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

    .en-text { font-size: 38px; font-weight: 900; color: #1e293b; margin-bottom: 5px; }
    .ar-text { font-size: 26px; color: #10b981; font-weight: 700; }

    /* سطر النطق: كبير جداً وواضح (تعديل السطر الثالث) */
    .pron-box {
        background-color: #fff1f2;
        padding: 20px;
        border-radius: 18px;
        border: 3px dashed #f43f5e;
        color: #e11d48;
        font-size: 45px; /* تكبير إضافي بناءً على طلبك */
        font-weight: 900;
        margin-top: 20px;
        display: block;
        width: 100%;
        line-height: 1.2;
    }

    /* أيقونة الإعدادات العائمة الاحترافية */
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 65px !important;
        height: 65px !important;
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(0,123,255,0.5) !important;
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
        font-size: 24px !important;
    }

    audio { width: 100%; height: 50px; margin-top: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والصوت ---
DB_FILE = "data.json"
AUDIO_DIR = "audio_cache"
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

VOICES = {
    "🎙️ صوت رجالي واضح (Guy)": "en-US-GuyNeural",
    "🎙️ صوت نسائي رقيق (Ava)": "en-US-AvaNeural",
    "🎙️ صوت بريطاني فخم (Sonia)": "en-GB-SoniaNeural"
}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"categories": {}, "favorites": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

async def generate_voice(text, filename, voice_id, rate):
    # تم تثبيت السرعة لتكون بطيئة وواضحة جداً لعدم بلع الحروف
    communicate = edge_tts.Communicate(text, voice_id, rate=rate)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

def get_audio_html(file_path):
    """حل مشكلة الآيفون عبر Base64 مع إضافة ID فريد لإجبار المتصفح على التحديث"""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        unique_id = hashlib.md5(data).hexdigest() # معرّف فريد للصوت
        return f'<audio id="{unique_id}" controls preload="auto"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 3. أيقونة الإعدادات العائمة (تظهر وتختفي) ---
# تم وضعها في popover كما طلبت لتكون احترافية وتلقائية
with st.popover("⚙️"):
    st.markdown("### 🛠 إعدادات الصوت")
    selected_voice_key = st.selectbox("اختر المعلم:", list(VOICES.keys()), key="voice_choice")
    # السرعة الافتراضية -30% لضمان وضوح مخارج الحروف
    selected_speed = st.slider("سرعة النطق:", -50, 0, -30, step=5, key="speed_choice")
    st.divider()
    search_query = st.text_input("🔍 بحث عن جملة:", key="search_input")

# --- 4. واجهة المنصة ---
st.markdown("<h1 style='text-align: center; color: #007bff; font-family: Cairo; margin-bottom:30px;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)

if is_admin:
    st.title("🛠 لوحة الإدارة")
    new_cat = st.text_input("أضف قسماً جديداً:")
    if st.button("حفظ القسم"):
        data["categories"][new_cat] = []; save_data(data); st.rerun()
    
    if categories:
        target_cat = st.selectbox("إضافة جمل إلى:", categories)
        input_data = st.text_area("أدخل (جملة | ترجمة | نطق)")
        if st.button("🚀 حفظ الجمل"):
            for line in input_data.strip().split('\n'):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    data["categories"][target_cat].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
            save_data(data); st.success("تم الحفظ بنجاح!"); st.rerun()

else:
    if categories:
        unit_choice = st.selectbox("📂 اختر الوحدة الدراسية:", categories)
        items_to_show = data["categories"][unit_choice]
        
        if search_query:
            items_to_show = [i for i in items_to_show if search_query.lower() in i['en'].lower()]

        for item in items_to_show:
            # عرض بطاقة الكلمة
            st.markdown(f"""
            <div class="card">
                <div class="en-text">{item['en']}</div>
                <div class="ar-text">{item['ar']}</div>
                <div class="pron-box">{item['pron']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- منطق تغيير الصوت (الإصلاح الجذري) ---
            voice_id = VOICES[selected_voice_key]
            v_short_name = voice_id.split('-')[2]
            
            # إنشاء اسم ملف فريد يجمع بين (النص + نوع الصوت + السرعة)
            # هذا يضمن أنه عند تغيير أي إعداد، يتغير اسم الملف فوراً
            text_hash = hashlib.md5(f"{item['en']}_{v_short_name}_{selected_speed}".encode()).hexdigest()
            filename = f"audio_{text_hash}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)
            
            if not os.path.exists(filepath):
                with st.spinner("جاري تبديل صوت المعلم..."):
                    asyncio.run(generate_voice(item['en'], filename, voice_id, f"{selected_speed}%"))
            
            # عرض الصوت (سيعمل على الأيفون ويحدث فوراً عند تغيير الصوت)
            st.markdown(get_audio_html(filepath), unsafe_allow_html=True)
            st.divider()
    else:
        st.info("مرحباً بك! بانتظار رفع الدروس من قبل الإدارة.")
