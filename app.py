import streamlit as st
import streamlit.components.v1 as components
import json, os, asyncio, edge_tts, base64, hashlib, random, time

# ══════════════════════════════════════════════════════
# 1. Page config
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide", page_icon="🎓")

# ── Dark mode state ──
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

DK = st.session_state.dark_mode
BG      = "#0f172a" if DK else "#f0f4ff"
CARD_BG = "#1e293b" if DK else "#ffffff"
TEXT    = "#f1f5f9" if DK else "#1e293b"
SUB     = "#94a3b8" if DK else "#64748b"
BORDER  = "#334155" if DK else "#e2e8f0"
INPUT_BG= "#334155" if DK else "#1e293b"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
#MainMenu,footer,header,.stDeployButton{{visibility:hidden;}}
.stApp{{background-color:{BG};font-family:'Cairo',sans-serif;}}

.card{{
    background:{CARD_BG};padding:32px 28px 24px;border-radius:22px;
    border-right:10px solid #2563eb;margin-bottom:10px;
    box-shadow:0 8px 32px rgba(37,99,235,0.12);text-align:center;width:100%;
    transition:transform 0.18s ease,box-shadow 0.18s ease;
}}
.card:hover{{transform:translateY(-4px);box-shadow:0 18px 48px rgba(37,99,235,0.2);}}
.en-text{{font-size:40px;font-weight:900;color:{TEXT};margin-bottom:6px;}}
.ar-text{{font-size:26px;color:#059669;font-weight:700;margin-bottom:4px;font-family:'Cairo',sans-serif;}}
.pron-box{{
    background:linear-gradient(135deg,#fff1f2 0%,#ffe4e6 100%);
    padding:14px 18px;border-radius:16px;border:3px dashed #f43f5e;
    color:#e11d48;font-size:clamp(22px,5vw,46px);font-weight:900;margin-top:14px;
    display:block;width:100%;line-height:1.4;font-family:'Cairo',sans-serif;
    word-break:break-word;overflow-wrap:break-word;
}}
@media(max-width:600px){{
    .pron-box{{font-size:clamp(18px,4.5vw,28px)!important;padding:10px 12px;}}
    .en-text{{font-size:clamp(22px,6vw,32px)!important;}}
    .ar-text{{font-size:clamp(16px,4vw,22px)!important;}}
    .card{{padding:20px 16px 16px!important;}}
    .quiz-en{{font-size:clamp(22px,6vw,36px)!important;}}
}}

/* Quiz */
.quiz-card{{
    background:{CARD_BG};padding:40px 32px;border-radius:24px;
    border-top:8px solid #7c3aed;margin-bottom:16px;
    box-shadow:0 10px 40px rgba(124,58,237,0.15);text-align:center;width:100%;
}}
.quiz-en{{font-size:44px;font-weight:900;color:{TEXT};margin-bottom:8px;}}
.quiz-hint{{font-size:18px;color:{SUB};font-family:'Cairo',sans-serif;margin-bottom:20px;}}
.quiz-correct{{
    background:linear-gradient(135deg,#d1fae5,#a7f3d0);border:3px solid #059669;
    border-radius:16px;padding:20px;margin-top:16px;font-size:28px;
    font-weight:900;color:#065f46;font-family:'Cairo',sans-serif;
}}
.quiz-wrong{{
    background:linear-gradient(135deg,#fee2e2,#fecaca);border:3px solid #dc2626;
    border-radius:16px;padding:20px;margin-top:16px;font-size:22px;
    font-weight:700;color:#7f1d1d;font-family:'Cairo',sans-serif;
}}
.quiz-reveal{{
    background:linear-gradient(135deg,#ede9fe,#ddd6fe);border:3px solid #7c3aed;
    border-radius:16px;padding:20px;margin-top:16px;font-family:'Cairo',sans-serif;
}}
.quiz-score{{
    background:linear-gradient(135deg,#1e293b,#0f172a);border-radius:24px;padding:40px;
    text-align:center;color:white;font-family:'Cairo',sans-serif;
    box-shadow:0 20px 60px rgba(0,0,0,0.35);
}}
.score-number{{font-size:80px;font-weight:900;color:#fbbf24;line-height:1;}}
.score-label{{font-size:24px;color:#94a3b8;margin-top:8px;}}
.score-msg{{font-size:30px;font-weight:900;margin-top:20px;}}
.q-counter{{font-size:16px;color:{SUB};font-family:'Cairo',sans-serif;text-align:left;margin-bottom:4px;}}
.progress-bar-wrap{{background:{BORDER};border-radius:99px;height:12px;width:100%;margin:12px 0;}}
.progress-bar-fill{{background:linear-gradient(90deg,#7c3aed,#2563eb);height:12px;border-radius:99px;transition:width 0.4s ease;}}

/* Timer */
.timer-box{{
    background:linear-gradient(135deg,#7c3aed,#4f46e5);color:white;
    border-radius:16px;padding:12px 24px;font-size:28px;font-weight:900;
    text-align:center;margin-bottom:16px;font-family:'Cairo',sans-serif;
    box-shadow:0 4px 20px rgba(124,58,237,0.4);
}}
.timer-warn{{background:linear-gradient(135deg,#ef4444,#dc2626)!important;}}

/* Popover */
div[data-testid="stPopover"]>button{{
    border-radius:50%!important;width:62px!important;height:62px!important;
    font-size:26px!important;background:linear-gradient(135deg,#2563eb,#1d4ed8)!important;
    color:white!important;border:none!important;
    box-shadow:0 6px 24px rgba(37,99,255,0.45)!important;
    position:fixed!important;bottom:30px!important;right:30px!important;z-index:9999!important;
}}
.platform-title{{text-align:center;color:#2563eb;font-family:'Cairo',sans-serif;font-size:42px;font-weight:900;margin-bottom:8px;}}
.platform-subtitle{{text-align:center;color:{SUB};font-family:'Cairo',sans-serif;font-size:18px;margin-bottom:30px;}}
hr{{border:none;border-top:2px solid {BORDER};margin:4px 0 20px;}}

label,.stTextInput label,.stTextArea label,.stSelectbox label,.stSlider label,
.stTabs [data-baseweb="tab"],h1,h2,h3,h4,
p,div[data-testid="stText"],.stMarkdown p,
.stSelectbox span,div[data-baseweb="select"] span,
.stAlert p,.stInfo p{{color:{TEXT}!important;font-weight:600;}}
.stTabs [data-baseweb="tab"][aria-selected="true"]{{color:#2563eb!important;}}

.stTextInput input,.stTextArea textarea{{
    background-color:{INPUT_BG}!important;color:#ffffff!important;
    border:2px solid #2563eb!important;border-radius:10px!important;
    font-family:'Cairo',sans-serif!important;
}}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{{color:#94a3b8!important;}}
div[data-baseweb="select"]>div{{background-color:{INPUT_BG}!important;border:2px solid #2563eb!important;border-radius:10px!important;}}
div[data-baseweb="select"] span,div[data-baseweb="select"] div{{color:#ffffff!important;}}
ul[data-baseweb="menu"]{{background-color:{INPUT_BG}!important;}}
ul[data-baseweb="menu"] li{{color:#ffffff!important;}}
ul[data-baseweb="menu"] li:hover{{background-color:#2563eb!important;}}

div[data-testid="stPopoverBody"] label,div[data-testid="stPopoverBody"] p,
div[data-testid="stPopoverBody"] h3,div[data-testid="stPopoverBody"] .stMarkdown p,
div[data-testid="stPopoverBody"] div[data-testid="stText"],
div[data-testid="stPopoverBody"] .stSlider label,
div[data-testid="stPopoverBody"] .stSlider span{{color:#ffffff!important;}}
div[data-testid="stPopoverBody"] input{{background-color:#334155!important;color:#ffffff!important;border:2px solid #2563eb!important;border-radius:10px!important;}}
div[data-testid="stPopoverBody"] input::placeholder{{color:#94a3b8!important;}}
div[data-testid="stPopoverBody"] div[data-baseweb="select"]>div{{background-color:#334155!important;border:2px solid #2563eb!important;border-radius:10px!important;}}
div[data-testid="stPopoverBody"] div[data-baseweb="select"] span,
div[data-testid="stPopoverBody"] div[data-baseweb="select"] div{{color:#ffffff!important;}}

/* PDF print */
@media print{{
    .stApp>*:not(#print-area){{display:none!important;}}
    #print-area{{display:block!important;}}
    .print-card{{
        border:2px solid #2563eb;border-radius:12px;padding:20px;
        margin-bottom:16px;page-break-inside:avoid;text-align:center;
    }}
    .print-en{{font-size:28px;font-weight:900;color:#1e293b;}}
    .print-ar{{font-size:20px;color:#059669;font-weight:700;}}
    .print-pron{{font-size:22px;color:#e11d48;font-weight:900;border:2px dashed #f43f5e;border-radius:8px;padding:8px;margin-top:8px;}}
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 2. Data & Audio helpers
# ══════════════════════════════════════════════════════
DB_FILE   = "data.json"
AUDIO_DIR = "audio_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

if not os.path.exists(os.path.join(AUDIO_DIR, ".voices_updated_v2")):
    for _f in os.listdir(AUDIO_DIR):
        if _f.endswith(".mp3"):
            try: os.remove(os.path.join(AUDIO_DIR, _f))
            except: pass
    open(os.path.join(AUDIO_DIR, ".voices_updated_v2"), "w").close()

VOICES = {
    "🎓 صوت رجالي رسمي واضح (Andrew)": "en-US-AndrewMultilingualNeural",
    "🎓 صوت نسائي رسمي واضح (Emma)":   "en-US-EmmaMultilingualNeural",
    "🎓 صوت بريطاني اكاديمي (Ryan)":    "en-GB-RyanNeural",
}

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {"categories": {}, "favorites": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

async def _gen(text, path, voice, rate):
    await edge_tts.Communicate(text, voice, rate=rate).save(path)

def generate_voice(text, filename, voice, rate):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed(): raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    loop.run_until_complete(_gen(text, os.path.join(AUDIO_DIR, filename), voice, rate))

def render_audio(file_path):
    with open(file_path, "rb") as f: b64 = base64.b64encode(f.read()).decode()
    components.html(
        "<html><body style='margin:0;padding:4px 0 0 0;background:transparent;'>"
        "<audio controls preload='auto' style='width:100%;height:48px;border-radius:12px;display:block;'>"
        "<source src='data:audio/mpeg;base64," + b64 + "' type='audio/mpeg'>"
        "</audio></body></html>", height=64)

def ensure_audio(text, v_id, speed):
    fhash = hashlib.md5(f"{text}|{v_id}|{speed}".encode()).hexdigest()
    fname = f"audio_{fhash}.mp3"
    fpath = os.path.join(AUDIO_DIR, fname)
    if not os.path.exists(fpath):
        with st.spinner("جار توليد الصوت..."): generate_voice(text, fname, v_id, f"{speed:+d}%")
    return fpath

def normalize(s):
    return s.strip().replace("،","").replace(",","").replace(".","").replace(" ","")


# ══════════════════════════════════════════════════════
# 3. Session state init
# ══════════════════════════════════════════════════════
DEFAULTS = {
    "quiz_active": False, "quiz_mode": "normal",  # normal | listen | timer
    "quiz_items": [], "quiz_idx": 0, "quiz_score": 0,
    "quiz_answered": False, "quiz_user_ans": "", "quiz_show_ans": False,
    "quiz_results": [], "timer_start": 0, "timer_seconds": 30,
    "timer_expired": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v


# ══════════════════════════════════════════════════════
# 4. Load data
# ══════════════════════════════════════════════════════
data       = load_data()
categories = list(data["categories"].keys())
is_admin   = st.query_params.get("admin") == "true"


# ══════════════════════════════════════════════════════
# 5. Popover (settings)
# ══════════════════════════════════════════════════════
with st.popover("⚙️"):
    st.markdown("### 🛠 اعدادات النطق")
    selected_voice_key = st.selectbox("اختر المعلم:", list(VOICES.keys()), key="v_sel")
    selected_speed     = st.slider("سرعة النطق:", -50, 0, -30, 5, key="s_sel")
    st.divider()
    search_q = st.text_input("🔍 بحث سريع:", key="search_q")
    st.divider()
    # Dark mode toggle inside popover
    dm_label = "☀️ الوضع النهاري" if DK else "🌙 الوضع الليلي"
    if st.button(dm_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


# ══════════════════════════════════════════════════════
# 6. Header
# ══════════════════════════════════════════════════════
st.markdown(
    "<div class='platform-title'>🎓 منصة اتقان اللغة الانجليزية</div>"
    "<div class='platform-subtitle'>تعلم الكلمات والجمل بنطق صحيح واضح</div>",
    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 7. ADMIN
# ══════════════════════════════════════════════════════
if is_admin:
    st.title("🛠 لوحة الادارة الكاملة")
    tab1, tab2 = st.tabs(["➕ اضافة محتوى", "🗑 ادارة وحذف"])
    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("💾 حفظ القسم الجديد") and new_c.strip():
            if new_c.strip() not in data["categories"]:
                data["categories"][new_c.strip()] = []; save_data(data)
                st.success(f"تم انشاء القسم: {new_c.strip()}"); st.rerun()
            else: st.warning("هذا القسم موجود بالفعل.")
        if categories:
            st.divider()
            target = st.selectbox("اضافة الى قسم:", categories, key="add_cat")
            raw = st.text_area("الكلمة/الجملة | الترجمة | النطق  (سطر جديد لكل ادخال)",
                placeholder="Hello | مرحبا | هلو\nGoodbye | وداعا | غود-باي", height=160)
            if st.button("🚀 حفظ الادخالات") and raw.strip():
                added = 0
                for line in raw.strip().split("\n"):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3 and all(parts):
                        data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]}); added += 1
                if added: save_data(data); st.success(f"تم حفظ {added} ادخال!"); st.rerun()
                else: st.error("تاكد من الصيغة: كلمة | ترجمة | نطق")
    with tab2:
        if categories:
            st.subheader("حذف قسم كامل")
            cat_to_del = st.selectbox("اختر القسم:", categories, key="del_cat")
            if st.button("🔥 حذف القسم نهائيا"):
                del data["categories"][cat_to_del]; save_data(data); st.rerun()
            st.divider()
            st.subheader("حذف جملة/كلمة من قسم")
            cat_manage = st.selectbox("اختر القسم:", categories, key="manage_cat")
            items_m = data["categories"].get(cat_manage, [])
            if items_m:
                for i, item in enumerate(items_m):
                    c1, c2 = st.columns([5,1])
                    c1.write(f"**{item['en']}** — {item['ar']}  |  *{item['pron']}*")
                    if c2.button("🗑", key=f"del_{cat_manage}_{i}"):
                        data["categories"][cat_manage].pop(i); save_data(data); st.rerun()
            else: st.info("هذا القسم فارغ.")
        else: st.info("لا توجد اقسام بعد.")


# ══════════════════════════════════════════════════════
# 8. STUDENT VIEW
# ══════════════════════════════════════════════════════
else:
    if not categories:
        st.info("مرحبا بك! يرجى اضافة اقسام من لوحة الادارة اولا.")
    else:
        choice = st.selectbox("📂 اختر القسم الذي يناسبك:", categories)
        items  = list(data["categories"].get(choice, []))
        if search_q:
            q = search_q.lower()
            items = [it for it in items if q in it["en"].lower() or q in it["ar"] or q in it["pron"]]

        if not items:
            st.warning("لا توجد نتائج تطابق بحثك.")
        else:
            v_id = VOICES[selected_voice_key]

            # ── أزرار الأوضاع الأربعة ──
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("📖 دراسة", use_container_width=True,
                             type="primary" if not st.session_state.quiz_active else "secondary"):
                    st.session_state.quiz_active = False; st.rerun()
            with c2:
                if st.button("📝 اختبار", use_container_width=True,
                             type="primary" if st.session_state.quiz_active and st.session_state.quiz_mode=="normal" else "secondary"):
                    shuffled = items.copy(); random.shuffle(shuffled)
                    st.session_state.update({"quiz_active":True,"quiz_mode":"normal","quiz_items":shuffled,
                        "quiz_idx":0,"quiz_score":0,"quiz_answered":False,"quiz_user_ans":"",
                        "quiz_show_ans":False,"quiz_results":[]}); st.rerun()
            with c3:
                if st.button("🔊 استماع", use_container_width=True,
                             type="primary" if st.session_state.quiz_active and st.session_state.quiz_mode=="listen" else "secondary"):
                    shuffled = items.copy(); random.shuffle(shuffled)
                    st.session_state.update({"quiz_active":True,"quiz_mode":"listen","quiz_items":shuffled,
                        "quiz_idx":0,"quiz_score":0,"quiz_answered":False,"quiz_user_ans":"",
                        "quiz_show_ans":False,"quiz_results":[]}); st.rerun()
            with c4:
                if st.button("⏱️ موقوت", use_container_width=True,
                             type="primary" if st.session_state.quiz_active and st.session_state.quiz_mode=="timer" else "secondary"):
                    shuffled = items.copy(); random.shuffle(shuffled)
                    st.session_state.update({"quiz_active":True,"quiz_mode":"timer","quiz_items":shuffled,
                        "quiz_idx":0,"quiz_score":0,"quiz_answered":False,"quiz_user_ans":"",
                        "quiz_show_ans":False,"quiz_results":[],"timer_start":time.time(),"timer_expired":False}); st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)

            # ════════════════════════════════
            # وضع الدراسة + PDF
            # ════════════════════════════════
            if not st.session_state.quiz_active:
                # زر طباعة PDF
                if st.button("🖨️ طباعة القسم كـ PDF", use_container_width=False):
                    cards_html = ""
                    for it in items:
                        cards_html += f"""
                        <div class='print-card'>
                            <div class='print-en'>{it['en']}</div>
                            <div class='print-ar'>{it['ar']}</div>
                            <div class='print-pron'>{it['pron']}</div>
                        </div>"""
                    pdf_html = f"""
                    <html dir='rtl'>
                    <head>
                    <meta charset='utf-8'>
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
                        body{{font-family:'Cairo',sans-serif;padding:20px;direction:rtl;}}
                        h1{{text-align:center;color:#2563eb;font-size:28px;margin-bottom:8px;}}
                        h2{{text-align:center;color:#64748b;font-size:16px;margin-bottom:24px;font-weight:400;}}
                        .print-card{{border:2px solid #2563eb;border-radius:12px;padding:20px;
                            margin-bottom:16px;page-break-inside:avoid;text-align:center;}}
                        .print-en{{font-size:28px;font-weight:900;color:#1e293b;}}
                        .print-ar{{font-size:20px;color:#059669;font-weight:700;margin-top:6px;}}
                        .print-pron{{font-size:22px;color:#e11d48;font-weight:900;border:2px dashed #f43f5e;
                            border-radius:8px;padding:8px;margin-top:10px;}}
                        @media print{{@page{{margin:15mm;}}}}
                    </style>
                    </head>
                    <body>
                    <h1>🎓 منصة اتقان اللغة الانجليزية</h1>
                    <h2>قسم: {choice} — عدد الكلمات: {len(items)}</h2>
                    {cards_html}
                    <script>window.onload=function(){{window.print();}}</script>
                    </body></html>"""
                    b64_pdf = base64.b64encode(pdf_html.encode("utf-8")).decode()
                    components.html(
                        f'<iframe src="data:text/html;base64,{b64_pdf}" '
                        f'style="display:none" id="pf"></iframe>'
                        f'<script>document.getElementById("pf").onload=function(){{this.contentWindow.print();}}</script>',
                        height=0)

                st.markdown("<br>", unsafe_allow_html=True)

                for item in items:
                    st.markdown(
                        f"<div class='card'><div class='en-text'>{item['en']}</div>"
                        f"<div class='ar-text'>{item['ar']}</div>"
                        f"<div class='pron-box'>{item['pron']}</div></div>",
                        unsafe_allow_html=True)
                    render_audio(ensure_audio(item["en"], v_id, selected_speed))
                    st.markdown("<hr>", unsafe_allow_html=True)

            # ════════════════════════════════
            # دالة مشتركة: عرض نتيجة الاختبار
            # ════════════════════════════════
            else:
                quiz_items = st.session_state.quiz_items
                idx        = st.session_state.quiz_idx
                total      = len(quiz_items)
                mode       = st.session_state.quiz_mode

                def show_results():
                    score = st.session_state.quiz_score
                    pct   = int(score / total * 100) if total else 0
                    msg, color = (
                        ("🏆 ممتاز! اجبت على كل الاسئلة صحيحة!", "#10b981") if pct==100 else
                        ("👍 جيد جداً! استمر في التطور", "#f59e0b") if pct>=70 else
                        ("💪 لا باس! راجع الكلمات وحاول مجدداً", "#ef4444")
                    )
                    st.markdown(f"""
                    <div class='quiz-score'>
                        <div style='font-size:32px;font-weight:900;margin-bottom:16px;'>نتيجة الاختبار</div>
                        <div class='score-number'>{score}/{total}</div>
                        <div class='score-label'>اجبت بشكل صحيح على {score} من اصل {total} سؤال</div>
                        <div class='score-msg' style='color:{color}'>{msg}</div>
                        <div style='margin-top:24px;background:#1e293b;border-radius:99px;height:16px;'>
                            <div style='background:linear-gradient(90deg,#7c3aed,#2563eb);height:16px;border-radius:99px;width:{pct}%;'></div>
                        </div>
                        <div style='color:#94a3b8;margin-top:8px;font-size:20px;'>{pct}%</div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.expander("📋 مراجعة اجاباتك"):
                        for r in st.session_state.quiz_results:
                            icon = "✅" if r["correct"] else "❌"
                            st.markdown(f"{icon} **{r['en']}**  \nاجابتك: *{r['user']}*  \nالصحيحة: *{r['ar']}*")
                            st.divider()
                    if st.button("🔄 اعادة الاختبار", type="primary", use_container_width=True):
                        shuffled = items.copy(); random.shuffle(shuffled)
                        st.session_state.update({"quiz_items":shuffled,"quiz_idx":0,"quiz_score":0,
                            "quiz_answered":False,"quiz_user_ans":"","quiz_show_ans":False,
                            "quiz_results":[],"timer_start":time.time(),"timer_expired":False}); st.rerun()

                def handle_answer(item, user_ans, show_only):
                    correct_ar = item["ar"].strip()
                    if show_only:
                        st.markdown(f"""
                        <div class='quiz-reveal'>
                            <div style='font-size:20px;color:#5b21b6;font-weight:700;margin-bottom:8px;'>الاجابة الصحيحة:</div>
                            <div style='font-size:32px;font-weight:900;color:#4c1d95;'>{correct_ar}</div>
                            <div style='font-size:18px;color:#6d28d9;margin-top:8px;'>النطق: {item['pron']}</div>
                        </div>""", unsafe_allow_html=True)
                        st.session_state.quiz_results.append({"en":item["en"],"ar":correct_ar,"user":"—","correct":False})
                    else:
                        is_correct = normalize(user_ans) == normalize(correct_ar)
                        if is_correct:
                            st.session_state.quiz_score += 1
                            st.markdown(f"<div class='quiz-correct'>✅ اجابة صحيحة! 🎉<br><span style='font-size:24px;'>{correct_ar}</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class='quiz-wrong'>❌ اجابة خاطئة<br>
                            <span style='font-size:18px;'>اجابتك: {user_ans}</span><br>
                            <span style='font-size:22px;color:#991b1b;'>✔ الصحيحة: {correct_ar}</span><br>
                            <span style='font-size:18px;color:#7f1d1d;'>النطق: {item['pron']}</span></div>""", unsafe_allow_html=True)
                        st.session_state.quiz_results.append({"en":item["en"],"ar":correct_ar,"user":user_ans,"correct":is_correct})

                def next_btn(idx, total):
                    lbl = "➡️ السؤال التالي" if idx+1 < total else "🏁 اظهر النتيجة النهائية"
                    if st.button(lbl, type="primary", use_container_width=True):
                        st.session_state.quiz_idx      += 1
                        st.session_state.quiz_answered  = False
                        st.session_state.quiz_user_ans  = ""
                        st.session_state.quiz_show_ans  = False
                        if mode == "timer": st.session_state.timer_start = time.time()
                        st.session_state.timer_expired  = False
                        st.rerun()

                # انتهى الاختبار
                if idx >= total:
                    show_results()

                # سؤال حالي
                else:
                    item    = quiz_items[idx]
                    pct_now = int(idx / total * 100)

                    # شريط التقدم
                    st.markdown(f"""
                    <div class='q-counter'>السؤال {idx+1} من {total}</div>
                    <div class='progress-bar-wrap'>
                        <div class='progress-bar-fill' style='width:{pct_now}%'></div>
                    </div>""", unsafe_allow_html=True)

                    # ── اختبار موقوت: حساب الوقت ──
                    if mode == "timer":
                        elapsed  = time.time() - st.session_state.timer_start
                        limit    = st.session_state.timer_seconds
                        remaining = max(0, limit - int(elapsed))
                        warn_cls = "timer-warn" if remaining <= 10 else ""
                        st.markdown(f"<div class='timer-box {warn_cls}'>⏱️ الوقت المتبقي: {remaining} ثانية</div>",
                                    unsafe_allow_html=True)
                        if remaining == 0 and not st.session_state.quiz_answered:
                            st.session_state.quiz_answered = True
                            st.session_state.quiz_show_ans = True
                            st.session_state.timer_expired = True
                            st.rerun()

                    # ── بطاقة السؤال ──
                    if mode == "listen":
                        # اختبار الاستماع: الصوت فقط بدون رؤية الكلمة
                        st.markdown(f"""
                        <div class='quiz-card'>
                            <div class='quiz-hint'>🔊 استمع جيداً واكتب ما تسمعه بالعربية</div>
                            <div style='font-size:60px;margin:20px 0;'>👂</div>
                            <div class='quiz-hint' style='color:#7c3aed;font-size:16px;'>
                                اضغط تشغيل واستمع للكلمة/الجملة
                            </div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='quiz-card'>
                            <div class='quiz-hint'>💡 ما معنى هذه الكلمة/الجملة بالعربية؟</div>
                            <div class='quiz-en'>{item['en']}</div>
                            <div class='quiz-hint' style='margin-top:12px;color:#7c3aed;font-size:20px;'>
                                النطق: {item['pron']}
                            </div>
                        </div>""", unsafe_allow_html=True)

                    # صوت الكلمة
                    render_audio(ensure_audio(item["en"], v_id, selected_speed))
                    st.markdown("<br>", unsafe_allow_html=True)

                    # ── لم يجب بعد ──
                    if not st.session_state.quiz_answered:
                        user_ans = st.text_input("✏️ اكتب الترجمة العربية:", key=f"ans_{idx}_{mode}", placeholder="اكتب اجابتك هنا...")
                        ca, cb = st.columns(2)
                        with ca:
                            if st.button("✅ تحقق", type="primary", use_container_width=True):
                                if user_ans.strip():
                                    st.session_state.quiz_answered = True
                                    st.session_state.quiz_user_ans = user_ans.strip()
                                    st.rerun()
                                else: st.warning("اكتب اجابتك اولاً!")
                        with cb:
                            if st.button("👁 اظهر الاجابة", use_container_width=True):
                                st.session_state.quiz_answered = True
                                st.session_state.quiz_show_ans = True
                                st.session_state.quiz_user_ans = ""
                                st.rerun()
                        # تحديث تلقائي للمؤقت
                        if mode == "timer" and not st.session_state.quiz_answered:
                            time.sleep(1); st.rerun()

                    # ── بعد الاجابة ──
                    else:
                        if st.session_state.timer_expired:
                            st.error("⏰ انتهى الوقت!")
                        handle_answer(item, st.session_state.quiz_user_ans, st.session_state.quiz_show_ans)
                        st.markdown("<br>", unsafe_allow_html=True)
                        next_btn(idx, total)
