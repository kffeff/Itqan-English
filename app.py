import streamlit as st
import json
import os
import asyncio
import edge_tts
import random

# --- 1. إعدادات الصفحة والجمالية الحيوية ---
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide", initial_sidebar_state="expanded")

# كود CSS المطور لتحسين الخطوط وظهور الصوت في كل الأجهزة
st.markdown("""
    <style>
    /* إخفاء زوائد المنصة لجعلها كالتطبيق */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    
    /* الخلفية الحيوية */
    .stApp {
        background-color: #e0f7fa;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='%23b2ebf2' fill-opacity='0.4'%3E%3Cpath d='M14 16h2v2h-2zM28 32h2v2h-2zM10 60h2v2h-2zM66 12h2v2h-2zM70 46h2v2h-2z'/%3E%3C/g%3E%3C/svg%3E");
    }
    
    /* نصوص الإدارة باللون الأسود */
    label, .stMarkdown p, .stSelectbox label, button[data-baseweb="tab"] p { 
        color: black !important; 
        font-weight: bold !important; 
    }
    
    /* تصميم بطاقات الجمل */
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        border-right: 10px solid #00acc1;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    .en-text { font-size: 32px; font-weight: 800; color: #006064; margin-bottom: 10px; }
    .ar-text { font-size: 26px; color: #00acc1; direction: rtl; font-weight: 600; margin-bottom: 10px; }
    
    /* --- تعديل السطر الثالث (النطق): تكبير وتوضيح --- */
    .pron-text { 
        font-size: 24px; /* تكبير الخط */
        color: #d81b60; /* لون مميز وواضح */
        font-weight: bold;
        background-color: #fce4ec;
        padding: 5px 15px;
        border-radius: 10px;
        display: inline-block;
        margin-top: 10px;
    }
    
    /* تجميل أزرار الأجهزة */
    .stButton>button {
        border-radius: 15px;
        background: linear-gradient(45deg, #00acc1, #0277bd);
        color: white;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات والصوت ---
DB_FILE = "data.json"
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

VOICES = {
    "🎙️ رجل أمريكي (بطيء وواضح)": "en-US-GuyNeural",
    "🎙️ امرأة أمريكية (صافي)": "en-US-AvaNeural",
    "🎙️ صوت بريطاني (مميز)": "en-GB-SoniaNeural"
}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"categories": {}, "favorites": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

async def generate_voice(text, filename, voice_key, rate="-15%"): # ضبط السرعة الافتراضية لتكون أبطأ وأوضح
    communicate = edge_tts.Communicate(text, VOICES[voice_key], rate=rate)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

# --- 3. المنطق البرمجي الأساسي ---
data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 4. القائمة الجانبية (الأيقونة التلقائية للطالب) ---
# تظهر وتختفي تلقائياً عند الضغط على السهم في الجانب
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:black;'>🎨 تخصيص الصوت</h2>", unsafe_allow_html=True)
    st.info("من هنا يمكنك تغيير نبرة الصوت وسرعته في أي وقت.")
    
    user_voice = st.selectbox("اختر الشخصية الصوتية:", list(VOICES.keys()))
    # جعل السرعة الافتراضية -15% لضمان وضوح مخارج الحروف
    user_speed = st.slider("سرعة النطق (كلما قل الرقم كان أوضح):", -50, 10, -15, step=5)
    
    st.divider()
    app_mode = st.radio("الوضع الحالي:", ["📚 مكتبة الجمل", "🧠 وضع الاختبار"])
    search_q = st.text_input("🔍 بحث عن كلمة...")

# --- 5. لوحة الإدارة (Admin) ---
if is_admin:
    st.markdown("<h1 style='text-align:center; color:black;'>🛠 إدارة المنصة</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["إضافة محتوى", "تعديل وحذف", "إدارة الأقسام"])
    
    with t1:
        new_c = st.text_input("اسم قسم جديد:")
        if st.button("حفظ القسم"):
            if new_c and new_c not in data["categories"]:
                data["categories"][new_c] = []
                save_data(data); st.rerun()
        
        if categories:
            target = st.selectbox("إضافة إلى:", categories)
            raw = st.text_area("تنسيق: (جملة | ترجمة | نطق العربي)")
            if st.button("🚀 حفظ الجمل"):
                lines = raw.strip().split('\n')
                for line in lines:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3:
                        data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
                save_data(data); st.success("تم الحفظ بنجاح!"); st.rerun()

    with t3:
        if categories:
            cat_del = st.selectbox("حذف قسم بالكامل", categories)
            st.warning(f"هل أنت متأكد من حذف '{cat_del}'؟")
            if st.button("🔥 حذف نهائي"):
                del data["categories"][cat_del]; save_data(data); st.rerun()

# --- 6. واجهة الطلاب (المظهر المطور) ---
else:
    st.markdown("<h1 style='text-align: center; color: #007ea7;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    if categories:
        choice = st.selectbox("اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        
        if search_q:
            items = [i for i in items if search_q.lower() in i['en'].lower()]

        if app_mode == "📚 مكتبة الجمل":
            for idx, item in enumerate(items):
                st.markdown(f"""
                <div class="card">
                    <div class="en-text">{item['en']}</div>
                    <div class="ar-text">{item['ar']}</div>
                    <div class="pron-text">{item['pron']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # معالجة الصوت ليعمل على الآيفون وكل الأجهزة
                v_id = VOICES[user_voice].split('-')[2]
                # اسم الملف يتغير بتغير السرعة لضمان التحديث
                f_name = f"{item['en'][:10].replace(' ','_').lower()}_{v_id}_{user_speed}.mp3"
                f_path = os.path.join(AUDIO_DIR, f_name)
                
                if not os.path.exists(f_path):
                    speed_str = f"{user_speed}%"
                    asyncio.run(generate_voice(item['en'], f_name, user_voice, speed_str))
                
                # استخدام قارئ الملفات لضمان التوافق مع Safari (آيفون)
                with open(f_path, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                
                st.divider()

        else: # وضع الاختبار
            st.subheader("🧠 اختبر أذنك وحفظك")
            if items:
                if 'q_item' not in st.session_state: st.session_state.q_item = random.choice(items)
                q = st.session_state.q_item
                
                v_id = VOICES[user_voice].split('-')[2]
                f_name = f"test_{v_id}_{user_speed}.mp3"
                asyncio.run(generate_voice(q['en'], f_name, user_voice, f"{user_speed}%"))
                
                with open(os.path.join(AUDIO_DIR, f_name), "rb") as f:
                    st.audio(f.read())
                
                if st.button("كشف الإجابة"):
                    st.success(f"الترجمة: {q['ar']}")
                    st.info(f"النطق: {q['pron']}")
                    if st.button("جملة أخرى"):
                        del st.session_state.q_item; st.rerun()
    else:
        st.info("الموقع جاهز! أضف ?admin=true للرابط لتبدأ الإدارة.")
