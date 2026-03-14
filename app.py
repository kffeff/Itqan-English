import streamlit as st
import edge_tts
import asyncio
import hashlib
import base64
import os
import json

st.set_page_config(page_title="منصة إتقان الإنجليزية", layout="wide")

DATA_FILE = "data.json"
AUDIO_DIR = "audio_cache"

os.makedirs(AUDIO_DIR, exist_ok=True)

VOICES = {
"رجل واضح": "en-US-GuyNeural",
"امرأة واضحة": "en-US-AvaNeural",
"بريطاني": "en-GB-SoniaNeural"
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {"categories":{}}

def save_data(data):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

data = load_data()

async def generate_tts(text,voice,speed,path):
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

def get_audio(text,voice,speed):

    key = f"{text}_{voice}_{speed}"
    hash_name = hashlib.md5(key.encode()).hexdigest()

    file_path = f"{AUDIO_DIR}/{hash_name}.mp3"

    if not os.path.exists(file_path):
        run_async(generate_tts(text,voice,speed,file_path))

    with open(file_path,"rb") as f:
        audio_bytes = f.read()

    b64 = base64.b64encode(audio_bytes).decode()

    html = f"""
    <audio controls preload="auto">
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """

    return html

st.title("منصة إتقان الإنجليزية")

voice_name = st.selectbox(
"اختر الصوت",
list(VOICES.keys())
)

speed = st.slider(
"سرعة النطق",
-50,
0,
-30
)

voice_id = VOICES[voice_name]

params = st.query_params
admin = str(params.get("admin","false")).lower()=="true"

if admin:

    st.header("لوحة الإدارة")

    new_cat = st.text_input("قسم جديد")

    if st.button("إضافة قسم"):
        if new_cat not in data["categories"]:
            data["categories"][new_cat]=[]
            save_data(data)
            st.rerun()

    if data["categories"]:

        cat = st.selectbox("القسم",list(data["categories"].keys()))

        raw = st.text_area("English | Arabic | Pronunciation")

        if st.button("حفظ"):
            for line in raw.split("\n"):
                parts=[p.strip() for p in line.split("|")]

                if len(parts)==3:
                    data["categories"][cat].append({
                    "en":parts[0],
                    "ar":parts[1],
                    "pron":parts[2]
                    })

            save_data(data)
            st.rerun()

        st.subheader("المحتوى")

        for i,item in enumerate(data["categories"][cat]):

            c1,c2=st.columns([6,1])

            c1.write(item["en"]+" - "+item["ar"])

            if c2.button("حذف",key=f"del{i}"):

                data["categories"][cat].pop(i)
                save_data(data)
                st.rerun()

else:

    if data["categories"]:

        cat = st.selectbox(
        "الوحدة",
        list(data["categories"].keys())
        )

        items = data["categories"][cat]

        for item in items:

            st.markdown(
            f"""
            ### {item['en']}
            **{item['ar']}**
            {item['pron']}
            """
            )

            audio_html = get_audio(
            item["en"],
            voice_id,
            speed
            )

            st.markdown(audio_html,unsafe_allow_html=True)

            st.divider()

    else:

        st.info("لا يوجد محتوى بعد")
