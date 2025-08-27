# Squat Detection & Scoring with Pose Estimation

This project uses **TensorFlow MoveNet** (a pose estimation model) and **OpenCV** to detect squats in real-time from a webcam feed.  
It tracks **hip–knee–ankle joint angles** to detect squat depth, count repetitions, and assign a **score based on form**.

---

## ⚙️ How it works

1. **Pose Detection**

   - Uses MoveNet (`.tflite` model) to extract 17 keypoints (shoulders, hips, knees, ankles, etc.) from webcam frames.

2. **Angle Calculation**

   - Calculates angles at both knees using hip, knee, and ankle coordinates.

3. **Rep Detection**

   - A rep is counted when the user moves from **down position (80°–130°)** back to **up position (>150°)**.

4. **Scoring Logic**

   - Perfect squat depth (85°–115°): **100 pts**
   - Good depth (80°–85° or 115°–130°): **90 pts**
   - Acceptable but not ideal (70°–80° or 130°–140°): **75 pts**
   - Too shallow/deep (<70° or >140°): **50 pts**

5. **Visual Feedback**
   - Skeleton is drawn in **green** during correct form, otherwise in red.
   - Live **counter** and **last rep score** are displayed on screen.

---

## 🚀 Setup & Run

### 1. Clone / Download the Project

```bash
git clone <your-repo-link>
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

Place the downloaded file in your project folder and extract it in the same location as of Jupyter Notebook:

```
3.tflite
```

### 4. Run the Program

```bash
use shift + enter to run each tab and run the main logic tab in the end
```

Your webcam will open and start detecting squats in real-time.  
Press **q** to exit.

---

## 📌 Notes

- Works best with a well-lit environment and the full body visible.
- Thresholds can be tuned inside `squats.ipynb`:
  - **Down position** → `80°–130°`
  - **Up position** → `150°–180°`
- Scoring system is customizable by editing the ranges in the code.

---

👨‍💻 Built with **Python, TensorFlow, OpenCV, NumPy**
