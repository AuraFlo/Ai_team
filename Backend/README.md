# 💪 AuraFlo Backend

Backend system for **AuraFlo** – a fitness & yoga assistant powered by **MoveNet (TFLite)**, **OpenCV**, and **FastAPI**.  
It supports **real-time exercise detection**, **breathing monitoring**, **emotion detection**, and a **yoga recommendation agent**.

---

## 🚀 Features

- **Exercise Detection**  
  - Pushups, Squats, Lunges, High Knees, Bicep Curls, Arm Circles  
  - Real-time pose estimation using **MoveNet (TFLite)**  
  - Accuracy & form evaluation  
  - Automatic rep counting  

- **Breathing Monitor**  
  - Tracks breathing rate from webcam ROI  
  - Detects irregular breathing (age-adjusted thresholds)  

- **Emotion Detection**  
  - Classifies facial expressions (Happy, Sad, Angry, etc.)  
  - Works alongside exercises for fatigue detection  

- **Yoga Recommendation Agent**  
  - Uses text/voice journal input  
  - Predicts fatigue with an ML model (SVM)  
  - Recommends yoga poses based on user’s health & goals  
  - Stores weekly logs & generates reports  

- **Reports**  
  - PDF session reports with reps, accuracy, breathing, and emotion trends  

---

## 🗂 Project Structure

```
AuraFlo_Backend/
│── app/
│   ├── api/               # FastAPI endpoints
│   │   ├── endpoints/
│   │   │   ├── arm_circles.py
│   │   │   ├── pushups.py
│   │   │   ├── squats.py
│   │   │   ├── lunges.py
│   │   │   ├── high_knees.py
│   │   │   ├── bicep_curls.py
│   │   │   ├── yoga_agent.py
│   │   │   └── reports.py
│   ├── core/              # Core utilities
│   │   ├── camera.py
│   │   ├── processor.py
│   │   ├── logger.py
│   │   ├── preprocessor.py
│   │   ├── utils.py
│   │   └── visualizer.py
│   ├── db/                # Database (SQLAlchemy + SQLite)
│   │   ├── database.py
│   │   ├── models.py
│   │   └── crud.py
│   ├── services/          # Exercise + AI services
│   │   ├── pushup_service.py
│   │   ├── squat_service.py
│   │   ├── lunge_service.py
│   │   ├── highKnees_service.py
│   │   ├── bicepCurl_service.py
│   │   ├── armCircles_service.py
│   │   ├── breathing_service.py
│   │   ├── emotion_service.py
│   │   ├── movenet_service.py
│   │   └── report_generator.py
│   ├── schemas/           # Pydantic schemas
│   ├── yoga_agent.py      # Yoga recommendation engine
│   ├── main.py            # FastAPI entrypoint
│   └── convert_movenet.py # Convert TF model → TFLite
│── tflite_models/         # Pre-trained TFLite models
│── saved_models/          # Saved TF models
│── requirements.txt
│── README.md
```

---

## ⚙️ Setup

### 1️⃣ Clone the repo
```bash
git clone https://github.com/your-username/AuraFlo_Backend.git
cd AuraFlo_Backend
```

### 2️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup database
```bash
python
>>> from app.db.database import Base, engine
>>> from app.db import models
>>> Base.metadata.create_all(bind=engine)
```

---

## ▶️ Running the Backend

### Start FastAPI server
```bash
uvicorn app.main:app --reload
```

Backend will be live at: **http://127.0.0.1:8000**

### API Docs (Swagger)
👉 Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📦 TFLite Models

Download and place MoveNet + Emotion models:

- `movenet_lightning.tflite` → `tflite_models/`
- `emotion_model.tflite` → `tflite_models/`

Convert from TFHub if needed:
```bash
python app/convert_movenet.py
```

---

## 📊 Reports

- PDF reports are generated under `logs/`  
- Example call:
```python
from app.services.report_generator import generate_session_report
path = generate_session_report(user_id=1)
print("Saved:", path)
```

---

## 🖥 Deployment on Raspberry Pi

- Use **TFLite models only** (`.tflite`)  
- Install **TensorFlow Lite Runtime** instead of full TensorFlow:
```bash
pip install tflite-runtime
```
- Optimize models with quantization for faster inference

---

## 📌 Tech Stack

- **FastAPI** (backend & REST APIs)
- **OpenCV** (video processing + skeleton drawing)
- **TensorFlow Lite** (pose detection, emotion recognition)
- **SQLite + SQLAlchemy** (database)
- **scikit-learn** (fatigue classifier)
- **Whisper.cpp** (voice-to-text for yoga journaling)
- **ReportLab + Matplotlib** (PDF reports)

---
## 🔗 Integration with Frontend

To integrate this backend with a React frontend:

1. **API Base URL**  
   - The backend runs by default at:  
     ```
     http://127.0.0.1:8000
     ```
   - Example: Fetch pushup results:
     ```javascript
     fetch("http://127.0.0.1:8000/pushups/process", {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({ landmarks: poseLandmarks })
     })
     .then(res => res.json())
     .then(data => console.log(data));
     ```

2. **WebSocket Streaming (Real-time)**  
   - For live exercise + emotion + breathing monitoring, connect to the WebSocket:
     ```javascript
     const ws = new WebSocket("ws://127.0.0.1:8765");
     ws.onmessage = (event) => {
       const data = JSON.parse(event.data);
       console.log("Real-time results:", data);
     };
     ```

3. **Frontend Responsibilities**
   - Capture webcam frames using `MediaPipe` or `WebRTC`.
   - Send frames or landmark JSON to the backend endpoints.
   - Display backend responses (rep count, accuracy, breathing, emotion, etc.) in the UI.

4. **Instruction Overlays**
   - The backend provides analysis only.  
   - The **frontend should render instructions and color overlays** (e.g., green for correct posture, red for incorrect) using the response fields like `state`, `accuracy`, and `angles`.


