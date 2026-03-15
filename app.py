import streamlit as st
import streamlit.components.v1 as components
import os, asyncio, edge_tts, base64, hashlib, random, time
from supabase import create_client, Client

st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide", page_icon="🎓")

if "dark_mode" not in st.session_state: st.session_state.dark_mode = False
DK      = st.session_state.dark_mode
BG      = "#0f172a" if DK else "#f0f4ff"
CARD_BG = "#1e293b" if DK else "#ffffff"
TEXT    = "#f1f5f9" if DK else "#1e293b"
SUB     = "#94a3b8" if DK else "#64748b"
BORDER  = "#334155" if DK else "#e2e8f0"
INPUT_BG= "#334155" if DK else "#1e293b"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
#MainMenu,footer,header,.stDeployButton,[data-testid='stSidebar'],[data-testid='stSidebarCollapseButton']{{display:none!important;visibility:hidden!important;}}
.stApp{{background-color:{BG};font-family:'Cairo',sans-serif;}}
.card{{background:{CARD_BG};padding:32px 28px 24px;border-radius:22px;border-right:10px solid #2563eb;
    margin-bottom:10px;box-shadow:0 8px 32px rgba(37,99,235,0.12);text-align:center;width:100%;
    transition:transform 0.18s ease,box-shadow 0.18s ease;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 18px 48px rgba(37,99,235,0.2);}}
