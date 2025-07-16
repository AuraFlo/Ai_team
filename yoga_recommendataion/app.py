import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import os
from yoga_agent import recommend_yoga, generate_weekly_report

# Streamlit configuration
st.set_page_config(page_title="🧘 Yoga Recommender", layout="centered", page_icon="🧘‍♀️")

# ---------------------------- Cute Custom CSS (Updated for visibility) ----------------------------
st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #fffafc;
        font-family: "Comic Sans MS", cursive, sans-serif;
        color: #333333;
    }
    .main-title {
        font-size: 2.8em;
        font-weight: 700;
        text-align: center;
        color: #d63384;
        margin-bottom: 0.1em;
    }
    .sub-header {
        font-size: 1.2em;
        text-align: center;
        color: #555;
        margin-bottom: 2em;
    }
    .stButton > button {
        background-color: #d63384;
        color: white;
        font-size: 16px;
        border-radius: 12px;
        padding: 0.5em 1.5em;
    }
    .stTextArea textarea {
        border-radius: 12px;
        background-color: #050505;
    }
    .stSidebar > div:first-child {
        background-color: #ffe0f0;
        border-radius: 16px;
        padding: 1em;
        color: #000;
    }
    .stSidebar .stHeader, .stSidebar label, .stSidebar span, .stSidebar input {
        color: #333 !important;
    }
    .stRadio > div > label {
        color: #333 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------- Header ----------------------------
st.markdown("<div class='main-title'>🌸 Adaptive Yoga Recommendation</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Gentle guidance for your body & mind 🧘‍♀️</div>", unsafe_allow_html=True)

# ---------------------------- Sidebar ----------------------------
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2019/04/05/00/22/yoga-4100342_1280.png")
    st.header("🌼 User Info")
    user_id = st.number_input("User ID", min_value=1, step=1)
    input_type = st.radio("How would you like to journal today?", ["Text", "Voice"])

# ---------------------------- Journal Entry ----------------------------
st.subheader("📓 Journal Entry")
journal_text = ""
audio_path = None

if input_type == "Text":
    journal_text = st.text_area("Describe your current mood, pain, or thoughts:", height=150)
else:
    st.info("🎙️ Click to record ~5 seconds")
    if st.button("🛑 Start Voice Recording"):
        try:
            fs = 44100
            seconds = 5
            st.write("🎤 Recording...")
            audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()

            if audio is not None:
                temp_dir = tempfile.gettempdir()
                audio_path = os.path.join(temp_dir, f"user_{user_id}_recording.wav")
                write(audio_path, fs, audio)
                st.audio(audio_path)
                st.session_state.audio_path = audio_path  # ✅ SAVE PATH
                st.success("🎉 Voice recorded!")
            else:
                st.error("❌ Recording failed.")
        except Exception as e:
            st.error(f"🎤 Error: {e}")


# ---------------------------- Recommendation ----------------------------
st.subheader("🌟 Your Personalized Yoga Plan")
if st.button("🌈 Get Recommendation") and user_id:
    with st.spinner("✨ Reading your thoughts..."):
        try:
            result = None
            if input_type == "Text" and journal_text.strip():
                result = recommend_yoga(user_id, journal_text, voice=False)
            elif input_type == "Voice":
                audio_path = st.session_state.get("audio_path", None)  # ✅ retrieve saved path
                if audio_path and os.path.exists(audio_path):
                    result = recommend_yoga(user_id, audio_path, voice=True)
            else:
               st.warning("⚠️ Voice not recorded. Please try again.")


            if result:
                st.markdown("#### 💖 Recommended Poses:")
                st.markdown(result['details'])
                st.video("https://www.youtube.com/embed/v7AYKMP6rOE")
        except Exception as e:
            st.error(f"💔 Recommendation failed: {e}")

# ---------------------------- Weekly Report ----------------------------
st.subheader("📈 Your Weekly Progress")
if st.button("📊 Show Report") and user_id:
    try:
        df, mood_df, pose_count = generate_weekly_report(user_id)

        if df.empty and mood_df.empty:
            st.warning("No sessions yet — keep going! 🌱")
        else:
            st.markdown("### 🔷 Accuracy Progress")
            st.line_chart(df.rename(columns={"Date": "index"}).set_index("index"))

            st.markdown("### 🔸 Mood & Fatigue")
            st.bar_chart(mood_df.rename(columns={"Date": "index"}).set_index("index"))

            st.markdown("### 🌻 Most Practiced Poses")
            if pose_count:
                for pose, count in pose_count:
                    st.write(f"🌼 {pose}: practiced {count} times")
            else:
                st.write("Pose data coming soon 🧘")
    except Exception as e:
        st.error(f"Oops! Couldn't load report: {e}")

# ---------------------------- Footer ----------------------------
st.markdown("""
    <hr style='border: 1px solid #ffe4e1;'>
    <center style='color: #d63384;'>
        Made with 💕 for your wellbeing | © 2025 Yoga Assistant
    </center>
""", unsafe_allow_html=True)
