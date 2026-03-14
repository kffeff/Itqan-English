import streamlit as st
import streamlit.components.v1 as components
import json
import os
import asyncio
import edge_tts
import base64
import hashlib

# --- 1. Page config ---
st.set_page_config(
    page_title="منصة إتقان اللغة الإنجليزية",
    layout="wide",
    page_icon="🎓"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');

    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }
    .stApp { background-color: #f0f4ff; font-family: 'Cairo', sans-serif; }

    .card {
        background: white;
        padding: 32px 28px 24px;
        border-radius: 22px;
        border-right: 10px solid #2563eb;
        margin-bottom: 10px;
        box-shadow: 0 8px 32px rgba(37,99,235,0.10);
        text-align: center;
        width: 100%;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 48px rgba(37,99,235,0.16);
    }
    .en-text {
        font-size: 40px; font-weight: 900;
        color: #1e293b; margin-bottom: 6px; letter-spacing: 0.5px;
    }
    .ar-text {
        font-size: 26px; color: #059669; font-weight: 700;
        margin-bottom: 4px; font-family: 'Cairo', sans-serif;
    }
    .pron-box {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
        padding: 18px 24px; border-radius: 16px;
        border: 3px dashed #f43f5e; color: #e11d48;
        font-size: 46px; font-weight: 900; margin-top: 18px;
        display: block; width: 100%; line-height: 1.3;
        font-family: 'Cairo', sans-serif; letter-spacing: 1px;
    }
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 62px !important; height: 62px !important;
        font-size: 26px !important;
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important; border: none !important;
        box-shadow: 0 6px 24px rgba(37,99,255,0.45) !important;
        position: fixed !important; bottom: 30px !important;
        right: 30px !important; z-index: 9999 !important;
    }
    .platform-title {
        text-align: center; color: #2563eb;
        font-family: 'Cairo', sans-serif;
        font-size: 42px; font-weight: 900;
        margin-bottom: 8px;
    }
    .platform-subtitle {
        text-align: center; color: #64748b;
        font-family: 'Cairo', sans-serif;
        font-size: 18px; margin-bottom: 30px;
    }
    hr { border: none; border-top: 2px solid #e2e8f0; margin: 4px 0 20px; }

    /* ---- النصوص خارج الحقول: اسود (الخلفية فاتحة) ---- */
    label,
    .stTextInput label, .stTextArea label,
    .stSelectbox label, .stSlider label,
    .stTabs [data-baseweb="tab"],
    h1, h2, h3, h4,
    p, div[data-testid="stText"],
    .stMarkdown p,
    .stSelectbox span,
    div[data-baseweb="select"] span,
    .stAlert p,
    .stInfo p {
        color: #000000 !important;
        font-weight: 600;
    }

    /* التبويب النشط يبقى ازرق */
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2563eb !important;
    }

    /* ---- النصوص داخل حقول الادخال: ابيض على خلفية داكنة ---- */
    .stTextInput input,
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 2px solid #2563eb !important;
        border-radius: 10px !important;
        font-family: 'Cairo', sans-serif !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #94a3b8 !important;
    }

    /* ---- Selectbox: خلفية داكنة ونص ابيض ---- */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border: 2px solid #2563eb !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #ffffff !important;
    }

    /* ---- قائمة الخيارات المنسدلة ---- */
    ul[data-baseweb="menu"] {
        background-color: #1e293b !important;
    }
    ul[data-baseweb="menu"] li {
        color: #ffffff !important;
    }
    ul[data-baseweb="menu"] li:hover {
        background-color: #2563eb !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- 2. Data helpers ---
DB_FILE = "data.json"
AUDIO_DIR = "audio_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICES = {
    "🎙️ صوت رجالي واضح (Guy)":    "en-US-GuyNeural",
    "🎙️ صوت نسائي رقيق (Ava)":    "en-US-AvaNeural",
    "🎙️ صوت بريطاني فخم (Sonia)": "en-GB-SoniaNeural",
}


def load_data() -> dict:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}, "favorites": []}


def save_data(data: dict) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def _generate_voice(text: str, path: str, voice_id: str, rate: str) -> None:
    communicate = edge_tts.Communicate(text, voice_id, rate=rate)
    await communicate.save(path)


def generate_voice(text: str, filename: str, voice_id: str, rate: str) -> None:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(
        _generate_voice(text, os.path.join(AUDIO_DIR, filename), voice_id, rate)
    )


def render_audio(file_path: str) -> None:
    """
    Safari/iPhone fix:
    components.html() creates a brand-new iframe on every Streamlit re-render.
    Safari treats each iframe as a fresh page => zero cache => audio always updates.
    Audio is embedded as Base64 so no external URL is needed.
    """
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    html = (
        "<html><body style='margin:0;padding:4px 0 0 0;background:transparent;'>"
        "<audio controls preload='auto' "
        "style='width:100%;height:48px;border-radius:12px;display:block;'>"
        "<source src='data:audio/mpeg;base64," + b64 + "' type='audio/mpeg'>"
        "</audio></body></html>"
    )
    components.html(html, height=64)


