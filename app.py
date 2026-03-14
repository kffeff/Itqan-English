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

# --- 4. لوحة الإدارة ---
if is_admin:
    st.markdown("<h1 style='text-align:center;'>🛠 لوحة التحكم بالإدارة</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["➕ إضافة محتوى", "🗑 إدارة الأقسام"])
    
    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("حفظ القسم"):
            if new_c and new_c not in data["categories"]:
                data["categories"][new_c] = []
                save_data(data); st.rerun()
        st.divider()
        if categories:
            target = st.selectbox("إضافة جمل إلى:", categories)
            raw = st.text_area("أدخل الجمل (الإنجليزية | العربية | النطق بالعربي):")
            if st.button("🚀 حفظ الجمل"):
                lines = raw.strip().split('\n')
                for line in lines:
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) == 3:
                            data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
                save_data(data); st.success("تم التحديث!"); st.rerun()

    with tab2:
        if categories:
            cat_del = st.selectbox("اختر قسماً لحذفه:", categories)
            if st.button("🔥 حذف القسم نهائياً"):
                del data["categories"][cat_del]
                save_data(data); st.rerun()

# --- 5. واجهة الطلاب (المحسنة للآيفون) ---
else:
    st.markdown("<h1 style='text-align: center; color: #007bff;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    if categories:
        choice = st.selectbox("اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        if search_q: items = [i for i in items if search_q.lower() in i['en'].lower()]

        if app_mode == "📚 مكتبة الجمل":
            for idx, item in enumerate(items):
                st.markdown(f"""
                <div class="card">
                    <div class="en-text">{item['en']}</div>
                    <div class="ar-text">{item['ar']}</div>
                    <div class="pron-text">{item['pron']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # توليد الصوت ومعالجة سرعته
                v_id = VOICES[user_voice].split('-')[2]
                f_name = f"v2_{item['en'][:10].replace(' ','_').lower()}_{v_id}_{user_speed}.mp3"
                f_path = os.path.join(AUDIO_DIR, f_name)
                
                if not os.path.exists(f_path):
                    asyncio.run(generate_voice(item['en'], f_name, user_voice, user_speed))
                
                # عرض مشغل الصوت بطريقة متوافقة مع الآيفون
                with open(f_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
                
                st.divider()
        
        else: # نمط الاختبار
            st.subheader("🧠 استمع وحاول التذكر")
            if items:
                if 'q_idx' not in st.session_state: st.session_state.q_idx = random.randint(0, len(items)-1)
                q = items[st.session_state.q_idx]
                
                f_name = f"quiz_{st.session_state.q_idx}_{user_speed}.mp3"
                if not os.path.exists(os.path.join(AUDIO_DIR, f_name)):
                    asyncio.run(generate_voice(q['en'], f_name, user_voice, user_speed))
                
                st.audio(os.path.join(AUDIO_DIR, f_name))
                if st.button("👁️ كشف الإجابة"):
                    st.info(f"الترجمة: {q['ar']}")
                    st.success(f"النطق: {q['pron']}")
                    if st.button("🔄 جملة تالية"):
                        del st.session_state.q_idx
                        st.rerun()
    else:
        st.warning("يرجى إضافة محتوى من لوحة الإدارة أولاً.")
