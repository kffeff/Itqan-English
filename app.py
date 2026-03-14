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

    /* سطر النطق: كبير جداً وواضح كما طلبت */
    .pron-box {
        background-color: #fff1f2;
        padding: 20px;
        border-radius: 18px;
        border: 3px dashed #f43f5e;
        color: #e11d48;
        font-size: 45px; 
        font-weight: 900;
        margin-top: 20px;
        display: block;
        width: 100%;
        line-height: 1.2;
    }

    /* أيقونة الإعدادات العائمة الاحترافية (Popover) */
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
    communicate = edge_tts.Communicate(text, voice_id, rate=rate)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

def get_audio_html(file_path, audio_id):
    """تشفير الصوت ليعمل على الآيفون مع إجبار المتصفح على التحديث عند تغيير الصوت"""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # استخدام audio_id فريد يضمن تحديث الصوت فوراً عند الطالب
        return f'<audio id="{audio_id}" controls preload="auto"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 3. أيقونة الإعدادات العائمة (Popover) ---
with st.popover("⚙️"):
    st.markdown("### 🛠 إعدادات النطق")
    selected_voice_key = st.selectbox("اختر المعلم:", list(VOICES.keys()), key="v_sel")
    selected_speed = st.slider("سرعة النطق:", -50, 0, -25, step=5, key="s_sel")
    st.divider()
    search_q = st.text_input("🔍 بحث سريع:", key="search_q")

# --- 4. واجهة المنصة ---
st.markdown("<h1 style='text-align: center; color: #007bff; font-family: Cairo;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)

if is_admin:
    st.title("🛠 لوحة الإدارة الكاملة")
    tab1, tab2 = st.tabs(["➕ إضافة محتوى", "🗑 إدارة وحذف"])
    
    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("حفظ القسم الجديد"):
            data["categories"][new_c] = []; save_data(data); st.rerun()
        
        if categories:
            st.divider()
            target = st.selectbox("إضافة إلى قسم:", categories)
            raw = st.text_area("جملة | ترجمة | نطق (سطر جديد لكل جملة)")
            if st.button("🚀 حفظ الجمل"):
                for line in raw.strip().split('\n'):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3:
                        data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
                save_data(data); st.success("تم الحفظ!"); st.rerun()

    with tab2:
        if categories:
            cat_to_del = st.selectbox("اختر قسماً لحذفه:", categories)
            if st.button("🔥 حذف القسم المختار نهائياً"):
                del data["categories"][cat_to_del]; save_data(data); st.rerun()
            
            st.divider()
            st.warning("لحذف جملة معينة، اختر القسم أولاً:")
            cat_manage = st.selectbox("إدارة جمل القسم:", categories, key="manage_cat")
            for i, item in enumerate(data["categories"][cat_manage]):
                col1, col2 = st.columns([4, 1])
                col1.write(f"{item['en']} - {item['ar']}")
                if col2.button("حذف", key=f"del_{cat_manage}_{i}"):
                    data["categories"][cat_manage].pop(i)
                    save_data(data); st.rerun()

else:
    if categories:
        choice = st.selectbox("📂 اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        
        if search_q:
            items = [i for i in items if search_q.lower() in i['en'].lower()]

        for item in items:
            st.markdown(f"""
            <div class="card">
                <div class="en-text">{item['en']}</div>
                <div class="ar-text">{item['ar']}</div>
                <div class="pron-box">{item['pron']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- منطق الصوت المطور (يتغير فوراً) ---
            v_id = VOICES[selected_voice_key]
            # توليد Hash فريد يجمع (النص + الصوت + السرعة)
            unique_str = f"{item['en']}_{v_id}_{selected_speed}"
            file_hash = hashlib.md5(unique_str.encode()).hexdigest()
            f_name = f"audio_{file_hash}.mp3"
            f_path = os.path.join(AUDIO_DIR, f_name)
            
            if not os.path.exists(f_path):
                asyncio.run(generate_voice(item['en'], f_name, v_id, f"{selected_speed}%"))
            
            # تمرير الـ file_hash كمعرف للـ audio لضمان التحديث في الآيفون
            st.markdown(get_audio_html(f_path, file_hash), unsafe_allow_html=True)
            st.divider()
    else:
        st.info("مرحباً بك! يرجى إضافة أقسام من لوحة الإدارة أولاً.")
