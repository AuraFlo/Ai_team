import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import os
from yoga_agent import recommend_yoga, generate_weekly_report

import cv2
import numpy as np
import tensorflow as tf
from movenet.movemodel import MoveNet  # Updated class name
from movenet.angl import calculate_angle

from movenet.movemodel import MoveNet
import sys
sys.path.append("AuraFlo_Lite/AuraFlo_Lite/src")
from session_logger import save_session_log

def load_pose_model():
    return MoveNet("movenet/movenet_lightning.tflite")  # Adjust path if needed

# Wrapper class to match our GUI usage
class MovenetModel:
    def init(self, model_path):
        self.model = MoveNet(model_path)

    def detect_pose(self, frame):
        return self.model.detect(frame)

# MoveNet keypoint indices
KEYPOINT_IDX = {
    "left_hip": 11, "left_knee": 13, "left_ankle": 15,
    "right_hip": 12, "right_knee": 14, "right_ankle": 16,
    "left_shoulder": 5, "right_shoulder": 6,
    "left_elbow": 7, "right_elbow": 8
}

# Extract angles for pose evaluation
def calculate_angles(keypoints):
    angle_dict = {}
    try:
        def get_point(name):
            return keypoints[KEYPOINT_IDX[name]][:2][::-1]  # (y, x) → (x, y)

        angle_dict["left_knee"] = calculate_angle(
            get_point("left_hip"), get_point("left_knee"), get_point("left_ankle")
        )
        angle_dict["right_knee"] = calculate_angle(
            get_point("right_hip"), get_point("right_knee"), get_point("right_ankle")
        )
        angle_dict["left_hip"] = calculate_angle(
            get_point("left_shoulder"), get_point("left_hip"), get_point("left_knee")
        )
        angle_dict["right_hip"] = calculate_angle(
            get_point("right_shoulder"), get_point("right_hip"), get_point("right_knee")
        )
        angle_dict["left_shoulder"] = calculate_angle(
            get_point("left_elbow"), get_point("left_shoulder"), get_point("left_hip")
        )
        angle_dict["right_shoulder"] = calculate_angle(
            get_point("right_elbow"), get_point("right_shoulder"), get_point("right_hip")
        )
    except Exception as e:
        pass  # skip if keypoints are missing or invalid
    return angle_dict

# Pose reference angles
POSE_REFERENCES = {
    "Tree Pose": {
        "left_knee": 90,
        "right_knee": 180,
        "left_hip": 180,
        "right_hip": 90,
        "left_shoulder": 180,
        "right_shoulder": 180
    },
    "Cobra Pose": {
        "left_knee": 180,
        "right_knee": 180,
        "left_hip": 90,
        "right_hip": 90,
        "left_shoulder": 90,
        "right_shoulder": 90
    }
}

# GUI helper function to trigger pose session
def run_pose_session(pose_name, reference_angles, video_url, model):
    st.video(video_url)
    st.markdown(f"### Now try the {pose_name}! Position yourself in front of the webcam")
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    frame_count, correct_count = 0, 0

    with st.spinner(f"📸 Checking your {pose_name}... Hold steady!"):
        while frame_count < 200:
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            keypoints = model.detect_pose(frame_rgb)
            angles = calculate_angles(keypoints)

            match_score = 0
            for joint, ref_angle in reference_angles.items():
                if joint in angles:
                    diff = abs(angles[joint] - ref_angle)
                    if diff < 20:
                        match_score += 1

            cv2.putText(frame, f"Match Score: {match_score}/{len(reference_angles)}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if match_score >= len(reference_angles) - 1:
                correct_count += 1

            stframe.image(frame, channels="BGR")
            frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    accuracy = round((correct_count / frame_count) * 100, 2)
    st.success(f"✅ {pose_name} Accuracy: {accuracy}%")
    return accuracy

import sqlite3
from fpdf import FPDF
import speech_recognition as sr

def save_report(user_id, pose_name, accuracy):
    conn = sqlite3.connect("yoga_recommendation.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pose_sessions (
            user_id INTEGER,
            pose TEXT,
            accuracy REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT INTO pose_sessions (user_id, pose, accuracy) VALUES (?, ?, ?)",
                   (user_id, pose_name, accuracy))
    conn.commit()
    conn.close()

def generate_pdf_report(user_id, pose_name, accuracy):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"Yoga Session Report - {pose_name}", ln=1, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"User ID: {user_id}", ln=1)
    pdf.cell(200, 10, txt=f"Pose Name: {pose_name}", ln=1)
    pdf.cell(200, 10, txt=f"Pose Accuracy: {accuracy}%", ln=1)
    filename = f"report_user_{user_id}_{pose_name.replace(' ', '')}.pdf"
    pdf.output(filename)
    st.success(f"📄 Report saved as {filename}")