# --- 3. Load state ---
data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"


# --- 4. Floating settings popover ---
with st.popover("⚙️"):
    st.markdown("### 🛠 اعدادات النطق")
    selected_voice_key = st.selectbox("اختر المعلم:", list(VOICES.keys()), key="v_sel")
    selected_speed = st.slider("سرعة النطق:", min_value=-50, max_value=0, value=-30, step=5, key="s_sel")
    st.divider()
    search_q = st.text_input("🔍 بحث سريع:", key="search_q")


# --- 5. Header ---
st.markdown(
    "<div class='platform-title'>🎓 منصة اتقان اللغة الانجليزية</div>"
    "<div class='platform-subtitle'>تعلم الكلمات والجمل بنطق صحيح واضح</div>",
    unsafe_allow_html=True,
)


# --- 6. Admin panel ---
if is_admin:
    st.title("🛠 لوحة الادارة الكاملة")
    tab1, tab2 = st.tabs(["➕ اضافة محتوى", "🗑 ادارة وحذف"])

    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("💾 حفظ القسم الجديد") and new_c.strip():
            if new_c.strip() not in data["categories"]:
                data["categories"][new_c.strip()] = []
                save_data(data)
                st.success(f"تم انشاء القسم: {new_c.strip()}")
                st.rerun()
            else:
                st.warning("هذا القسم موجود بالفعل.")

        if categories:
            st.divider()
            target = st.selectbox("اضافة الى قسم:", categories, key="add_cat")
            raw = st.text_area(
                "الكلمة/الجملة | الترجمة | النطق  (سطر جديد لكل ادخال)",
                placeholder="Hello | مرحبا | هلو\nGoodbye | وداعا | غود-باي",
                height=160,
            )
            if st.button("🚀 حفظ الادخالات") and raw.strip():
                added = 0
                for line in raw.strip().split("\n"):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3 and all(parts):
                        data["categories"][target].append(
                            {"en": parts[0], "ar": parts[1], "pron": parts[2]}
                        )
                        added += 1
                if added:
                    save_data(data)
                    st.success(f"تم حفظ {added} ادخال بنجاح!")
                    st.rerun()
                else:
                    st.error("تاكد من الصيغة: كلمة | ترجمة | نطق")

    with tab2:
        if categories:
            st.subheader("حذف قسم كامل")
            cat_to_del = st.selectbox("اختر القسم:", categories, key="del_cat")
            if st.button("🔥 حذف القسم نهائيا"):
                del data["categories"][cat_to_del]
                save_data(data)
                st.rerun()

            st.divider()
            st.subheader("حذف جملة/كلمة من قسم")
            cat_manage = st.selectbox("اختر القسم:", categories, key="manage_cat")
            items_m = data["categories"].get(cat_manage, [])
            if items_m:
                for i, item in enumerate(items_m):
                    col1, col2 = st.columns([5, 1])
                    col1.write(f"**{item['en']}** — {item['ar']}  |  *{item['pron']}*")
                    if col2.button("🗑", key=f"del_{cat_manage}_{i}"):
                        data["categories"][cat_manage].pop(i)
                        save_data(data)
                        st.rerun()
            else:
                st.info("هذا القسم فارغ.")
        else:
            st.info("لا توجد اقسام بعد.")


# --- 7. Student view ---
else:
    if not categories:
        st.info("مرحبا بك! يرجى اضافة اقسام من لوحة الادارة اولا.")
    else:
        choice = st.selectbox("📂 اختر الوحدة الدراسية:", categories)
        items = list(data["categories"].get(choice, []))

        if search_q:
            q = search_q.lower()
            items = [it for it in items if q in it["en"].lower() or q in it["ar"] or q in it["pron"]]

        if not items:
            st.warning("لا توجد نتائج تطابق بحثك.")
        else:
            v_id = VOICES[selected_voice_key]
            rate_str = f"{selected_speed:+d}%"

            for item in items:
                # Card
                st.markdown(
                    "<div class='card'>"
                    f"<div class='en-text'>{item['en']}</div>"
                    f"<div class='ar-text'>{item['ar']}</div>"
                    f"<div class='pron-box'>{item['pron']}</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )

                # Unique hash per (text + voice + speed)
                unique_str = f"{item['en']}|{v_id}|{selected_speed}"
                file_hash  = hashlib.md5(unique_str.encode()).hexdigest()
                f_name     = f"audio_{file_hash}.mp3"
                f_path     = os.path.join(AUDIO_DIR, f_name)

                if not os.path.exists(f_path):
                    with st.spinner("جار توليد الصوت..."):
                        generate_voice(item["en"], f_name, v_id, rate_str)

                # Render audio inside isolated iframe (Safari-safe)
                render_audio(f_path)

                st.markdown("<hr>", unsafe_allow_html=True)
