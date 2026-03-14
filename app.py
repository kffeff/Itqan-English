import streamlit as st
import json
import os
import asyncio
import edge_tts
import base64
import hashlib
from typing import Dict, Any

# ====== إعدادات ملف المشروع ======
DB_FILE = os.path.join(os.getcwd(), "data.json")
AUDIO_DIR = os.path.join(os.getcwd(), "audio_cache")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICES = {
    "🎙️ صوت رجالي واضح (Guy)": "en-US-GuyNeural",
    "🎙️ صوت نسائي رقيق (Ava)": "en-US-AvaNeural",
    "🎙️ صوت بريطاني فخم (Sonia)": "en-GB-SoniaNeural",
}

# ====== واجهة الصفحة والـ CSS ======
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide")

st.markdown(
    """
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

    /* سطر النطق: كبير جداً وواضح */
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

    /* زر الإعدادات العائم */
    .float-settings {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
    }

    .float-settings button{
        border-radius: 50% !important;
        width: 65px !important;
        height: 65px !important;
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(0,123,255,0.5) !important;
        font-size: 22px;
    }

    audio { width: 100%; height: 50px; margin-top: 20px; border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ====== إدارة البيانات ======

def load_data() -> Dict[str, Any]:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {"categories": {}, "favorites": []}
    return {"categories": {}, "favorites": []}


def save_data(data: Dict[str, Any]):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ====== الصوت (توليد وحفظ) ======
async def _generate_voice_async(ssml: str, output_path: str, voice: str):
    communicate = edge_tts.Communicate(ssml, voice)
    await communicate.save(output_path)


def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


def generate_voice(text: str, out_filename: str, voice_id: str, rate_percent: int) -> bool:
    """
    يُنشئ ملف صوتي بصيغة mp3 باستخدام edge-tts.
    rate_percent: عدد سالب أو موجب يمثل نسبة السرعة، مثال -30
    يعيد True عند النجاح و False عند الفشل (مع طباعة الخطأ في الواجهة).
    """
    out_path = os.path.join(AUDIO_DIR, out_filename)
    # بناء SSML مع prosody للتحكم بالسرعة بدقة
    rate_str = f"{rate_percent}%"
    ssml = f"<speak><prosody rate='{rate_str}'>{text}</prosody></speak>"
    try:
        run_async(_generate_voice_async(ssml, out_path, voice_id))
        return True
    except Exception as e:
        st.error(f"فشل توليد الصوت: {e}")
        return False


def get_audio_html(file_path: str, audio_id: str) -> str:
    """تشفير الملف بصيغة base64 وادراجه داخل وسم <audio> ليعمل على سفاري الآيفون."""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<audio id="{audio_id}" controls preload="auto"><source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg"></audio>'


# ====== تهيئة الحالة الجلسية ======
if "settings_open" not in st.session_state:
    st.session_state.settings_open = False

if "selected_voice_key" not in st.session_state:
    st.session_state.selected_voice_key = list(VOICES.keys())[0]

if "selected_speed" not in st.session_state:
    st.session_state.selected_speed = -30  # قيمة افتراضية بطيئة وواضحة

if "search_q" not in st.session_state:
    st.session_state.search_q = ""

# ====== تحميل البيانات ======
data = load_data()
categories = list(data.get("categories", {}).keys())

# ====== التحقق من كون المستخدم أدمن عبر باراميتر الرابط ======
params = st.query_params
is_admin = str(params.get("admin", "false")).lower() == "true"

# ====== زر الإعدادات العائم + لوحة الإعدادات (باستخدام popover إن توفر، وإلا fallback) ======

# حاول استخدام st.popover إن كانت متاحة
settings_container = None
if hasattr(st, "popover"):
    try:
        settings_container = st.popover("⚙️")
    except Exception:
        settings_container = None

if settings_container is not None:
    with settings_container:
        st.markdown("### 🛠 إعدادات النطق")
        st.selectbox("اختر المعلم:", list(VOICES.keys()), key="selected_voice_key")
        st.slider("سرعة النطق:", -50, 0, st.session_state.selected_speed, step=5, key="selected_speed")
        st.divider()
        st.text_input("🔍 بحث سريع:", key="search_q")
else:
    # Fallback: زر عائم يفتح/يغلق صندوق الإعدادات في أسفل الشاشة
    st.markdown(
        "<div class='float-settings'><button id='settings-btn'>⚙️</button></div>",
        unsafe_allow_html=True,
    )
    # الزر العائم لا يرسل حدث مباشرة؛ نعرض كتلة إعدادات قابلة للتوسيع
    with st.expander("⚙️ إعدادات النطق"):
        st.selectbox("اختر المعلم:", list(VOICES.keys()), key="selected_voice_key")
        st.slider("سرعة النطق:", -50, 0, st.session_state.selected_speed, step=5, key="selected_speed")
        st.divider()
        st.text_input("🔍 بحث سريع:", key="search_q")

# ====== عنوان المنصة ======
st.markdown("<h1 style='text-align: center; color: #007bff; font-family: Cairo;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)

# ====== واجهة الإدارة ======
if is_admin:
    st.title("🛠 لوحة الإدارة الكاملة")
    tab1, tab2 = st.tabs(["➕ إضافة محتوى", "🗑 إدارة وحذف"])

    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("حفظ القسم الجديد"):
            new_c = new_c.strip()
            if new_c:
                if new_c in data["categories"]:
                    st.warning("القسم موجود بالفعل.")
                else:
                    data["categories"][new_c] = []
                    save_data(data)
                    st.success("تم إنشاء القسم.")
                    st.experimental_rerun()
            else:
                st.error("الرجاء إدخال اسم قسم صالح.")

        if categories:
            st.divider()
            target = st.selectbox("إضافة إلى قسم:", categories)
            raw = st.text_area("جملة | ترجمة | نطق (سطر جديد لكل جملة)")
            if st.button("🚀 حفظ الجمل"):
                added = 0
                for line in raw.strip().split('\n'):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3 and parts[0]:
                        data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
                        added += 1
                if added:
                    save_data(data)
                    st.success(f"تم حفظ {added} جملة.")
                    st.experimental_rerun()
                else:
                    st.error("تأكد من تنسيق المدخلات (جملة | ترجمة | نطق).")

    with tab2:
        if categories:
            cat_to_del = st.selectbox("اختر قسماً لحذفه:", categories)
            if st.button("🔥 حذف القسم المختار نهائياً"):
                del data["categories"][cat_to_del]
                save_data(data)
                st.success("تم حذف القسم.")
                st.experimental_rerun()

            st.divider()
            st.warning("لحذف جملة معينة، اختر القسم أولاً:")
            cat_manage = st.selectbox("إدارة جمل القسم:", categories, key="manage_cat")
            # عرض كل جملة مع زر حذف
            for i, item in enumerate(list(data["categories"][cat_manage])):
                cols = st.columns([4, 1])
                cols[0].write(f"**{item['en']}**  —  {item['ar']}")
                if cols[1].button("حذف", key=f"del_{cat_manage}_{i}"):
                    data["categories"][cat_manage].pop(i)
                    save_data(data)
                    st.success("تم حذف الجملة.")
                    st.experimental_rerun()
        else:
            st.info("لا توجد أقسام. أضف أقساماً من التبويب السابق.")

# ====== واجهة الطالب ======
else:
    if categories:
        choice = st.selectbox("📂 اختر الوحدة الدراسية:", categories)
        items = data["categories"].get(choice, [])

        # تطبيق خيار البحث من الإعدادات
        q = st.session_state.get("search_q", "") or ""
        if q:
            items = [it for it in items if q.lower() in it.get('en', '').lower()]

        # إعدادات الصوت الحالية
        selected_voice_key = st.session_state.get("selected_voice_key", list(VOICES.keys())[0])
        selected_speed = st.session_state.get("selected_speed", -30)
        v_id = VOICES.get(selected_voice_key, list(VOICES.values())[0])

        for item in items:
            # HTML البطاقة
            st.markdown(f"""
            <div class="card">
                <div class="en-text">{item['en']}</div>
                <div class="ar-text">{item['ar']}</div>
                <div class="pron-box">{item['pron']}</div>
            </div>
            """, unsafe_allow_html=True)

            # إنشاء قيمة Hash فريدة تعتمد على النص + الصوت + السرعة
            unique_str = f"{item['en']}||{v_id}||{selected_speed}"
            file_hash = hashlib.md5(unique_str.encode()).hexdigest()
            f_name = f"audio_{file_hash}.mp3"
            f_path = os.path.join(AUDIO_DIR, f_name)

            # إذا لم يكن الملف موجوداً، نولده
            if not os.path.exists(f_path):
                ok = generate_voice(item['en'], f_name, v_id, selected_speed)
                if not ok:
                    st.warning("تعذر توليد الصوت حالياً. تأكد من اتصال السيرفر بالإنترنت.")

            # عرض الصوت بتشفير Base64 مع audio_id فريد
            audio_html = get_audio_html(f_path, file_hash)
            if audio_html:
                st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.info("لا يوجد ملف صوتي متاح.")

            st.divider()
    else:
        st.info("مرحباً بك! يرجى إضافة أقسام من لوحة الإدارة أولاً.")
