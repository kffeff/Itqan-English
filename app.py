<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة إتقان اللغة الإنجليزية</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f8ff;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }

        h1 { color: #2c7be5; margin-bottom: 30px; }

        /* حاوية البطاقة */
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 500px;
            text-align: center;
            border-right: 8px solid #2c7be5;
            position: relative;
        }

        .english-text {
            font-size: 28px;
            color: #1e3a8a;
            font-weight: bold;
            margin-bottom: 15px;
        }

        .arabic-translation {
            font-size: 22px;
            color: #10b981;
            margin-bottom: 20px;
        }

        /* تعديل سطر النطق ليصبح في سطر واحد وواضح */
        .phonetic-box {
            border: 2px dashed #ef4444;
            padding: 15px;
            border-radius: 12px;
            background-color: #fff5f5;
            font-size: 26px; /* تكبير الخط */
            color: #b91c1c;
            font-weight: 900;
            white-space: nowrap; /* منع الانقسام لسطرين */
            overflow-x: auto; /* السماح بالتمرير البسيط إذا كانت الجملة طويلة جداً */
            display: block;
            width: 100%;
            box-sizing: border-box;
        }

        /* زر الصوت */
        .play-btn {
            margin-top: 20px;
            background: #2c7be5;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 18px;
            cursor: pointer;
            transition: 0.3s;
        }

        /* أيقونة الإعدادات الجانبية */
        .settings-container {
            position: absolute;
            top: 10px;
            left: 10px;
        }

        .settings-icon {
            font-size: 24px;
            color: #64748b;
            cursor: pointer;
        }

        .voice-selector {
            display: none; /* مخفية افتراضياً */
            position: absolute;
            top: 40px;
            left: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
            z-index: 100;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .voice-selector.active {
            display: block;
        }

        select {
            padding: 5px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>

    <h1>منصة إتقان اللغة الإنجليزية</h1>

    <div class="card">
        <div class="settings-container">
            <i class="fas fa-cog settings-icon" onclick="toggleVoices()"></i>
            <div id="voiceMenu" class="voice-selector">
                <label style="font-size: 12px; display: block;">اختر الصوت:</label>
                <select id="voiceSelect"></select>
            </div>
        </div>

        <div class="english-text" id="textToSpeak">The patient needs urgent care</div>
        <div class="arabic-translation">المريض يحتاج لرعاية عاجلة</div>
        
        <div class="phonetic-box">
            ذا بيشنت نيدز أورجينت كير
        </div>

        <button class="play-btn" onclick="speakText()">
            <i class="fas fa-volume-up"></i> استماع للنطق
        </button>
    </div>

    <script>
        let synth = window.speechSynthesis;
        let voiceSelect = document.querySelector('#voiceSelect');
        let voices = [];

        // حل مشكلة الآيفون: تفعيل الصوت عند أول تفاعل للمستخدم
        function unlockAudio() {
            if (synth.speaking) return;
            const utter = new SpeechSynthesisUtterance('');
            synth.speak(utter);
            console.log("Audio Unlocked for iOS");
            window.removeEventListener('touchstart', unlockAudio);
            window.removeEventListener('click', unlockAudio);
        }
        window.addEventListener('touchstart', unlockAudio);
        window.addEventListener('click', unlockAudio);

        // تحميل الأصوات المتاحة
        function loadVoices() {
            voices = synth.getVoices();
            voiceSelect.innerHTML = '';
            voices.forEach((voice, i) => {
                if (voice.lang.includes('en')) { // حصر الأصوات بالإنجليزية فقط
                    let option = document.createElement('option');
                    option.value = i;
                    option.textContent = `${voice.name} (${voice.lang})`;
                    voiceSelect.appendChild(option);
                }
            });
        }

        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = loadVoices;
        }
        loadVoices();

        // وظيفة النطق مع معالجة السرعة والوضوح
        function speakText() {
            if (synth.speaking) synth.cancel();
            
            let text = document.getElementById('textToSpeak').innerText;
            let utter = new SpeechSynthesisUtterance(text);
            
            // اختيار الصوت المحدد
            if (voices.length > 0) {
                utter.voice = voices[voiceSelect.value];
            }

            // ضبط السرعة (0.7 تجعل النطق بطيئاً وواضحاً جداً)
            utter.rate = 0.7; 
            utter.pitch = 1;
            utter.volume = 1;

            synth.speak(utter);
        }

        // إظهار وإخفاء قائمة الأصوات
        function toggleVoices() {
            document.getElementById('voiceMenu').classList.toggle('active');
        }

        // إغلاق القائمة عند النقر خارجها
        window.onclick = function(event) {
            if (!event.target.matches('.settings-icon')) {
                let menu = document.getElementById('voiceMenu');
                if (menu.classList.contains('active')) {
                    menu.classList.remove('active');
                }
            }
        }
    </script>
</body>
</html>