.en-text{{font-size:40px;font-weight:900;color:{TEXT};margin-bottom:6px;}}
.ar-text{{font-size:26px;color:#059669;font-weight:700;margin-bottom:4px;font-family:'Cairo',sans-serif;}}
.pron-box{{background:linear-gradient(135deg,#fff1f2 0%,#ffe4e6 100%);padding:14px 18px;
    border-radius:16px;border:3px dashed #f43f5e;color:#e11d48;font-size:clamp(22px,5vw,46px);
    font-weight:900;margin-top:14px;display:block;width:100%;line-height:1.4;
    font-family:'Cairo',sans-serif;word-break:break-word;overflow-wrap:break-word;}}
@media(max-width:600px){{
    .pron-box{{font-size:clamp(18px,4.5vw,28px)!important;padding:10px 12px;}}
    .en-text{{font-size:clamp(22px,6vw,32px)!important;}}
    .ar-text{{font-size:clamp(16px,4vw,22px)!important;}}
    .card{{padding:20px 16px 16px!important;}}
    .quiz-en{{font-size:clamp(22px,6vw,36px)!important;}}
}}
.quiz-card{{background:{CARD_BG};padding:40px 32px;border-radius:24px;border-top:8px solid #7c3aed;
    margin-bottom:16px;box-shadow:0 10px 40px rgba(124,58,237,0.15);text-align:center;width:100%;}}
.quiz-en{{font-size:44px;font-weight:900;color:{TEXT};margin-bottom:8px;}}
.quiz-ar{{font-size:38px;font-weight:900;color:#059669;margin-bottom:8px;font-family:'Cairo',sans-serif;}}
.quiz-hint{{font-size:18px;color:{SUB};font-family:'Cairo',sans-serif;margin-bottom:20px;}}
.quiz-correct{{background:linear-gradient(135deg,#d1fae5,#a7f3d0);border:3px solid #059669;
    border-radius:16px;padding:20px;margin-top:16px;font-size:28px;font-weight:900;
    color:#065f46;font-family:'Cairo',sans-serif;}}
.quiz-wrong{{background:linear-gradient(135deg,#fee2e2,#fecaca);border:3px solid #dc2626;
    border-radius:16px;padding:20px;margin-top:16px;font-size:22px;font-weight:700;
    color:#7f1d1d;font-family:'Cairo',sans-serif;}}
.quiz-reveal{{background:linear-gradient(135deg,#ede9fe,#ddd6fe);border:3px solid #7c3aed;
    border-radius:16px;padding:20px;margin-top:16px;font-family:'Cairo',sans-serif;}}
.quiz-score{{background:linear-gradient(135deg,#1e293b,#0f172a);border-radius:24px;padding:40px;
    text-align:center;color:white;font-family:'Cairo',sans-serif;box-shadow:0 20px 60px rgba(0,0,0,0.35);}}
.score-number{{font-size:80px;font-weight:900;color:#fbbf24;line-height:1;}}
.score-label{{font-size:24px;color:#94a3b8;margin-top:8px;}}
.score-msg{{font-size:30px;font-weight:900;margin-top:20px;}}
.q-counter{{font-size:16px;color:{SUB};font-family:'Cairo',sans-serif;text-align:left;margin-bottom:4px;}}
.progress-bar-wrap{{background:{BORDER};border-radius:99px;height:12px;width:100%;margin:12px 0;}}
.progress-bar-fill{{background:linear-gradient(90deg,#7c3aed,#2563eb);height:12px;border-radius:99px;transition:width 0.4s ease;}}
.timer-box{{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:white;border-radius:16px;
    padding:12px 24px;font-size:28px;font-weight:900;text-align:center;margin-bottom:16px;
    font-family:'Cairo',sans-serif;box-shadow:0 4px 20px rgba(124,58,237,0.4);}}
.timer-warn{{background:linear-gradient(135deg,#ef4444,#dc2626)!important;}}
.mcq-opt{{width:100%;padding:16px 20px;border-radius:14px;border:2px solid {BORDER};
    background:{CARD_BG};font-size:22px;font-weight:700;font-family:'Cairo',sans-serif;
    margin:6px 0;text-align:center;display:block;}}
.mcq-opt-correct{{background:linear-gradient(135deg,#d1fae5,#a7f3d0)!important;border-color:#059669!important;color:#065f46!important;}}
.mcq-opt-wrong{{background:linear-gradient(135deg,#fee2e2,#fecaca)!important;border-color:#dc2626!important;color:#7f1d1d!important;}}
.mcq-opt-neutral{{opacity:0.45;}}
.repeat-badge{{background:linear-gradient(135deg,#f59e0b,#d97706);color:white;
    border-radius:99px;padding:4px 14px;font-size:14px;font-weight:700;
    font-family:'Cairo',sans-serif;display:inline-block;margin-bottom:8px;}}
.platform-title{{text-align:center;color:#2563eb;font-family:'Cairo',sans-serif;font-size:42px;font-weight:900;margin-bottom:8px;}}
.platform-subtitle{{text-align:center;color:{SUB};font-family:'Cairo',sans-serif;font-size:18px;margin-bottom:30px;}}
.settings-box{{background:{CARD_BG};border-radius:16px;padding:20px 24px;border:2px solid {BORDER};margin-bottom:20px;}}
.login-box{{background:{CARD_BG};border-radius:24px;padding:48px 40px;max-width:420px;
    margin:60px auto;box-shadow:0 20px 60px rgba(37,99,235,0.15);border-top:8px solid #2563eb;text-align:center;}}
hr{{border:none;border-top:2px solid {BORDER};margin:4px 0 20px;}}
label,.stTextInput label,.stTextArea label,.stSelectbox label,.stSlider label,
.stTabs [data-baseweb="tab"],h1,h2,h3,h4,p,div[data-testid="stText"],.stMarkdown p,
.stAlert p,.stInfo p{{color:{TEXT}!important;font-weight:600;}}
.stTabs [data-baseweb="tab"][aria-selected="true"]{{color:#2563eb!important;}}
button, button *, button p, button span, button div,
.stButton button, .stButton button * {{color:#ffffff!important;font-family:'Cairo',sans-serif!important;font-weight:700!important;}}
.stButton>button{{background:#1e293b!important;border:2px solid #334155!important;border-radius:10px!important;}}
.stButton>button:hover{{background:#2d3f55!important;border-color:#2563eb!important;}}
.stTextInput input,.stTextArea textarea{{background-color:{INPUT_BG}!important;color:#ffffff!important;
    border:2px solid #2563eb!important;border-radius:10px!important;font-family:'Cairo',sans-serif!important;}}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{{color:#94a3b8!important;}}
div[data-baseweb="select"]>div{{background-color:{INPUT_BG}!important;border:2px solid #2563eb!important;border-radius:10px!important;}}
div[data-baseweb="select"] span,div[data-baseweb="select"] div{{color:#ffffff!important;}}
ul[data-baseweb="menu"]{{background-color:{INPUT_BG}!important;}}
ul[data-baseweb="menu"] li{{color:#ffffff!important;}}
ul[data-baseweb="menu"] li:hover{{background-color:#2563eb!important;}}
</style>""", unsafe_allow_html=True)

SUPABASE_URL = "https://iwpccslbxlbaargqpgeg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3cGNjc2xieGxiYWFyZ3FwZ2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1MTc1MjcsImV4cCI6MjA4OTA5MzUyN30.9Lt0qCuVb6qu5KoSafSUCqN1Hb6P89EPO72grxSjqkg"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = get_supabase()

def get_categories():
    res = supabase.table("categories").select("*").order("name").execute()
    return res.data or []
def get_words(category_id):
    res = supabase.table("words").select("*").eq("category_id", category_id).execute()
    return res.data or []
def add_category(name):
    supabase.table("categories").insert({"name": name}).execute()
def delete_category(cat_id):
    supabase.table("categories").delete().eq("id", cat_id).execute()
def add_word(category_id, en, ar, pron):
    supabase.table("words").insert({"category_id": category_id, "en": en, "ar": ar, "pron": pron}).execute()
def delete_word(word_id):
    supabase.table("words").delete().eq("id", word_id).execute()

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

async def _gen(text, path, voice, rate):
    await edge_tts.Communicate(text, voice, rate=rate).save(path)
def generate_voice(text, filename, voice, rate):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed(): raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    loop.run_until_complete(_gen(text, os.path.join(AUDIO_DIR, filename), voice, rate))
def render_audio(fp):
    with open(fp, "rb") as f: b64 = base64.b64encode(f.read()).decode()
    components.html("<html><body style='margin:0;padding:4px 0 0 0;background:transparent;'>"
        "<audio controls preload='auto' style='width:100%;height:48px;border-radius:12px;display:block;'>"
        "<source src='data:audio/mpeg;base64," + b64 + "' type='audio/mpeg'></audio></body></html>", height=64)
def ensure_audio(text, v_id, speed):
    fhash = hashlib.md5(f"{text}|{v_id}|{speed}".encode()).hexdigest()
    fname = f"audio_{fhash}.mp3"; fpath = os.path.join(AUDIO_DIR, fname)
    if not os.path.exists(fpath):
        with st.spinner("جار توليد الصوت..."): generate_voice(text, fname, v_id, f"{speed:+d}%")
    return fpath
def normalize(s):
    return s.strip().replace("،","").replace(",","").replace(".","").replace(" ","").lower()
def make_mcq_choices(items, correct_item):
    wrong = [it for it in items if it["en"] != correct_item["en"]]
    chosen = random.sample(wrong, min(3, len(wrong)))
    choices = [correct_item["ar"]] + [c["ar"] for c in chosen]
    random.shuffle(choices)
    return choices

DEFAULTS = {
    "quiz_active":False,"quiz_mode":"normal","quiz_items":[],"quiz_idx":0,"quiz_score":0,
    "quiz_answered":False,"quiz_user_ans":"","quiz_show_ans":False,"quiz_results":[],
    "timer_start":0,"timer_expired":False,"mcq_choices":[],"mcq_selected":None,
    "smart_wrong":[],"smart_round":1,"admin_auth":False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

is_admin = st.query_params.get("admin") == "true"

@st.cache_data(ttl=30)
def cached_categories():
    return get_categories()
categories = cached_categories()
cat_names  = [c["name"] for c in categories]
cat_map    = {c["name"]: c["id"] for c in categories}

# ══ Header ══
st.markdown("<div class='platform-title'>🎓 منصة اتقان اللغة الانجليزية</div>"
            "<div class='platform-subtitle'>تعلم الكلمات والجمل بنطق صحيح واضح</div>",
            unsafe_allow_html=True)

# ══ ADMIN ══
if is_admin:
    # ── كلمة السر ──
    if not st.session_state.admin_auth:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("### 🔐 لوحة الادارة")
        st.markdown("أدخل كلمة السر للدخول")
        pwd = st.text_input("كلمة السر:", type="password", placeholder="••••••••")
        if st.button("🔓 دخول", type="primary", use_container_width=True):
            if pwd == "11223344":
                st.session_state.admin_auth = True; st.rerun()
            else:
                st.error("❌ كلمة السر خاطئة!")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # ── لوحة الادارة الكاملة ──
    col_title, col_logout = st.columns([8, 1])
    with col_title:
        st.title("🛠 لوحة الادارة الكاملة")
    with col_logout:
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.admin_auth = False; st.rerun()

    tab1, tab2, tab3 = st.tabs(["➕ اضافة محتوى", "🗑 ادارة وحذف", "🔁 حذف المكرر"])
    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("💾 حفظ القسم الجديد") and new_c.strip():
            if new_c.strip() not in cat_names:
                add_category(new_c.strip()); st.cache_data.clear()
                st.success(f"تم انشاء القسم: {new_c.strip()}"); st.rerun()
            else: st.warning("هذا القسم موجود بالفعل.")
        if categories:
            st.divider()
            target_name = st.selectbox("اضافة الى قسم:", cat_names, key="add_cat")
            raw = st.text_area("الكلمة/الجملة | الترجمة | النطق  (سطر جديد لكل ادخال)",
                placeholder="Hello | مرحبا | هلو\nGoodbye | وداعا | غود-باي", height=160)
            if st.button("🚀 حفظ الادخالات") and raw.strip():
                added = 0
                for line in raw.strip().split("\n"):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) == 3 and all(parts):
                        add_word(cat_map[target_name], parts[0], parts[1], parts[2]); added += 1
                if added: st.cache_data.clear(); st.success(f"تم حفظ {added} ادخال!"); st.rerun()
                else: st.error("تاكد من الصيغة: كلمة | ترجمة | نطق")
    with tab2:
        if categories:
            st.subheader("حذف قسم كامل")
            cat_to_del = st.selectbox("اختر القسم:", cat_names, key="del_cat")
            if st.button("🔥 حذف القسم نهائيا"):
                delete_category(cat_map[cat_to_del]); st.cache_data.clear(); st.rerun()
            st.divider()
            st.subheader("حذف جملة/كلمة من قسم")
            cat_manage = st.selectbox("اختر القسم:", cat_names, key="manage_cat")
            items_m = get_words(cat_map[cat_manage])
            if items_m:
                for item in items_m:
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"**{item['en']}** — {item['ar']}  |  *{item['pron']}*")
                    if c2.button("🗑", key=f"del_w_{item['id']}"):
                        delete_word(item["id"]); st.cache_data.clear(); st.rerun()
            else: st.info("هذا القسم فارغ.")
        else: st.info("لا توجد اقسام بعد.")

    with tab3:
        st.subheader("🔁 كشف وحذف الجمل المكررة")
        if categories:
            cat_dup = st.selectbox("اختر القسم للفحص:", ["📂 كل الأقسام"] + cat_names, key="dup_cat")
            if st.button("🔍 فحص المكررات", type="primary", use_container_width=True):
                all_dups = []
                cats_to_check = categories if cat_dup == "📂 كل الأقسام" else [c for c in categories if c["name"] == cat_dup]
                for cat in cats_to_check:
                    words = get_words(cat["id"])
                    seen = {}
                    for w in words:
                        key = w["en"].strip().lower()
                        if key in seen:
                            all_dups.append({"item": w, "cat": cat["name"]})
                        else:
                            seen[key] = w
                st.session_state["dups"] = all_dups

            if "dups" in st.session_state:
                dups = st.session_state["dups"]
                if not dups:
                    st.success("✅ لا توجد جمل مكررة!")
                else:
                    st.warning(f"⚠️ وجدنا {len(dups)} جملة مكررة:")
                    st.divider()
                    for d in dups:
                        c1, c2 = st.columns([5, 1])
                        c1.write(f"**{d['item']['en']}** — {d['item']['ar']} | قسم: *{d['cat']}*")
                        if c2.button("🗑", key=f"del_dup_{d['item']['id']}"):
                            delete_word(d["item"]["id"])
                            st.cache_data.clear()
                            st.session_state["dups"] = [x for x in dups if x["item"]["id"] != d["item"]["id"]]
                            st.rerun()
                    st.divider()
                    if st.button("🔥 حذف كل المكررات دفعة واحدة", type="primary", use_container_width=True):
                        for d in dups:
                            delete_word(d["item"]["id"])
                        st.cache_data.clear()
                        del st.session_state["dups"]
                        st.success("✅ تم حذف جميع المكررات!"); st.rerun()
        else:
            st.info("لا توجد اقسام بعد.")

# ══ STUDENT VIEW ══
else:
    if not categories:
        st.info("مرحبا بك! يرجى اضافة اقسام من لوحة الادارة اولا.")
    else:
        choice = st.selectbox("📂 اختر القسم الذي يناسبك:", cat_names)

        with st.expander("⚙️ الإعدادات", expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                selected_voice_key = st.selectbox("🎙️ اختر المعلم:", list(VOICES.keys()), key="v_sel")
            with col2:
                search_q = st.text_input("🔍 بحث سريع:", key="search_q")
            with col3:
                selected_speed = st.slider("⚡ سرعة النطق:", -50, 0, -30, 5, key="s_sel")
                if st.button("🌙" if not DK else "☀️", use_container_width=True):
                    st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()

        @st.cache_data(ttl=60)
        def cached_words(cat_id):
            return get_words(cat_id)
        items = cached_words(cat_map[choice])

        if "search_q" in st.session_state and st.session_state.search_q:
            q = st.session_state.search_q.lower()
            items = [it for it in items if q in it["en"].lower() or q in it["ar"] or q in it["pron"]]

        if not items:
            st.warning("لا توجد نتائج.")
        else:
            v_id = VOICES[selected_voice_key]
            st.markdown("**اختر وضع التعلم:**")
            r1c1,r1c2,r1c3,r1c4 = st.columns(4)
            r2c1,r2c2,r2c3,_    = st.columns(4)

            def start_quiz(mode):
                shuffled = items.copy(); random.shuffle(shuffled)
                st.session_state.update({
                    "quiz_active":True,"quiz_mode":mode,"quiz_items":shuffled,
                    "quiz_idx":0,"quiz_score":0,"quiz_answered":False,
                    "quiz_user_ans":"","quiz_show_ans":False,"quiz_results":[],
                    "mcq_choices":[],"mcq_selected":None,"smart_wrong":[],"smart_round":1,
                    "timer_start":time.time(),"timer_expired":False,
                }); st.rerun()

            def mode_btn(col, label, mode_name):
                active = st.session_state.quiz_active and st.session_state.quiz_mode==mode_name
                with col:
                    return st.button(label, use_container_width=True, type="primary" if active else "secondary")

            if r1c1.button("📖 دراسة", use_container_width=True,
                           type="primary" if not st.session_state.quiz_active else "secondary"):
                st.session_state.quiz_active = False; st.rerun()
            if mode_btn(r1c2,"📝 اختبار","normal"): start_quiz("normal")
            if mode_btn(r1c3,"🔊 استماع","listen"): start_quiz("listen")
            if mode_btn(r1c4,"⏱️ مؤقت","timer"): start_quiz("timer")
            if mode_btn(r2c1,"🎯 اختيار متعدد","mcq"): start_quiz("mcq")
            if mode_btn(r2c2,"🔤 اختبار عكسي","reverse"): start_quiz("reverse")
            if mode_btn(r2c3,"🔁 تكرار ذكي","smart"): start_quiz("smart")

            st.markdown("<hr>", unsafe_allow_html=True)

            if not st.session_state.quiz_active:
                if st.button("🖨️ طباعة القسم كـ PDF", use_container_width=False):
                    cards_html = "".join(
                        f"<div class='print-card'><div class='print-en'>{it['en']}</div>"
                        f"<div class='print-ar'>{it['ar']}</div><div class='print-pron'>{it['pron']}</div></div>"
                        for it in items)
                    pdf_html = f"""<html dir='rtl'><head><meta charset='utf-8'><style>
                    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
                    body{{font-family:'Cairo',sans-serif;padding:20px;direction:rtl;}}
                    h1{{text-align:center;color:#2563eb;font-size:28px;margin-bottom:8px;}}
                    h2{{text-align:center;color:#64748b;font-size:16px;margin-bottom:24px;font-weight:400;}}
                    .print-card{{border:2px solid #2563eb;border-radius:12px;padding:20px;margin-bottom:16px;page-break-inside:avoid;text-align:center;}}
                    .print-en{{font-size:28px;font-weight:900;color:#1e293b;}}
                    .print-ar{{font-size:20px;color:#059669;font-weight:700;margin-top:6px;}}
                    .print-pron{{font-size:22px;color:#e11d48;font-weight:900;border:2px dashed #f43f5e;border-radius:8px;padding:8px;margin-top:10px;}}
                    @media print{{@page{{margin:15mm;}}}}
                    </style></head><body>
                    <h1>🎓 منصة اتقان اللغة الانجليزية</h1>
                    <h2>قسم: {choice} — عدد الكلمات: {len(items)}</h2>
                    {cards_html}
                    <script>window.onload=function(){{window.print();}}</script>
                    </body></html>"""
                    b64p = base64.b64encode(pdf_html.encode("utf-8")).decode()
                    components.html(
                        f'<iframe src="data:text/html;base64,{b64p}" style="display:none" id="pf"></iframe>'
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
            else:
                mode = st.session_state.quiz_mode
                if mode == "smart":
                    quiz_items = st.session_state.quiz_items if st.session_state.smart_round==1 else st.session_state.smart_wrong
                    if not quiz_items and st.session_state.smart_round > 1:
                        st.balloons()
                        st.success(f"🏆 أحسنت! أتقنت جميع الكلمات بعد {st.session_state.smart_round-1} جولة!")
                        if st.button("🔄 ابدأ من جديد", type="primary", use_container_width=True): start_quiz("smart")
                        st.stop()
                else:
                    quiz_items = st.session_state.quiz_items

                idx   = st.session_state.quiz_idx
                total = len(quiz_items)

                def show_results():
                    score = st.session_state.quiz_score
                    pct   = int(score/total*100) if total else 0
                    msg, color = (
                        ("🏆 ممتاز! كل الاجابات صحيحة!","#10b981") if pct==100 else
                        ("👍 جيد جداً! استمر","#f59e0b") if pct>=70 else
                        ("💪 راجع الكلمات وحاول مجدداً","#ef4444"))
                    st.markdown(f"""<div class='quiz-score'>
                        <div style='font-size:32px;font-weight:900;margin-bottom:16px;'>نتيجة الاختبار</div>
                        <div class='score-number'>{score}/{total}</div>
                        <div class='score-label'>اجبت صحيح على {score} من {total}</div>
                        <div class='score-msg' style='color:{color}'>{msg}</div>
                        <div style='margin-top:24px;background:#1e293b;border-radius:99px;height:16px;'>
                        <div style='background:linear-gradient(90deg,#7c3aed,#2563eb);height:16px;border-radius:99px;width:{pct}%;'></div></div>
                        <div style='color:#94a3b8;margin-top:8px;font-size:20px;'>{pct}%</div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.expander("📋 مراجعة اجاباتك"):
                        for r in st.session_state.quiz_results:
                            st.markdown(f"{'✅' if r['correct'] else '❌'} **{r['en']}**  \nاجابتك: *{r['user']}*  \nالصحيحة: *{r['ar']}*")
                            st.divider()
                    if mode=="smart" and st.session_state.smart_wrong:
                        wc = len(st.session_state.smart_wrong)
                        st.warning(f"🔁 يوجد {wc} كلمة خاطئة — سيتم تكرارها")
                        if st.button(f"▶️ ابدأ جولة التكرار ({wc} كلمة)", type="primary", use_container_width=True):
                            nw = st.session_state.smart_wrong.copy(); random.shuffle(nw)
                            st.session_state.update({"quiz_items":nw,"quiz_idx":0,"quiz_score":0,
                                "quiz_answered":False,"quiz_user_ans":"","quiz_show_ans":False,
                                "quiz_results":[],"smart_wrong":[],"smart_round":st.session_state.smart_round+1,
                                "mcq_choices":[],"mcq_selected":None}); st.rerun()
                    else:
                        if st.button("🔄 اعادة الاختبار", type="primary", use_container_width=True): start_quiz(mode)

                if idx >= total:
                    show_results(); st.stop()

                item    = quiz_items[idx]
                pct_now = int(idx/total*100)
                round_label = f" — الجولة {st.session_state.smart_round}" if mode=="smart" else ""

                st.markdown(f"""<div class='q-counter'>السؤال {idx+1} من {total}{round_label}</div>
                <div class='progress-bar-wrap'><div class='progress-bar-fill' style='width:{pct_now}%'></div></div>""",
                unsafe_allow_html=True)

                if mode=="timer" and not st.session_state.quiz_answered:
                    remaining = max(0, 30-int(time.time()-st.session_state.timer_start))
                    warn = "timer-warn" if remaining<=10 else ""
                    st.markdown(f"<div class='timer-box {warn}'>⏱️ {remaining} ثانية</div>", unsafe_allow_html=True)
                    if remaining==0:
                        st.session_state.quiz_answered=True; st.session_state.quiz_show_ans=True
                        st.session_state.timer_expired=True; st.rerun()

                if mode=="listen":
                    st.markdown(f"<div class='quiz-card'><div class='quiz-hint'>🔊 استمع واكتب الترجمة العربية</div>"
                        f"<div style='font-size:60px;margin:20px 0;'>👂</div>"
                        f"<div class='quiz-hint' style='color:#7c3aed;'>اضغط تشغيل واستمع</div></div>", unsafe_allow_html=True)
                elif mode=="reverse":
                    st.markdown(f"<div class='quiz-card'><div class='quiz-hint'>🔤 اكتب هذه الكلمة/الجملة بالإنجليزية</div>"
                        f"<div class='quiz-ar'>{item['ar']}</div>"
                        f"<div class='quiz-hint' style='color:#7c3aed;font-size:20px;'>النطق: {item['pron']}</div></div>", unsafe_allow_html=True)
                elif mode=="mcq":
                    st.markdown(f"<div class='quiz-card'><div class='quiz-hint'>🎯 اختر الترجمة الصحيحة</div>"
                        f"<div class='quiz-en'>{item['en']}</div>"
                        f"<div class='quiz-hint' style='color:#7c3aed;font-size:20px;'>النطق: {item['pron']}</div></div>", unsafe_allow_html=True)
                elif mode=="smart":
                    st.markdown(f"<div class='repeat-badge'>🔁 تكرار ذكي — الجولة {st.session_state.smart_round}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='quiz-card'><div class='quiz-hint'>💡 ما معنى هذه الكلمة/الجملة بالعربية؟</div>"
                        f"<div class='quiz-en'>{item['en']}</div>"
                        f"<div class='quiz-hint' style='color:#7c3aed;font-size:20px;'>النطق: {item['pron']}</div></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='quiz-card'><div class='quiz-hint'>💡 ما معنى هذه الكلمة/الجملة بالعربية؟</div>"
                        f"<div class='quiz-en'>{item['en']}</div>"
                        f"<div class='quiz-hint' style='color:#7c3aed;font-size:20px;'>النطق: {item['pron']}</div></div>", unsafe_allow_html=True)

                render_audio(ensure_audio(item["en"], v_id, selected_speed))
                st.markdown("<br>", unsafe_allow_html=True)

                if mode=="mcq":
                    if not st.session_state.mcq_choices:
                        st.session_state.mcq_choices = make_mcq_choices(items, item)
                    choices    = st.session_state.mcq_choices
                    correct_ar = item["ar"]
                    if not st.session_state.quiz_answered:
                        for i, ch in enumerate(choices):
                            if st.button(ch, key=f"mcq_{idx}_{i}", use_container_width=True):
                                st.session_state.quiz_answered=True; st.session_state.mcq_selected=ch; st.rerun()
                    else:
                        selected   = st.session_state.mcq_selected
                        is_correct = selected and normalize(selected)==normalize(correct_ar)
                        for ch in choices:
                            if normalize(ch)==normalize(correct_ar):
                                st.markdown(f"<div class='mcq-opt mcq-opt-correct'>✅ {ch}</div>", unsafe_allow_html=True)
                            elif ch==selected and not is_correct:
                                st.markdown(f"<div class='mcq-opt mcq-opt-wrong'>❌ {ch}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='mcq-opt mcq-opt-neutral'>{ch}</div>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        if is_correct: st.session_state.quiz_score+=1; st.success("🎉 اجابة صحيحة!")
                        else: st.error(f"الصحيحة: {correct_ar}")
                        if mode=="smart" and not is_correct: st.session_state.smart_wrong.append(item)
                        st.session_state.quiz_results.append({"en":item["en"],"ar":correct_ar,"user":selected or "—","correct":bool(is_correct)})
                        st.markdown("<br>", unsafe_allow_html=True)
                        lbl = "➡️ التالي" if idx+1<total else "🏁 النتيجة"
                        if st.button(lbl, type="primary", use_container_width=True):
                            st.session_state.update({"quiz_idx":idx+1,"quiz_answered":False,
                                "mcq_choices":[],"mcq_selected":None,
                                "timer_start":time.time(),"timer_expired":False}); st.rerun()
                else:
                    if not st.session_state.quiz_answered:
                        ph  = "اكتب الكلمة/الجملة بالإنجليزية..." if mode=="reverse" else "اكتب اجابتك هنا..."
                        lbl = "✏️ اكتب الكلمة/الجملة بالإنجليزية:" if mode=="reverse" else "✏️ اكتب الترجمة العربية:"
                        user_ans = st.text_input(lbl, key=f"ans_{idx}_{mode}", placeholder=ph)
                        ca, cb = st.columns(2)
                        with ca:
                            if st.button("✅ تحقق", type="primary", use_container_width=True):
                                if user_ans.strip():
                                    st.session_state.quiz_answered=True; st.session_state.quiz_user_ans=user_ans.strip(); st.rerun()
                                else: st.warning("اكتب اجابتك اولاً!")
                        with cb:
                            if st.button("👁 اظهر الاجابة", use_container_width=True):
                                st.session_state.quiz_answered=True; st.session_state.quiz_show_ans=True
                                st.session_state.quiz_user_ans=""; st.rerun()
                        if mode=="timer": time.sleep(1); st.rerun()
                    else:
                        correct    = item["en"] if mode=="reverse" else item["ar"]
                        user_ans   = st.session_state.quiz_user_ans
                        show_only  = st.session_state.quiz_show_ans
                        if st.session_state.timer_expired: st.error("⏰ انتهى الوقت!")
                        if show_only:
                            st.markdown(f"<div class='quiz-reveal'>"
                                f"<div style='font-size:20px;color:#5b21b6;font-weight:700;margin-bottom:8px;'>الاجابة الصحيحة:</div>"
                                f"<div style='font-size:32px;font-weight:900;color:#4c1d95;'>{correct}</div>"
                                f"<div style='font-size:18px;color:#6d28d9;margin-top:8px;'>النطق: {item['pron']}</div></div>", unsafe_allow_html=True)
                            st.session_state.quiz_results.append({"en":item["en"],"ar":item["ar"],"user":"—","correct":False})
                            if mode=="smart": st.session_state.smart_wrong.append(item)
                        else:
                            is_correct = normalize(user_ans)==normalize(correct)
                            if is_correct:
                                st.session_state.quiz_score+=1
                                st.markdown(f"<div class='quiz-correct'>✅ اجابة صحيحة! 🎉<br><span style='font-size:24px;'>{correct}</span></div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='quiz-wrong'>❌ اجابة خاطئة<br>"
                                    f"<span style='font-size:18px;'>اجابتك: {user_ans}</span><br>"
                                    f"<span style='font-size:22px;color:#991b1b;'>✔ الصحيحة: {correct}</span><br>"
                                    f"<span style='font-size:18px;color:#7f1d1d;'>النطق: {item['pron']}</span></div>", unsafe_allow_html=True)
                                if mode=="smart": st.session_state.smart_wrong.append(item)
                            st.session_state.quiz_results.append({"en":item["en"],"ar":item["ar"],"user":user_ans,"correct":is_correct})
                        st.markdown("<br>", unsafe_allow_html=True)
                        lbl = "➡️ التالي" if idx+1<total else "🏁 النتيجة"
                        if st.button(lbl, type="primary", use_container_width=True):
                            st.session_state.update({"quiz_idx":idx+1,"quiz_answered":False,
                                "quiz_user_ans":"","quiz_show_ans":False,
                                "timer_start":time.time(),"timer_expired":False}); st.rerun()
