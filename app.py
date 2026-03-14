import streamlit as st
import json
import os
import asyncio
import edge_tts
import base64
import hashlib

# --- 1. إعدادات الصفحة والهوية البصرية ---
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

    /* ───────── البطاقة ───────── */
    .card {
        background: white;
        padding: 32px 28px 24px;
        border-radius: 22px;
        border-right: 10px solid #2563eb;
        margin-bottom: 28px;
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
        font-size: 40px;
        font-weight: 900;
        color: #1e293b;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }
    .ar-text {
        font-size: 26px;
        color: #059669;
        font-weight: 700;
        margin-bottom: 4px;
        font-family: 'Cairo', sans-serif;
    }

    /* ───────── صندوق النطق ───────── */
    .pron-box {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
        padding: 18px 24px;
        border-radius: 16px;
        border: 3px dashed #f43f5e;
        color: #e11d48;
        font-size: 46px;
        font-weight: 900;
        margin-top: 18px;
        display: block;
        width: 100%;
        line-height: 1.3;
        font-family: 'Cairo', sans-serif;
        letter-spacing: 1px;
    }

    /* ───────── مشغل الصوت ───────── */
    audio {
        width: 100%;
        height: 50px;
        margin-top: 18px;
        border-radius: 12px;
        outline: none;
    }

    /* ───────── زر Popover العائم ───────── */
    div[data-testid="stPopover"] > button {
        border-radius: 50% !important;
        width: 62px !important;
        height: 62px !important;
        font-size: 26px !important;
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 6px 24px rgba(37,99,235,0.45) !important;
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999 !important;
        cursor: pointer !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.08) !important;
        box-shadow: 0 10px 30px rgba(37,99,235,0.55) !important;
    }

    /* ───────── عنوان المنصة ───────── */
    .platform-title {
        text-align: center;
        color: #2563eb;
        font-family: 'Cairo', sans-serif;
        font-size: 42px;
        font-weight: 900;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .platform-subtitle {
        text-align: center;
        color: #64748b;
        font-family: 'Cairo', sans-serif;
        font-size: 18px;
        margin-bottom: 30px;
    }

    /* ───────── فاصل مميز ───────── */
    hr { border: none; border-top: 2px solid #e2e8f0; margin: 8px 0 20px; }
    </style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 2. إدارة البيانات
# ─────────────────────────────────────────────
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


async def _generate_voice(text: str, filename: str, voice_id: str, rate: str) -> None:
    """توليد ملف صوتي باستخدام edge-tts وحفظه."""
    communicate = edge_tts.Communicate(text, voice_id, rate=rate)
    await communicate.save(os.path.join(AUDIO_DIR, filename))


def generate_voice(text: str, filename: str, voice_id: str, rate: str) -> None:
    """واجهة متزامنة لتوليد الصوت — تعمل بشكل صحيح داخل Streamlit."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(_generate_voice(text, filename, voice_id, rate))


def get_audio_html(file_path: str, audio_id: str) -> str:
    """
    الحل النهائي لمشكلة Safari/iPhone:
    ─────────────────────────────────────
    Safari يُخزّن عنصر <audio> في الـ cache ويتجاهل تغيير الـ src.
    الحل: نضع الـ Base64 كاملاً في متغير JS، ثم نحذف العنصر القديم
    ونُنشئ عنصراً جديداً تماماً من الصفر في كل مرة.
    هذا يجبر Safari على التعامل مع الصوت كمورد جديد كلياً.
    """
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    return f"""
<div id="wrapper_{audio_id}" style="margin-top:18px;"></div>
<script>
(function() {{
    var wrapper = document.getElementById('wrapper_{audio_id}');
    if (!wrapper) return;

    // احذف أي عنصر audio قديم داخل هذا الـ wrapper
    wrapper.innerHTML = '';

    // أنشئ عنصر audio جديداً من الصفر
    var audio = document.createElement('audio');
    audio.controls = true;
    audio.preload  = 'auto';
    audio.style.cssText = 'width:100%;height:50px;border-radius:12px;display:block;';

    var source = document.createElement('source');
    source.type = 'audio/mpeg';
    source.src  = 'data:audio/mpeg;base64,{b64}';

    audio.appendChild(source);

    // load() يجبر Safari على قراءة الـ src الجديد وتجاهل الـ cache
    audio.load();

    wrapper.appendChild(audio);
}})();
</script>
"""


# ─────────────────────────────────────────────
# تحميل البيانات + قراءة المعاملات
# ─────────────────────────────────────────────
data = load_data()
categories = list(data["categories"].keys())
is_admin = st.query_params.get("admin") == "true"


# ─────────────────────────────────────────────
# 3. أيقونة الإعدادات العائمة (Popover)
# ─────────────────────────────────────────────
with st.popover("⚙️"):
    st.markdown("### 🛠 إعدادات النطق")
    selected_voice_key = st.selectbox(
        "اختر المعلم:", list(VOICES.keys()), key="v_sel"
    )
    selected_speed = st.slider(
        "سرعة النطق:", min_value=-50, max_value=0, value=-30, step=5, key="s_sel"
    )
    st.divider()
    search_q = st.text_input("🔍 بحث سريع:", key="search_q")


# ─────────────────────────────────────────────
# 4. عنوان المنصة
# ─────────────────────────────────────────────
st.markdown(
    "<div class='platform-title'>🎓 منصة إتقان اللغة الإنجليزية</div>"
    "<div class='platform-subtitle'>تعلّم الكلمات والجمل بنطق صحيح واضح</div>",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# 5. لوحة الإدارة (admin=true)
# ─────────────────────────────────────────────
if is_admin:
    st.title("🛠 لوحة الإدارة الكاملة")
    tab1, tab2 = st.tabs(["➕ إضافة محتوى", "🗑 إدارة وحذف"])

    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("💾 حفظ القسم الجديد") and new_c.strip():
            if new_c.strip() not in data["categories"]:
                data["categories"][new_c.strip()] = []
                save_data(data)
                st.success(f"تم إنشاء القسم: {new_c.strip()}")
                st.rerun()
            else:
                st.warning("هذا القسم موجود بالفعل.")

        if categories:
            st.divider()
            target = st.selectbox("إضافة إلى قسم:", categories, key="add_cat")
            raw = st.text_area(
                "الكلمة/الجملة | الترجمة | النطق  (سطر جديد لكل إدخال)",
                placeholder="Hello | مرحبا | هَلو\nGoodbye | وداعاً | غود-باي",
                height=160,
            )
            if st.button("🚀 حفظ الإدخالات") and raw.strip():
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
                    st.success(f"تم حفظ {added} إدخال بنجاح!")
                    st.rerun()
                else:
                    st.error("لم يُعثر على إدخالات صحيحة. تأكد من الصيغة: كلمة | ترجمة | نطق")

    with tab2:
        if categories:
            st.subheader("حذف قسم كامل")
            cat_to_del = st.selectbox("اختر القسم:", categories, key="del_cat")
            if st.button("🔥 حذف القسم نهائياً"):
                del data["categories"][cat_to_del]
                save_data(data)
                st.success(f"تم حذف القسم: {cat_to_del}")
                st.rerun()

            st.divider()
            st.subheader("حذف جملة/كلمة من قسم")
            cat_manage = st.selectbox("اختر القسم:", categories, key="manage_cat")
            items_m = data["categories"].get(cat_manage, [])
            if items_m:
                for i, item in enumerate(items_m):
                    col1, col2 = st.columns([5, 1])
                    col1.write(f"**{item['en']}** — {item['ar']}  |  *{item['pron']}*")
                    if col2.button("🗑 حذف", key=f"del_{cat_manage}_{i}"):
                        data["categories"][cat_manage].pop(i)
                        save_data(data)
                        st.rerun()
            else:
                st.info("هذا القسم فارغ.")
        else:
            st.info("لا توجد أقسام بعد. أضف قسماً من تبويب (إضافة محتوى).")


# ─────────────────────────────────────────────
# 6. واجهة الطالب
# ─────────────────────────────────────────────
else:
    if not categories:
        st.info("🌟 مرحباً بك! يرجى إضافة أقسام من لوحة الإدارة أولاً.")
    else:
        choice = st.selectbox("📂 اختر الوحدة الدراسية:", categories)
        items = list(data["categories"].get(choice, []))

        # تصفية البحث
        if search_q:
            q = search_q.lower()
            items = [
                it for it in items
                if q in it["en"].lower() or q in it["ar"] or q in it["pron"]
            ]

        if not items:
            st.warning("لا توجد نتائج تطابق بحثك.")
        else:
            v_id = VOICES[selected_voice_key]
            rate_str = f"{selected_speed:+d}%"   # مثال: "-30%"

            for item in items:
                # ── عرض البطاقة ──
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="en-text">{item['en']}</div>
                        <div class="ar-text">{item['ar']}</div>
                        <div class="pron-box">{item['pron']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ── توليد الصوت (Hashing يضمن ملفاً فريداً لكل مجموعة إعدادات) ──
                unique_str = f"{item['en']}|{v_id}|{selected_speed}"
                file_hash  = hashlib.md5(unique_str.encode()).hexdigest()
                f_name     = f"audio_{file_hash}.mp3"
                f_path     = os.path.join(AUDIO_DIR, f_name)

                if not os.path.exists(f_path):
                    with st.spinner("جارٍ توليد الصوت..."):
                        generate_voice(item["en"], f_name, v_id, rate_str)

                # ── عرض مشغل الصوت (Base64 يضمن العمل على iPhone/Safari) ──
                st.markdown(get_audio_html(f_path, file_hash), unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
