import streamlit as st
import json
import os
import asyncio
import edge_tts
import random

# --- 1. إعدادات الصفحة والاسم الجديد ---
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide", initial_sidebar_state="expanded")

# كود CSS المطور (تكبير النطق + الألوان السوداء + التوافق مع الجوال)
st.markdown("""
    <style>
    /* إخفاء الزوائد */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}
    
    /* الخلفية الحيوية */
    .stApp {
        background-color: #e0f7fa;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='%23b2ebf2' fill-opacity='0.4'%3E%3Cpath d='M14 16h2v2h-2zM28 32h2v2h-2zM10 60h2v2h-2zM66 12h2v2h-2zM70 46h2v2h-2z'/%3E%3C/g%3E%3C/svg%3E");
    }
    
    /* نصوص الإدارة باللون الأسود */
    button[data-baseweb="tab"] p { color: black !important; font-weight: bold !important; font-size: 18px !important; }
    label, .stMarkdown p, .stSelectbox label, .stHeader h1 { color: black !important; font-weight: bold !important; }
    .stAlert p { color: black !important; font-weight: bold !important; }
    
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
    .ar-text { font-size: 24px; color: #00acc1; direction: rtl; font-weight: 600; }
    
    /* --- تعديل السطر الثالث (النطق): كبير وواضح جداً --- */
    .pron-text { 
        font-size: 26px; /* تكبير الخط */
        color: #d81b60; /* لون مميز وواضح */
        font-weight: 900; 
        background-color: #fce4ec;
        padding: 5px 15px;
        border-radius: 12px;
        display: inline-block;
        margin-top: 10px;
        border: 1px solid #f8bbd0;
    }
    
    /* أزرار حيوية */
    .stButton>button {
        border-radius: 15px;
        background: linear-gradient(45deg, #00acc1, #0277bd);
        color: white;
        font-weight: bold;
        border: none;
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
    speed = f"{rate:+d}%"
    communicate = edge_tts.Communicate(text, VOICES[voice_key], rate=speed)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 4. القائمة الجانبية (خيار الأصوات والتحكم للطالب) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:black;'>⚙️ إعدادات النطق</h2>", unsafe_allow_html=True)
    user_voice = st.selectbox("اختر نبرة الصوت المفضل:", list(VOICES.keys()))
    # جعل السرعة الافتراضية -15 لضمان الوضوح وعدم "بلع" الأحرف
    user_speed = st.slider("سرعة النطق (السالب أبطأ وأوضح):", -50, 10, -15, step=5)
    st.divider()
    app_mode = st.radio("النمط:", ["📚 مكتبة الجمل", "🧠 اختبار الذاكرة"])
    search_q = st.text_input("🔍 بحث عن جملة...")

# --- 5. لوحة الإدارة (Hidden Admin Panel) ---
if is_admin:
    st.markdown("<h1 style='text-align:center; color:black;'>🛠 إدارة المنصة</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["إضافة محتوى", "تعديل وحذف", "إدارة الأقسام"])
    
    with tab1:
        st.markdown("<p style='color:black;'>اسم القسم الجديد:</p>", unsafe_allow_html=True)
        new_c = st.text_input("", placeholder="مثلاً: الوحدة الأولى")
        if st.button("حفظ القسم"):
            if new_c and new_c not in data["categories"]:
                data["categories"][new_c] = []
                save_data(data); st.rerun()
        
        st.divider()
        if categories:
            st.markdown("<p style='color:black;'>أضف الجمل (جملة | ترجمة | نطق):</p>", unsafe_allow_html=True)
            target = st.selectbox("إلى:", categories)
            raw = st.text_area("النصوص:")
            if st.button("🚀 حفظ الجمل"):
                lines = raw.strip().split('\n')
                for line in lines:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3:
                        data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
                save_data(data); st.success("تم الحفظ بنجاح!"); st.rerun()

    with tab3:
        if categories:
            cat_del = st.selectbox("حذف قسم بالكامل", categories)
            st.warning(f"هل أنت متأكد من حذف قسم '{cat_del}' بالكامل؟")
            if st.button("🔥 تأكيد الحذف النهائي"):
                del data["categories"][cat_del]; save_data(data); st.rerun()

# --- 6. واجهة الطلاب (المظهر المطور) ---
else:
    st.markdown("<h1 style='text-align: center; color: #007ea7;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    if categories:
        choice = st.selectbox("اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        
        if search_q:
            items = [i for i in items if search_q.lower() in i['en'].lower() or search_q in i['ar']]

        if app_mode == "📚 مكتبة الجمل":
            for idx, item in enumerate(items):
                st.markdown(f"""
                <div class="card">
                    <div class="en-text">{item['en']}</div>
                    <div class="ar-text">{item['ar']}</div>
                    <div class="pron-text">{item['pron']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # توليد وتشغيل الصوت (نظام التوافق مع الآيفون)
                v_id = VOICES[user_voice].split('-')[2]
                f_name = f"{item['en'][:10].replace(' ','_').lower()}_{v_id}_{user_speed}.mp3"
                f_path = os.path.join(AUDIO_DIR, f_name)
                
                if not os.path.exists(f_path):
                    asyncio.run(generate_voice(item['en'], f_name, user_voice, user_speed))
                
                # قراءة الملف كـ Bytes لضمان ظهوره في Safari
                with open(f_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                
                # أزرار التفاعل
                c_f, c_n = st.columns([1, 1])
                is_f = item['en'] in data.get('favorites', [])
                if c_f.button("⭐" if is_f else "☆", key=f"fav_{idx}"):
                    if 'favorites' not in data: data['favorites'] = []
                    if is_f: data['favorites'].remove(item['en'])
                    else: data['favorites'].append(item['en'])
                    save_data(data); st.rerun()
                if c_n.button("📋 Notion", key=f"not_{idx}"):
                    st.code(f"**{item['en']}** | {item['ar']}")
                    st.toast("تم تحضير التنسيق!")
        
        else: # وضع الاختبار
            st.subheader("🧠 اختبر قدرتك السمعية")
            if items:
                if 'q_item' not in st.session_state: st.session_state.q_item = random.choice(items)
                q = st.session_state.q_item
                
                v_id = VOICES[user_voice].split('-')[2]
                f_name = f"test_{v_id}_{user_speed}.mp3"
                asyncio.run(generate_voice(q['en'], f_name, user_voice, user_speed))
                
                with open(os.path.join(AUDIO_DIR, f_name), "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                
                if st.button("👁️ كشف الإجابة"):
                    st.success(f"الإنجليزية: {q['en']}")
                    st.info(f"الترجمة: {q['ar']}")
                    st.warning(f"النطق: {q['pron']}")
                    if st.button("🔄 جملة أخرى"):
                        del st.session_state.q_item; st.rerun()
    else:
        st.info("أهلاً بك! ابدأ بإضافة المحتوى من لوحة التحكم (?admin=true).")