import subprocess
import tempfile
import os

def recognize_pose_from_voice():
    st.info("🎙 Speak the pose name (e.g., Tree Pose or Cobra Pose)")

    try:
        fs = 44100
        seconds = 5
        st.info("🎤 Recording for 5 seconds...")

        # Record audio
        audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()

        # Save to temp .wav file
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, "pose_audio.wav")
        write(audio_path, fs, audio)

        # Transcribe with whisper.cpp
        whisper_exe = "whisper/main.exe"  # Adjust this path if needed
        whisper_model = "ggml-base.en.bin"  # Ensure it's in same dir or full path
        result = subprocess.run([
            whisper_exe,
            "-m", whisper_model,
            "-f", audio_path,
            "-otxt",
            "-of", "pose_output"
        ], cwd=os.path.dirname(whisper_exe), capture_output=True)

        if result.returncode != 0:
            st.error("❌ Whisper transcription failed")
            return None

        # Read transcribed output
        transcript_path = os.path.join(os.path.dirname(whisper_exe), "pose_output.txt")
        if not os.path.exists(transcript_path):
            st.error("❌ Transcription file not found")
            return None

        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read().lower()
            st.success(f"📝 Transcription: {transcript.strip()}")

            if "tree" in transcript:
                return "Tree Pose"
            elif "cobra" in transcript:
                return "Cobra Pose"
            else:
                st.warning("❓ Pose not recognized in voice")
                return None

    except Exception as e:
        st.error(f"🎤 Voice recognition error: {str(e)}")
        return None

