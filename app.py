import streamlit as st
import os
import json
import asyncio
import hashlib
import base64
import edge_tts

# =========================
# إعدادات أساسية
# =========================
st.set_page_config(page_title="منصة إتقان اللغة الإنجليزية", layout="wide")

DB_FILE = "data.json"
AUDIO_DIR = "audio_cache"

os.makedirs(AUDIO_DIR, exist_ok=True)

VOICES = {
    "🎙️ صوت رجالي واضح": "en-US-GuyNeural",
    "🎙️ صوت نسائي واضح": "en-US-AvaNeural",
    "🎙️ صوت بريطاني": "en-GB-SoniaNeural"
}

# =========================
# تصميم الواجهة
# =========================
st.markdown("""
<style>

#MainMenu, footer, header {visibility:hidden;}

.card{
background:white;
padding:30px;
border-radius:25px;
border-right:12px solid #007bff;
margin-bottom:25px;
box-shadow:0 10px 30px rgba(0,0,0,0.07);
text-align:center;
}

.en{
font-size:40px;
font-weight:900;
color:#1e293b;
}

.ar{
font-size:26px;
color:#059669;
font-weight:700;
margin-top:5px;
}

.pron{
margin-top:20px;
font-size:45px;
font-weight:900;
color:#e11d48;
background:#fff1f2;
padding:18px;
border-radius:16px;
border:3px dashed #f43f5e;
}

audio{
width:100%;
margin-top:20px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# قاعدة البيانات
# =========================
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {"categories":{}}

def save_data(data):
    with open(DB_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

data = load_data()

# =========================
# توليد الصوت
# =========================
async def tts_generate(text, voice, speed, path):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=f"{speed}%"
    )
    await communicate.save(path)

def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(coro)
        loop.close()
        return result

def generate_audio(text, voice, speed):

    unique_string = f"{text}_{voice}_{speed}"
    file_hash = hashlib.md5(unique_string.encode()).hexdigest()

    filename = f"{file_hash}.mp3"
    path = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(path):
        run_async(tts_generate(text, voice, speed, path))

    with open(path,"rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()

    audio_id = hashlib.md5((file_hash+"audio").encode()).hexdigest()

    html = f"""
    <audio id="{audio_id}" controls preload="auto">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """

    return html

# =========================
# إعدادات المستخدم
# =========================
with st.popover("⚙️"):

    voice_name = st.selectbox("اختر الصوت", list(VOICES.keys()))
    speed = st.slider("سرعة النطق", -50, 0, -30)

    st.divider()

    search = st.text_input("بحث")

voice_id = VOICES[voice_name]

# =========================
# العنوان
# =========================
st.markdown("<h1 style='text-align:center;color:#007bff'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)

# =========================
# تحديد وضع الإدارة
# =========================
params = st.query_params
is_admin = str(params.get("admin","false")).lower() == "true"

# =========================
# لوحة الإدارة
# =========================
if is_admin:

    st.title("لوحة الإدارة")

    tab1,tab2 = st.tabs(["إضافة محتوى","إدارة"])

    with tab1:

        new_cat = st.text_input("اسم القسم")

        if st.button("إضافة قسم"):

            if new_cat.strip():

                if new_cat not in data["categories"]:
                    data["categories"][new_cat] = []
                    save_data(data)
                    st.rerun()

        if data["categories"]:

            target = st.selectbox("القسم", list(data["categories"].keys()))

            raw = st.text_area("جملة | ترجمة | نطق")

            if st.button("حفظ الجمل"):

                for line in raw.split("\n"):

                    parts = [x.strip() for x in line.split("|")]

                    if len(parts) == 3 and parts[0]:

                        data["categories"][target].append({
                            "en":parts[0],
                            "ar":parts[1],
                            "pron":parts[2]
                        })

                save_data(data)
                st.rerun()

    with tab2:

        if data["categories"]:

            cat = st.selectbox("اختر القسم", list(data["categories"].keys()))

            if st.button("حذف القسم"):

                del data["categories"][cat]
                save_data(data)
                st.rerun()

            st.divider()

            for i,item in enumerate(list(data["categories"][cat])):

                c1,c2 = st.columns([5,1])

                c1.write(item["en"]+" - "+item["ar"])

                if c2.button("حذف",key=f"del_{cat}_{i}"):

                    data["categories"][cat].pop(i)
                    save_data(data)
                    st.rerun()

# =========================
# واجهة الطالب
# =========================
else:

    if data["categories"]:

        cat = st.selectbox("الوحدة الدراسية", list(data["categories"].keys()))

        items = data["categories"][cat]

        if search:
            items = [i for i in items if search.lower() in i["en"].lower()]

        for item in items:

            st.markdown(f"""
            <div class='card'>
            <div class='en'>{item['en']}</div>
            <div class='ar'>{item['ar']}</div>
            <div class='pron'>{item['pron']}</div>
            </div>
            """, unsafe_allow_html=True)

            audio_html = generate_audio(item["en"], voice_id, speed)

            st.markdown(audio_html, unsafe_allow_html=True)

            st.divider()

    else:

        st.info("لا توجد وحدات دراسية بعد. استخدم لوحة الإدارة.")
