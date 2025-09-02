
# 🧘 Adaptive Yoga Recommendation System

The **Adaptive Yoga Recommendation System** is an AI-powered wellness assistant that enhances yoga practice through personalized recommendations based on user journaling and pose performance.

---

## 💡 What It Does

This system analyzes the user's journal input—either written or spoken—and combines it with their personal health data and pose accuracy trends to recommend suitable yoga poses. The recommendations support recovery, improve form, and promote consistency.

---

## ✨ Key Features

- 🗣️ **Journal Input (Text or Voice)**: Users can record or write a short entry about fatigue, stress, or pain. Voice input is transcribed using the `Whisper` model via `faster-whisper`.

- 👤 **User Profile Awareness**: Considers age, gender, injury history, and fitness goals to make safe, personalized suggestions.

- 📈 **Weekly Progress Tracking**: Tracks pose accuracy, posture errors, and fatigue across sessions using charts.

- 🧘 **Intelligent Pose Suggestions**: Based on journal analysis (e.g., "back pain", "fatigue"), recommends 2–4 beginner-friendly poses focused on safety and goals.

- 📚 **Integrated Learning Support**:
  - Tutorial video link
  - Wikipedia snippet for pose background
  - DuckDuckGo live search results for deeper learning

- 🧾 **Summary Report**: Includes motivational quotes, practice tips, and injury-specific modifications.

---

## 🛠️ Built With

- Python (Streamlit, SQLite3, pandas)
- Faster-Whisper (for transcription)
- Matplotlib (for charts and visuals)
- Web scraping: DuckDuckGo + Wikipedia

---

---

## ⚙️ Setup Guide

### ✅ 1. Install Anaconda
[Download Anaconda](https://www.anaconda.com/products/distribution)

### ✅ 2. Create and Activate Virtual Environment
Using Anaconda Prompt:

```bash
conda create -n yoga-env python=3.10
conda activate yoga-env
```

### ✅ 3. Install Dependencies

Navigate to the project folder and run:

```bash
pip install -r requirements.txt
```

### ✅ 4. Set Up FFmpeg (for Whisper Voice Input)

1. Download from: [FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/)
2. Extract to: `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH
4. Restart Anaconda Prompt

### ▶️ 5. Run the App

```bash
streamlit run app.py
```

The app will open in your browser.

---

## 🧪 Features Recap

- Voice + text journaling input
- Weekly trend charts (fatigue + accuracy)
- Personalized yoga pose suggestions
- Tutorials + Wikipedia background
- NLP-based issue detection (e.g., back pain, fatigue)

---

## 🗄️ Initial Database (Optional)

If running for the first time, you can initialize the database by calling:

```python
create_and_populate_db()
```

This seeds demo users and sessions.

---

## 🧑‍💻 Developer Notes

- Whisper handles voice transcription
- You can customize logic in `yoga_agent.py`
- Reports are based on actual session logs

---

## ❤️ Contact

Facing issues running the app? Open an issue on GitHub or reach out!

