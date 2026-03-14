import streamlit as st
import json
import os
import asyncio
import edge_tts
import random

# --- 1. إعدادات الصفحة والجمالية الحيوية ---
st.set_page_config(page_title="Itqan English Pro", layout="wide", initial_sidebar_state="expanded")

# كود CSS للألوان الحيوية والرسومات والنصوص السوداء في الإدارة
st.markdown("""
    <style>
    /* إخفاء زوائد المنصة */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}
    
    /* التصميم العام: خلفية حيوية ورسومات */
    .stApp {
        background-color: #e0f7fa;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='%23b2ebf2' fill-opacity='0.4'%3E%3Cpath d='M14 16h2v2h-2zM28 32h2v2h-2zM10 60h2v2h-2zM66 12h2v2h-2zM70 46h2v2h-2z'/%3E%3C/g%3E%3C/svg%3E");
    }
    
    /* جعل نصوص لوحة الإدارة (Tabs, Labels) سوداء تماماً كما طلبت */
    button[data-baseweb="tab"] p { color: black !important; font-weight: bold !important; font-size: 18px !important; }
    label, .stMarkdown p, .stSelectbox label, .stHeader h1 { color: black !important; font-weight: bold !important; }
    .stAlert p { color: black !important; font-weight: bold !important; }
    
    /* تصميم بطاقات الجمل للطلاب */
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        border-right: 8px solid #00acc1;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,172,193,0.1);
    }
    .en-text { font-size: 28px; font-weight: 800; color: #006064; }
    .ar-text { font-size: 22px; color: #00acc1; direction: rtl; font-weight: 600; }
    
    /* أزرار حيوية */
    .stButton>button {
        border-radius: 12px;
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

async def generate_voice(text, filename, voice_key, rate=0):
    speed = f"{rate:+d}%"
    communicate = edge_tts.Communicate(text, VOICES[voice_key], rate=speed)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

# --- 3. تعريف المتغيرات الأساسية (الحل للخطأ) ---
data = load_data()
categories = list(data["categories"].keys())
# هنا قمنا بتعريف is_admin قبل استخدامه
is_admin = st.query_params.get("admin") == "true"

# --- 4. القائمة الجانبية (تظهر للجميع) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:black;'>🎧 إعدادات الصوت</h2>", unsafe_allow_html=True)
    user_voice = st.selectbox("اختر الصوت المفضل:", list(VOICES.keys()))
    user_speed = st.slider("سرعة النطق:", -50, 50, 0, step=10)
    st.divider()
    app_mode = st.radio("النمط:", ["📚 مكتبة الجمل", "🧠 اختبار الذاكرة"])
    search_q = st.text_input("🔍 بحث...")

# --- 5. لوحة الإدارة (Hidden Admin Panel) ---
if is_admin:
    st.markdown("<h1 style='text-align:center; color:black;'>🛠 لوحة الإدارة</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["إضافة محتوى", "تعديل وحذف", "إدارة الأقسام"])
    
    with tab1:
        st.markdown("<p style='color:black;'>إنشاء قسم جديد:</p>", unsafe_allow_html=True)
        new_c = st.text_input("اسم القسم:")
        if st.button("حفظ القسم"):
            if new_c and new_c not in data["categories"]:
                data["categories"][new_c] = []
                save_data(data); st.rerun()
        
        st.divider()
        if categories:
            st.markdown("<p style='color:black;'>إضافة جملة (جملة | ترجمة | نطق):</p>", unsafe_allow_html=True)
            target = st.selectbox("إضافة إلى:", categories)
            raw = st.text_area("النصوص:")
            if st.button("🚀 حفظ الجملة"):
                lines = raw.strip().split('\n')
                for line in lines:
                    if "|" in line:
                        en, ar, pr = [p.strip() for p in line.split("|")]
                        data["categories"][target].append({"en": en, "ar": ar, "pron": pr})
                save_data(data); st.success("تم الحفظ!"); st.rerun()

    with tab2:
        if categories:
            manage_cat = st.selectbox("تعديل من قسم:", categories)
            for idx, item in enumerate(data["categories"][manage_cat]):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{item['en']}**")
                if c2.button("🗑 حذف", key=f"del_{idx}"):
                    data["categories"][manage_cat].pop(idx)
                    save_data(data); st.rerun()

    with tab3:
        if categories:
            cat_to_del = st.selectbox("حذف قسم بالكامل", categories)
            # النص باللون الأسود كما طلبت
            st.warning(f"هل أنت متأكد من حذف قسم '{cat_to_del}' بالكامل؟")
            if st.button("🔥 تأكيد الحذف النهائي"):
                del data["categories"][cat_to_del]
                save_data(data); st.rerun()

# --- 6. واجهة الطلاب (Student Interface) ---
else:
    st.markdown("<h1 style='text-align: center; color: #007ea7;'>📚 منصة إتقان للغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    if categories:
        choice = st.selectbox("اختر الوحدة:", categories)
        items = data["categories"][choice]
        
        if search_q:
            items = [i for i in items if search_q.lower() in i['en'].lower()]

        if app_mode == "📚 مكتبة الجمل":
            for idx, item in enumerate(items):
                st.markdown(f"""
                <div class="card">
                    <div class="en-text">{item['en']}</div>
                    <div class="ar-text">{item['ar']}</div>
                    <div style='color:#777; font-style:italic;'>{item['pron']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # توليد الصوت ديناميكياً حسب اختيار الطالب
                v_id = VOICES[user_voice].split('-')[2]
                f_name = f"{item['en'][:15].replace(' ','_').lower()}_{v_id}_{user_speed}.mp3"
                f_path = os.path.join(AUDIO_DIR, f_name)
                
                if not os.path.exists(f_path):
                    with st.spinner("جاري تحضير نبرة الصوت..."):
                        asyncio.run(generate_voice(item['en'], f_name, user_voice, user_speed))
                
                with open(f_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                
                # المفضلة و Notion
                c_f, c_n = st.columns([1, 1])
                is_f = item['en'] in data.get('favorites', [])
                if c_f.button("⭐" if is_f else "☆", key=f"fav_{idx}"):
                    if 'favorites' not in data: data['favorites'] = []
                    if is_f: data['favorites'].remove(item['en'])
                    else: data['favorites'].append(item['en'])
                    save_data(data); st.rerun()
                if c_n.button("📋 Notion", key=f"not_{idx}"):
                    st.code(f"**{item['en']}** | {item['ar']}")
        
        else: # نمط الاختبار
            st.subheader("🧠 اختبر ذاكرتك")
            if items:
                if 'quiz_item' not in st.session_state: st.session_state.quiz_item = random.choice(items)
                q = st.session_state.quiz_item
                
                v_id = VOICES[user_voice].split('-')[2]
                f_name = f"{q['en'][:15].replace(' ','_').lower()}_{v_id}_{user_speed}.mp3"
                f_path = os.path.join(AUDIO_DIR, f_name)
                
                if not os.path.exists(f_path):
                    asyncio.run(generate_voice(q['en'], f_name, user_voice, user_speed))
                
                with open(f_path, "rb") as f: st.audio(f.read())
                if st.button("👁️ كشف المعنى"):
                    st.success(f"الترجمة: {q['ar']}")
                    if st.button("🔄 جملة أخرى"):
                        del st.session_state.quiz_item
                        st.rerun()
    else:
        st.info("أهلاً بك! ابدأ بإضافة الأقسام من لوحة التحكم (?admin=true).")