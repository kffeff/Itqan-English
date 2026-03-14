# --- 4. لوحة الإدارة ---
if is_admin:
    st.markdown("<h1 style='text-align:center;'>🛠 لوحة التحكم بالإدارة</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["➕ إضافة محتوى", "🗑 إدارة الأقسام"])
    
    with tab1:
        new_c = st.text_input("اسم القسم الجديد:")
        if st.button("حفظ القسم"):
            if new_c and new_c not in data["categories"]:
                data["categories"][new_c] = []
                save_data(data); st.rerun()
        st.divider()
        if categories:
            target = st.selectbox("إضافة جمل إلى:", categories)
            raw = st.text_area("أدخل الجمل (الإنجليزية | العربية | النطق بالعربي):")
            if st.button("🚀 حفظ الجمل"):
                lines = raw.strip().split('\n')
                for line in lines:
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) == 3:
                            data["categories"][target].append({"en": parts[0], "ar": parts[1], "pron": parts[2]})
                save_data(data); st.success("تم التحديث!"); st.rerun()

    with tab2:
        if categories:
            cat_del = st.selectbox("اختر قسماً لحذفه:", categories)
            if st.button("🔥 حذف القسم نهائياً"):
                del data["categories"][cat_del]
                save_data(data); st.rerun()

# --- 5. واجهة الطلاب (المحسنة للآيفون) ---
else:
    st.markdown("<h1 style='text-align: center; color: #007bff;'>منصة إتقان اللغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    if categories:
        choice = st.selectbox("اختر الوحدة الدراسية:", categories)
        items = data["categories"][choice]
        if search_q: items = [i for i in items if search_q.lower() in i['en'].lower()]

        if app_mode == "📚 مكتبة الجمل":
            for idx, item in enumerate(items):
                st.markdown(f"""
                <div class="card">
                    <div class="en-text">{item['en']}</div>
                    <div class="ar-text">{item['ar']}</div>
                    <div class="pron-text">{item['pron']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # توليد الصوت ومعالجة سرعته
                v_id = VOICES[user_voice].split('-')[2]
                f_name = f"v2_{item['en'][:10].replace(' ','_').lower()}_{v_id}_{user_speed}.mp3"
                f_path = os.path.join(AUDIO_DIR, f_name)
                
                if not os.path.exists(f_path):
                    asyncio.run(generate_voice(item['en'], f_name, user_voice, user_speed))
                
                # عرض مشغل الصوت بطريقة متوافقة مع الآيفون
                with open(f_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
                
                st.divider()
        
        else: # نمط الاختبار
            st.subheader("🧠 استمع وحاول التذكر")
            if items:
                if 'q_idx' not in st.session_state: st.session_state.q_idx = random.randint(0, len(items)-1)
                q = items[st.session_state.q_idx]
                
                f_name = f"quiz_{st.session_state.q_idx}_{user_speed}.mp3"
                if not os.path.exists(os.path.join(AUDIO_DIR, f_name)):
                    asyncio.run(generate_voice(q['en'], f_name, user_voice, user_speed))
                
                st.audio(os.path.join(AUDIO_DIR, f_name))
                if st.button("👁 كشف الإجابة"):
                    st.info(f"الترجمة: {q['ar']}")
                    st.success(f"النطق: {q['pron']}")
                    if st.button("🔄 جملة تالية"):
                        del st.session_state.q_idx
                        st.rerun()
    else:
        st.warning("يرجى إضافة محتوى من لوحة الإدارة أولاً.")
