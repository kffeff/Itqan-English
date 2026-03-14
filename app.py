import streamlit as st
import json
import os
import asyncio
import edge_tts
import base64

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide")

# كود CSS احترافي لتعديل الخطوط، الأيقونات، ومشغل الصوت
st.markdown("""
    <style>
    /* إخفاء القوائم الافتراضية لزيادة الاحترافية */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
    
    .stApp {
        background-color: #f8fbff;
    }

    /* تصميم البطاقة الرئيسية */
    .card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border-right: 12px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        text-align: center;
        width: 100%;
    }

    .en-text { 
        font-size: 32px; 
        font-weight: 900; 
        color: #1e293b; 
        margin-bottom: 10px;
    }

    .ar-text { 
        font-size: 24px; 
        color: #10b981; 
        font-weight: 600; 
        margin-bottom: 15px;
    }

    /* تعديل سطر النطق (كبير جداً وواضح) */
    .pron-box {
        background-color: #fff1f2;
        padding: 15px;
        border-radius: 15px;
        border: 2px dashed #f43f5e;
        color: #e11d48;
        font-size: 35px; /* تكبير الخط كما طلبت */
        font-weight: 800;
        margin-top: 10px;
        display: inline-block;
        width: 100%;
        line-height: 1.5;
    }

    /* تنسيق مشغل الصوت ليعمل بوضوح على المتصفحات */
    audio {
        width: 100%;
        height: 45px;
        margin-top: 15px;
        border-radius: 10px;
    }

    /* أيقونة الإعدادات الجانبية */
    .floating-settings {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والصوت ---
DB_FILE = "data.json"
AUDIO_DIR = "audio_cache"
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

VOICES = {
    "🎙️ أمريكي - هادئ (Guy)": "en-US-GuyNeural",
    "🎙️ أمريكية - واضحة (Ava)": "en-US-AvaNeural",
    "🎙️ بريطاني - رزين (Sonia)": "en-GB-SoniaNeural"
}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"categories": {}, "favorites": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

async def generate_voice(text, filename, voice_key, rate):
    # تم ضبط الـ rate ليكون بطيئاً لضمان عدم "بلع" الحروف
    communicate = edge_tts.Communicate(text, VOICES[voice_key], rate=rate)
    await communicate.save(os.path.join(AUDIO_DIR, filename))

def get_audio_html(file_path):
    """تحويل الملف الصوتي ليعمل على الآيفون بسلاسة عبر Base64"""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio controls preload="auto"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"

# --- 3. أيقونة الإعدادات (تظهر وتختفي) ---
# استخدمنا Popover ليكون بمثابة الأيقونة التي تفتح وتغلق قائمة الأصوات
with st.sidebar:
    st.markdown("### ⚙️ إعدادات المنصة")
    u_voice = st.selectbox("اختر صوت المعلم:", list(VOICES.keys()))
    # ضبط السرعة الافتراضية لتكون -25% لضمان نطق الحروف بوضوح
    u_speed = st.slider("سرعة النطق (يفضل بطيئة):", -50, 0, -25, step=5)
    st.divider()
    search_q = st.text_input("🔍 ابحث عن جملة:")

# --- 4. لوحة الإدارة (فقط عند طلبها) ---
if is_admin:
    st.title("🛠 إدارة محتوى المنصة")
    # (كود الإدارة يظل كما هو مع تحسينات طفيفة في الحفظ)
    new_c = st.text_input("اسم القسم الجديد:")
    if st.button("إضافة القسم"):
        data["categories"][new_c] = []; save_data(data); st.rerun()
    
    if categories:
        target = st.selectbox("اختر القسم للإضافة:", categories)
        raw = st.text_area("أدخل البيانات (جملة | ترجمة | نطق)")
        if st.button("حفظ الجمل"):
            for line in raw.strip().split('\n'):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
            save_data(data); st.success("تم التحديث بنجاح!"); st.rerun()

# --- 5. واجهة الطالب (منصة إتقان اللغة الإنجليزية) ---
else:
    st.markdown("<h1 style='text-align: center; color: #007bff; font-family: Cairo;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    if categories:
        # جعل اختيار الوحدة في الأعلى بشكل واضح
        choice = st.selectbox("📂 اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        
        if search_q:
            items = [i for i in items if search_q.lower() in i['en'].lower()]

        for idx, item in enumerate(items):
            # عرض البطاقة
            st.markdown(f"""
            <div class="card">
                <div class="en-text">{item['en']}</div>
                <div class="ar-text">{item['ar']}</div>
                <div class="pron-box">{item['pron']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # توليد الصوت ومعالجة مشكلة الأيفون
            v_code = VOICES[u_voice].split('-')[2]
            f_name = f"voice_{hash(item['en'])}_{v_code}_{u_speed}.mp3"
            f_path = os.path.join(AUDIO_DIR, f_name)
            
            if not os.path.exists(f_path):
                with st.spinner("جاري تحضير نطق المعلم..."):
                    asyncio.run(generate_voice(item['en'], f_name, u_voice, f"{u_speed}%"))
            
            # تشغيل الصوت عبر HTML المعدل للأيفون
            st.markdown(get_audio_html(f_path), unsafe_allow_html=True)
            st.divider()
    else:
        st.info("مرحباً بك! بانتظار إضافة الدروس من قبل الإدارة.")