# Streamlit configuration
st.set_page_config(
    page_title="AuraFlo - Smart Yoga Assistant",
    page_icon="🧘‍♀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Professional CSS with PERFECT BUTTON ALIGNMENT
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #001F24 0%, #002A2E 100%);
        color: #E0F7FA;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Professional Header */
    .professional-header {
        background: linear-gradient(135deg, #003B40 0%, #004D4D 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(78, 240, 231, 0.1);
        text-align: center;
    }
    
    .app-title {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4EF0E7 0%, #A7FFEB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        text-shadow: none;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: #A7FFEB;
        margin-top: 0.5rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Professional Cards */
    .feature-card {
        background: rgba(0, 77, 77, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(78, 240, 231, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(78, 240, 231, 0.1);
        border-color: rgba(78, 240, 231, 0.3);
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #4EF0E7;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-header::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(135deg, #4EF0E7, #A7FFEB);
        border-radius: 2px;
    }
    
    /* Feature Card Headings - MATCHING SECTION HEADER COLOR */
    .feature-card h4 {
        color: #4EF0E7 !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
        margin-bottom: 1rem !important;
    }
    
    .feature-card h5 {
        color: #4EF0E7 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Ensure all markdown headings in feature cards match */
    .feature-card .markdown-text-container h4,
    .feature-card .markdown-text-container h5,
    .feature-card .element-container h4,
    .feature-card .element-container h5 {
        color: #4EF0E7 !important;
        font-weight: 600 !important;
    }
    
    /* PERFECT BUTTON ALIGNMENT - FIXING ALL ISSUES */
    
    /* First, fix column spacing and padding */
    [data-testid="column"] {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }
    
    [data-testid="column"]:first-child {
        padding-left: 0 !important;
    }
    
    [data-testid="column"]:last-child {
        padding-right: 0 !important;
    }
    
    /* Button container alignment */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 0.5rem 0 !important;
        width: 100% !important;
    }
    
    /* ALL BUTTON STYLING - ENSURING CONSISTENT SIZE AND BLACK TEXT */
    div.stButton > button:first-child {
        background-color: #A7FFEB !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 0.5rem !important;
        font-size: 0.9rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        width: 100% !important;
        min-width: 140px !important;
        max-width: 200px !important;
        min-height: 48px !important;
        max-height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        margin: 0 auto !important;
    }

    div.stButton > button:first-child:hover {
        background-color: #9fffe2 !important;
        color: #000000 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    div.stButton > button:first-child:active {
        background-color: #8fffd9 !important;
        color: #000000 !important;
        transform: translateY(0px) !important;
    }

    div.stButton > button:first-child:focus {
        background-color: #A7FFEB !important;
        color: #000000 !important;
        outline: 2px solid #4EF0E7 !important;
        outline-offset: 2px !important;
    }

    /* Force all button text elements to be black */
    div.stButton > button:first-child * {
        color: #000000 !important;
    }

    div.stButton > button:first-child span {
        color: #000000 !important;
    }

    div.stButton > button:first-child p {
        color: #000000 !important;
    }

    /* Additional enforcement for button text */
    .stButton button[kind="primary"] {
        color: #000000 !important;
    }

    .stButton button[kind="secondary"] {
        color: #000000 !important;
    }

    /* Ultimate button text enforcement */
    [data-testid="stVerticalBlock"] button,
    [data-testid="stHorizontalBlock"] button,
    .stButton button {
        color: #000000 !important;
    }

    [data-testid="stVerticalBlock"] button span,
    [data-testid="stHorizontalBlock"] button span,
    .stButton button span {
        color: #000000 !important;
    }

    /* Force override any inherited text colors */
    .stButton > div > button > div {
        color: #000000 !important;
    }

    .stButton > div > button > div > p {
        color: #000000 !important;
    }
    
    /* Button row spacing */
    .stButton + .stButton {
        margin-top: 0.5rem !important;
    }

    /* Radio button styling - keeping visible text */
    .stRadio > div {
        color: #E0F7FA !important;
    }

    .stRadio > div > label {
        color: #E0F7FA !important;
    }

    .stRadio > div > label > div {
        color: #E0F7FA !important;
    }
    
    /* Primary Action Buttons */
    .primary-button {
        background: linear-gradient(135deg, #4EF0E7 0%, #A7FFEB 100%) !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .primary-button:hover {
        background: linear-gradient(135deg, #A7FFEB 0%, #4EF0E7 100%) !important;
        color: #000000 !important;
        box-shadow: 0 6px 20px rgba(78, 240, 231, 0.3) !important;
    }
    
    /* Enhanced Input Fields */
    .stTextArea textarea,
    .stTextInput > div > input,
    .stSelectbox > div > div {
        background: rgba(0, 77, 77, 0.3) !important;
        color: #E0F7FA !important;
        border: 1px solid rgba(78, 240, 231, 0.3) !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus,
    .stTextInput > div > input:focus {
        border-color: rgba(78, 240, 231, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(78, 240, 231, 0.1) !important;
        outline: none !important;
    }
    
    /* Enhanced Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #002A2E 0%, #001F24 100%) !important;
        border-right: 1px solid rgba(78, 240, 231, 0.1);
    }
    
    section[data-testid="stSidebar"] * {
        color: #E0F7FA !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #4EF0E7 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar button styling - ensuring black text */
    section[data-testid="stSidebar"] div.stButton > button:first-child {
        background-color: #A7FFEB !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        width: 100% !important;
        min-height: 48px !important;
        transition: all 0.3s ease !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:first-child:hover {
        background-color: #9fffe2 !important;
        color: #000000 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:first-child * {
        color: #000000 !important;
    }
    
    /* Professional Metrics */
    [data-testid="metric-container"] {
        background: rgba(0, 59, 64, 0.4);
        border: 1px solid rgba(78, 240, 231, 0.2);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(5px);
    }
    
    /* Enhanced Alerts */
    [data-testid="stAlert"] {
        background: rgba(1, 77, 78, 0.6) !important;
        color: #E0F7FA !important;
        border-left: 4px solid #4EF0E7 !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    .stSuccess {
        background: rgba(46, 125, 50, 0.2) !important;
        border-left-color: #4CAF50 !important;
    }
    
    .stError {
        background: rgba(211, 47, 47, 0.2) !important;
        border-left-color: #f44336 !important;
    }
    
    .stWarning {
        background: rgba(245, 124, 0, 0.2) !important;
        border-left-color: #ff9800 !important;
    }
    
    /* Professional Boxes */
    .recommendation-box {
        background: linear-gradient(135deg, rgba(0, 59, 64, 0.6) 0%, rgba(0, 77, 77, 0.4) 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(78, 240, 231, 0.2);
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .quote-box {
        background: linear-gradient(135deg, rgba(0, 77, 77, 0.6) 0%, rgba(1, 77, 78, 0.4) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        font-style: italic;
        text-align: center;
        margin: 1rem 0;
        color: #A7FFEB;
        border: 1px solid rgba(167, 255, 235, 0.2);
        backdrop-filter: blur(10px);
        position: relative;
    }
    
    .quote-box::before {
        content: '"';
        font-size: 4rem;
        color: rgba(78, 240, 231, 0.3);
        position: absolute;
        top: -10px;
        left: 20px;
        font-family: serif;
    }
    
    /* Enhanced Expanders */
    .streamlit-expanderHeader {
        background: rgba(0, 77, 77, 0.3) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(78, 240, 231, 0.2) !important;
    }
    
    /* Progress Indicators */
    .stProgress > div > div {
        background: linear-gradient(90deg, #4EF0E7, #A7FFEB) !important;
    }
    
    /* Enhanced Charts */
    .stLineChart, .stBarChart {
        background: rgba(0, 59, 64, 0.3);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(78, 240, 231, 0.1);
    }
    
    /* Professional Footer */
    .professional-footer {
        background: rgba(0, 31, 36, 0.8);
        padding: 2rem;
        border-radius: 16px;
        margin-top: 3rem;
        text-align: center;
        border: 1px solid rgba(78, 240, 231, 0.1);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2.4rem;
        }
        
        .section-header {
            font-size: 1.5rem;
        }
        
        .professional-header {
            padding: 1.5rem;
        }
        
        div.stButton > button:first-child {
            font-size: 0.8rem !important;
            padding: 0.6rem 0.4rem !important;
            min-width: 120px !important;
        }
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #4EF0E7 !important;
    }
    
    /* Enhanced Tab Design */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 77, 77, 0.3);
        border-radius: 12px;
        padding: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #A7FFEB;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4EF0E7, #A7FFEB);
        color: #001F24 !important;
    }
</style>
""", unsafe_allow_html=True)

# Professional Header with Logo
def render_professional_header():
    try:
        import base64
        def get_base64_logo(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        
        logo_base64 = get_base64_logo("yoga_baba.png")
        
        st.markdown(f"""
        <div class="professional-header">
            <img src='data:image/png;base64,{logo_base64}' width='180' style='margin-bottom: 1rem;'/>
            <h1 class="app-title">AuraFlo</h1>
            <p class="app-subtitle">AI-Powered Wellness & Fitness Companion</p>
        </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown("""
        <div class="professional-header">
            <h1 class="app-title">🧘‍♀ AuraFlo</h1>
            <p class="app-subtitle">AI-Powered Wellness & Fitness Companion</p>
        </div>
        """, unsafe_allow_html=True)

render_professional_header()

with st.sidebar:
    # -------- Logo (smaller and left-aligned) --------
    import base64
    def get_base64_logo(png_file_path):
        with open(png_file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    logo_base64 = get_base64_logo("logo.png")
    st.markdown(f"""
        <div style='text-align: left; margin-bottom: 1rem;'>
            <img src='data:image/png;base64,{logo_base64}' width='60'/>
        </div>
    """, unsafe_allow_html=True)

    # -------- Sidebar Heading --------
    st.markdown('<h2 style="color: #4EF0E7; margin-bottom: 1.5rem;">🌟 User Dashboard</h2>', unsafe_allow_html=True)

    # -------- Custom CSS: Change User ID Text Color Only --------
    st.markdown("""
        <style>
        label[for="User ID"] {
            color: #000000 !important;
        }
        div[data-baseweb="input"] input {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # -------- Profile Settings --------
    st.markdown('<h3 style="color:#A7FFEB;">👤 Profile Settings</h3>', unsafe_allow_html=True)
    user_id = st.number_input("User ID", min_value=1, step=1, value=1)

    # -------- Quick Stats --------
    st.markdown('<h3 style="color:#A7FFEB;">📊 Quick Stats</h3>', unsafe_allow_html=True)

    try:
        import sqlite3
        from yoga_agent import config
        conn = sqlite3.connect(config.database_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM journal_logs WHERE user_id = ?", (user_id,))
        journal_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT fatigue_level FROM journal_logs 
            WHERE user_id = ? 
            ORDER BY entry_date DESC 
            LIMIT 1
        """, (user_id,))
        latest_fatigue = cursor.fetchone()

        conn.close()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sessions", journal_count, delta="+1" if journal_count > 0 else None)
        with col2:
            if latest_fatigue:
                fatigue_emoji = {"high": "😴", "medium": "😐", "low": "⚡"}.get(latest_fatigue[0], "😐")
                st.metric("Energy", f"{fatigue_emoji}")
    except Exception as e:
        st.info("Stats will appear after first use")

    # -------- Daily Intention --------
    st.markdown('<h3 style="color:#A7FFEB;">💭 Daily Intention</h3>', unsafe_allow_html=True)

    intentions = [
        "I am present in this moment",
        "I listen to my body with kindness", 
        "I choose peace over perfection",
        "I am grateful for my body's strength",
        "I breathe in calm, breathe out tension"
    ]
    import random
    selected_intention = random.choice(intentions)

    st.markdown(f"""
        <div class="quote-box" style="
            font-size: 0.9rem;
            padding: 1rem;
            border-left: 4px solid #4EF0E7;
            background-color: #002D33;
            color: #E0F7FA;
            border-radius: 6px;">
            {selected_intention}
        </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🧘 Yoga Practice", "💪 Fitness Tracker", "📝 Journal & AI Coach", "📊 Analytics"])

with tab1:
    st.markdown('<div class="section-header">🧘‍♀ Yoga Practice Studio</div>', unsafe_allow_html=True)
    
    # Pose Practice Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    
    st.markdown("""
<div style='
    font-size: 1.6em;
    font-weight: 600;
    color:#A7FFEB;
    margin-top: 1em;
    margin-bottom: 0.5em;
'>
🎯 Interactive Pose Detection
</div>
""", unsafe_allow_html=True)
    st.markdown("Practice yoga poses with real-time AI feedback and form correction.")
    
    pose_model = load_pose_model()
    col1, col2 = st.columns(2)
    with col1:
     if st.button("🌳 Start Tree Pose"):
        # Your exact file path
        video_path = os.path.join("yoga_project", "video", "tree_pose_video.mp4")
        
        # Check if file exists (for debugging)
        if os.path.exists(video_path):
            st.success(f"✅ Video found: {video_path}")
        else:
            st.error(f"❌ Video not found: {video_path}")
            video_path = None
        
        run_pose_session("Tree Pose", POSE_REFERENCES["Tree Pose"], video_path, pose_model)

    with col2:
     if st.button("🐍 Start Cobra Pose"):
        # Your exact file path
        video_path = os.path.join("yoga_project", "video", "cobra_pose_tutorial.mp4")
        #yoga_project\video\tree_pose_video.mp4
        # Check if file exists (for debugging)
        if os.path.exists(video_path):
            st.success(f"✅ Video found: {video_path}")
        else:
            st.error(f"❌ Video not found: {video_path}")
            video_path = None
        
        run_pose_session("Cobra Pose", POSE_REFERENCES["Cobra Pose"], video_path, pose_model)
    
    st.markdown('</div>', unsafe_allow_html=True)
    # Quick Routines
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("""
<div style='
    font-size: 1.6em;
    font-weight: 600;
    color:#A7FFEB;
    margin-top: 1em;
    margin-bottom: 0.5em;
'>
 ⚡ Quick Wellness Routines
</div>
""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        if st.button("🌅 Morning Flow", help="Energizing 10-minute routine"):
            st.markdown("""
            <div class="recommendation-box">
            <h4 style="color: #A7FFEB;">🌅 Morning Energy Flow</h4>
            <p><strong>Duration:</strong> 10 minutes</p>
            <ol>
                <li>Cat-Cow Pose (2 min)</li>
                <li>Downward Dog (2 min)</li>
                <li>Warrior II (2 min each side)</li>
                <li>Tree Pose (1 min each side)</li>
            </ol>
            <p><em>Perfect for starting your day with energy and focus!</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🌙 Evening Calm", help="Relaxing wind-down routine"):
            st.markdown("""
            <div class="recommendation-box">
            <h4 style="color: #A7FFEB;">🌙 Evening Relaxation</h4>
            <p><strong>Duration:</strong> 15 minutes</p>
            <ol>
                <li>Child's Pose (3 min)</li>
                <li>Seated Forward Bend (3 min)</li>
                <li>Legs Up the Wall (5 min)</li>
                <li>Corpse Pose (4 min)</li>
            </ol>
            <p><em>Unwind and prepare for restful sleep.</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("⚡ Energy Boost", help="Quick energy restoration"):
            st.markdown("""
            <div class="recommendation-box">
            <h4 style="color: #A7FFEB;">⚡ Quick Energy Boost</h4>
            <p><strong>Duration:</strong> 8 minutes</p>
            <ol>
                <li>Bridge Pose (2 min)</li>
                <li>Cobra Pose (2 min)</li>
                <li>Warrior II (2 min)</li>
                <li>Tree Pose (2 min)</li>
            </ol>
            <p><em>Instant energy when you need it most!</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-header">💪 Fitness Tracker</div>', unsafe_allow_html=True)
    
    # Import fitness functions
    from session_logger import save_session_log
    from motivational import print_random_quote  
    from pushup_scoring import run_pushup_session
    from bicep_curl import run_bicep_curl_session
    from shutdown_handler import shutdown_system
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    
    st.markdown("""
<div style='
    font-size: 1.6em;
    font-weight: 600;
    color:#A7FFEB;
    margin-top: 1em;
    margin-bottom: 0.5em;
'>
 🏋 Exercise Detection & Tracking
</div>
""", unsafe_allow_html=True)
    st.markdown("Real-time form analysis with AI-powered rep counting and feedback.")
    
    # PERFECTLY ALIGNED Exercise Buttons - Using 5 equal columns for all buttons
    col1, col2, col3 = st.columns(3, gap="small")
    
    with col1:
        if st.button("💪 Push-up Session", key="pushup_session", help="Start AI-guided push-up tracking"):
            with st.spinner("🔄 Initializing push-up detection..."):
                run_pushup_session()
                # Add video reference
                video_path = "yoga_project\video\pushup_session.mp4"
                if os.path.exists(video_path):
                    st.markdown("#### 📺 Proper Form Reference")
                    with open(video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                        st.video(video_bytes)
    
    with col2:
        if st.button("💪 Bicep Curl Session", key="bicep_session", help="Start AI-guided bicep curl tracking"):
            with st.spinner("🔄 Initializing bicep curl detection..."):
                run_bicep_curl_session()
                # Add video reference
                video_path = "yoga_project\video\Bisep_curl.mp4"
                if os.path.exists(video_path):
                    st.markdown("#### 📺 Proper Form Reference")
                    with open(video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                        st.video(video_bytes)
    
    with col3:
        if st.button("💬 Get Motivated", key="motivation", help="Receive inspirational fitness quotes"):
            print_random_quote()
    
    
    st.markdown('</div>', unsafe_allow_html=True)
    

    

with tab3:
    st.markdown('<div class="section-header">📝 AI Wellness Coach</div>', unsafe_allow_html=True)
    
    # Journal Entry Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
 
    st.markdown("""
<div style='
    font-size: 1.6em;
    font-weight: 600;
    color:#A7FFEB;
    margin-top: 1em;
    margin-bottom: 0.5em;
'>
 📓 Daily Wellness Journal
</div>
""", unsafe_allow_html=True)
    st.markdown(
    '<p style="color: #A7FFEB; font-size: 16px;">Share your thoughts, mood, and physical state for personalized AI recommendations.</p>',
    unsafe_allow_html=True
    )

    st.markdown("""
    <style>
    /* Change radio label text color */
    .stRadio > label {
        color: #A7FFEB !important;
        font-weight: bold;
    }

    /* Change radio option text color */
    .stRadio div[role="radiogroup"] label {
        color: #A7FFEB !important;
    }
    </style>
""", unsafe_allow_html=True)

    input_type = st.radio("How would you like to journal today?", ["✍ Text Entry", "🎤 Voice Recording"], horizontal=True)
    
    # Initialize session state
    if 'audio_path' not in st.session_state:
        st.session_state.audio_path = None
    
    journal_text = ""
    audio_path = None
    
    if input_type == "✍ Text Entry":
        journal_text = st.text_area(
            ".",
            height=120,
            placeholder="E.g., I'm feeling energetic today but my shoulders are a bit tense from work...",
            help="Be specific about your physical and emotional state for better recommendations"
        )
    
    else:  # Voice Recording
        st.info("🎙 Click the button below to record a 5-second voice message")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎤 Start Recording", key="voice_record", help="Record your wellness check-in"):
                try:
                    fs = 44100
                    seconds = 5
                    
                    with st.spinner("🎤 Recording... Speak now!"):
                        audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
                        sd.wait()

                    if audio is not None and len(audio) > 0:
                        temp_dir = tempfile.gettempdir()
                        audio_path = os.path.join(temp_dir, f"user_{user_id}_wellness_recording.wav")
                        write(audio_path, fs, audio)
                        st.session_state.audio_path = audio_path
                        st.success("🎉 Voice recorded successfully!")
                    else:
                        st.error("❌ Recording failed - no audio captured.")
                except Exception as e:
                    st.error(f"🎤 Recording Error: {str(e)}")
                    st.info("💡 Please check your microphone permissions.")
        
        with col2:
            if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
                st.audio(st.session_state.audio_path)
                st.success("✅ Audio ready for analysis")
            else:
                st.info("📍 No recording yet")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Recommendations Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
   
    st.markdown("""
<div style='
    font-size: 1.6em;
    font-weight: 600;
    color:#A7FFEB;
    margin-top: 1em;
    margin-bottom: 0.5em;
'>
🤖 Personalized AI Recommendations
</div>
""", unsafe_allow_html=True)
    
    if st.button("🌟 Get AI Wellness Plan", key="ai_recommend", help="Generate personalized recommendations based on your input"):
        if user_id:
            with st.spinner("🧠 AI is analyzing your input and creating personalized recommendations..."):
                try:
                    result = None
                    
                    if input_type == "✍ Text Entry" and journal_text.strip():
                        result = recommend_yoga(user_id, journal_text, voice=False)
                    elif input_type == "🎤 Voice Recording":
                        audio_path = st.session_state.get("audio_path", None)
                        if audio_path and os.path.exists(audio_path):
                            result = recommend_yoga(user_id, audio_path, voice=True)
                        else:
                            st.warning("⚠ Please record your voice message first.")
                            result = None
                    else:
                        st.warning("⚠ Please provide input (text or voice) for personalized recommendations.")
                        result = None

                    if result:
                        # Enhanced recommendation display
                        st.markdown("""
                        <div class="recommendation-box">
                            <h4>🎯 Your Personalized Wellness Plan</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(result['details'])
                        
                        # Display motivational quote
                        if 'quote' in result:
                            st.markdown(f"""
                            <div class="quote-box">
                                {result["quote"]}
                            </div>
                            """, unsafe_allow_html=True)
                        
                    
                        # Professional tips section
                        with st.expander("💡 Professional Wellness Tips", expanded=True):
                            st.markdown("""
                            🔹 *Session Guidelines:*
                            - Begin with 3-5 minutes of mindful breathing
                            - Hold each pose for 30-60 seconds
                            - Focus on alignment over depth
                            - Listen to your body's signals
                            
                            🔹 *Optimization Tips:*
                            - Practice on an empty stomach (2-3 hours after meals)
                            - Stay hydrated before and after practice
                            - Use props for support when needed
                            - End with 5 minutes of relaxation
                            """)
                        
                except Exception as e:
                    st.error(f"💔 AI recommendation failed: {str(e)}")
                    st.info("💡 Please try again or check your input format.")
        else:
            st.warning("⚠ Please set your User ID in the sidebar first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-header">📊 Progress Analytics</div>', unsafe_allow_html=True)
    
    # Weekly Report Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
   
    st.markdown("""
<div style='
    font-size: 1.6em;
    font-weight: 600;
    color:#A7FFEB;
    margin-top: 1em;
    margin-bottom: 0.5em;
'>
📈 Weekly Progress Dashboard
</div>
""", unsafe_allow_html=True)
    
    if st.button("📊 Generate Weekly Report", key="weekly_report", help="View your comprehensive weekly analytics"):
        if user_id:
            try:
                with st.spinner("📊 Generating comprehensive analytics..."):
                    session_df, fatigue_df, error_counts = generate_weekly_report(user_id)

                if session_df.empty and fatigue_df.empty:
                    st.markdown("""
                    <div class="recommendation-box">
                        <h4 style="color: #A7FFEB;>📋 Getting Started</h4>
                        <p>No weekly data found yet. Keep practicing to unlock detailed analytics! 🌱</p>
                        
                        <h5>📊 What you'll see here:</h5>
                        <ul>
                            <li><strong>Pose Accuracy Trends:</strong> Track form improvement over time</li>
                            <li><strong>Energy Level Patterns:</strong> Understand your daily energy cycles</li>
                            <li><strong>Performance Insights:</strong> Areas for focused improvement</li>
                            <li><strong>Consistency Metrics:</strong> Practice frequency and duration</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Display analytics in professional layout
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if not session_df.empty:
                            st.markdown("##### 📈 Pose Accuracy Progression")
                            st.line_chart(session_df.rename(columns={"Date": "index"}).set_index("index"))
                        else:
                            st.info("📊 Pose accuracy data will appear after practice sessions")

                    with col2:
                        if not fatigue_df.empty:
                            st.markdown("##### ⚡ Energy Level Trends")
                            st.bar_chart(fatigue_df.rename(columns={"Date": "index"}).set_index("index"))
                        else:
                            st.info("📊 Energy trend data will appear after journal entries")

                    # Improvement areas
                    if error_counts:
                        st.markdown("##### 🎯 Focus Areas for Improvement")
                        improvement_data = []
                        for err, count in error_counts:
                            improvement_data.append({"Area": err.capitalize(), "Frequency": count})
                        
                        for item in improvement_data:
                            st.markdown(f"{item['Area']}:** {item['Frequency']} occurrences")
                    else:
                        st.success("✅ Excellent! No major improvement areas identified this week! 🎉")
                        
            except Exception as e:
                st.error(f"💥 Analytics generation failed: {str(e)}")
                st.info("💡 Analytics will be available after using the app for a few sessions.")
        else:
            st.warning("⚠ Please set your User ID in the sidebar to view analytics.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Metrics
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)

    st.markdown("""
<div style='
    font-size: 1.6em;
    font-weight: 600;
    color:#A7FFEB;
    margin-top: 1em;
    margin-bottom: 0.5em;
'>
🏆 Performance Metrics
</div>
""", unsafe_allow_html=True)
    
    # Sample metrics (replace with real data)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Weekly Sessions",
            value="12",
            delta="3",
            help="Total practice sessions this week"
        )
    
    with col2:
        st.metric(
            label="Average Accuracy",
            value="87%",
            delta="5%",
            help="Average pose accuracy across all sessions"
        )
    
    with col3:
        st.metric(
            label="Consistency Score",
            value="94%",
            delta="2%",
            help="How consistently you've maintained your practice"
        )
    
    with col4:
        st.metric(
            label="Wellness Score",
            value="8.2/10",
            delta="0.4",
            help="Overall wellness rating based on journal entries"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Advanced Settings & Help
with st.expander("⚙ Advanced Settings & Help", expanded=False):
    st.markdown("""
    <div class="feature-card">
        <h4>🔧 Application Settings</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🗃 Data Management")
        if st.button("🔄 Reset User Data", help="Clear all stored user data"):
            if st.checkbox("⚠ I understand this will permanently delete all my data"):
                try:
                    import sqlite3
                    conn = sqlite3.connect("yoga_recommendation.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM journal_logs WHERE user_id = ?", (user_id,))
                    cursor.execute("DELETE FROM weekly_data WHERE user_id = ?", (user_id,))
                    conn.commit()
                    conn.close()
                    st.success("✅ User data reset successfully!")
                except Exception as e:
                    st.error(f"❌ Error resetting data: {e}")
    
    with col2:
        st.markdown("##### 📊 System Status")
        try:
            from yoga_agent import config
            st.info(f"📁 Database: {config.database_name}")
            st.info(f"🤖 AI Model: {config.model_file}")
            
            # Database health check
            import sqlite3
            conn = sqlite3.connect(config.database_name)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            st.success(f"✅ Database Tables: {len(tables)} active")
            
            if 'journal_logs' in tables:
                conn = sqlite3.connect(config.database_name)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM journal_logs")
                count = cursor.fetchone()[0]
                conn.close()
                st.info(f"📝 Total Entries: {count}")
                
        except Exception as e:
            st.warning(f"⚠ System check: {e}")

with st.expander("💡 Yoga Tips & Guidelines"):
    st.markdown("""
    <h3 style='color:#A7FFEB;'>🌟 Getting Started with Yoga</h3>

    **For Beginners:**
    - Start with 10-15 minute sessions  
    - Focus on breathing and alignment over perfection  
    - Use props (blocks, straps) when needed  
    - Listen to your body and rest when needed  
    
    **Safety First:**  
    - Never force a pose  
    - Stop if you feel pain (discomfort is okay, pain is not)  
    - Warm up before deeper stretches  
    - Cool down with relaxation poses  
    
    **Making it a Habit:**  
    - Practice at the same time each day  
    - Start small and be consistent  
    - Track your progress in this app  
    - Celebrate small victories  
    
    **When to Avoid Yoga:**  
    - During acute injury or illness  
    - If you have specific medical conditions (consult your doctor)  
    - On a full stomach (wait 2–3 hours after large meals)  
""", unsafe_allow_html=True)

# Auto-initialization (Enhanced)
if 'app_initialized' not in st.session_state:
    try:
        from yoga_agent import ensure_users_table_exists, ensure_weekly_data_table_exists, train_fatigue_classifier, config
        import os
        
        with st.spinner("🚀 Initializing AuraFlo systems..."):
            # Initialize database tables
            ensure_users_table_exists()
            ensure_weekly_data_table_exists()
            
            # Train model if it doesn't exist
            if not os.path.exists(config.model_file):
                with st.spinner("🤖 Training AI wellness model for the first time..."):
                    train_fatigue_classifier()
        
        st.session_state.app_initialized = True
        st.success("✅ AuraFlo is ready for your wellness journey!")
        
    except Exception as e:
        st.error(f"⚠ Initialization notice: {e}")
        st.info("💡 The app will still function, but some AI features may be limited.")
