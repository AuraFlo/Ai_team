# High Knees Detection & Scoring with Pose Estimation

This project uses **TensorFlow MoveNet** (a pose estimation model) and **OpenCV** to detect high knees in real-time from a webcam feed.  
It tracks **hip–knee–ankle joint angles** to detect repetitions, count each leg individually, and assign a **score based on form**.

---

## ⚙️ How it works

1. **Pose Detection**

   - Uses MoveNet (`.tflite` model) to extract 17 keypoints (shoulders, hips, knees, ankles, etc.) from webcam frames.

2. **Angle Calculation**

   - Calculates angles at both knees using hip, knee, and ankle coordinates.
   - Smooths the angles using a short buffer for stability.

3. **Rep Detection**

   - A rep for each leg is counted when the knee is lifted above the hip (UP condition) and returned to neutral (DOWN condition).
   - Counts are **incremented 0.5 per leg** to get total reps.

4. **Scoring Logic**

   - Knee height close to hip and angle < 90°: **100 pts**
   - Knee slightly lower or angle < 120°: **80 pts**
   - Otherwise (less height or angle > 120°): **60 pts**

5. **Visual Feedback**
   - Skeleton is drawn in **green** during correct form, otherwise in red.
   - Live **counter** and **last rep score** are displayed on screen.

---

## 🚀 Setup & Run

### 1. Clone / Download the Project

```bash
git clone <your-repo-link>
cd high-knees-detector
```

### 2. Install Python

Make sure you have **Python 3.8+** installed.  
Check using:

```bash
python --version
```

### 3. Download MoveNet Model

Download MoveNet Lightning (TFLite) from TensorFlow Hub:  
👉 [MoveNet Lightning TFLite model](https://tfhub.dev/google/lite-model/movenet/singlepose/lightning/tflite/float16/4)

Place the downloaded file in your project folder and rename it:

```
3.tflite
```

### 4. Run the Program

```bash
use shift + enter to run each tab and run the main logic tab in the end
```

Your webcam will open and start detecting high knees in real-time.  
Press **q** to exit.

---

## 📌 Notes

- Works best in a well-lit environment with the full body visible.
- Thresholds can be tuned inside `high_knees_detector.py`:
  - **UP condition** → Knee above hip, angle < 100°
  - **DOWN condition** → Angle > 160°
- Scoring system is customizable by editing the ranges in the code.

---

👨‍💻 Built with **Python, TensorFlow, OpenCV, NumPy**
