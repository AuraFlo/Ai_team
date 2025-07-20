# 💪 AuraFlo Push-Up Scoring System

This project is designed to evaluate push-up form in real-time using **MediaPipe Pose**, **OpenCV**, and custom logic. It calculates a dynamic score from 0 to 100 for each frame based on joint angles and counts total reps, offering visual feedback with color-coded joint lines.

## 📁 Directory Structure
auraflo_pushup_project/
│
├── pushup_scoring.py       # Main logic for detection and scoring
├── ideal_pushup_pose.py    # Define correct push-up angles and tolerances
└── utils.py                # Angle calculation, helper functions


⚙️ Setup Instructions

1. Clone the Repository

git clone https://github.com/AuraFlo/auraflo_pushup_project.git
cd auraflo_pushup_project


2. Create and Activate Virtual Environment

python3 -m venv auraflo-env
source auraflo-env/bin/activate  # For macOS/Linux
# .\auraflo-env\Scripts\activate  # For Windows

3. Install Dependencies

pip install -r requirements.txt



If you don't have a `requirements.txt`, here are some common dependencies:

mediapipe
opencv-python
numpy



🚀 How to Run
python pushup_scoring.py


Make sure your webcam is enabled. Press `Esc` to quit.


🎯 Features

✅ **Color-coded feedback**:

  * Green lines for correct joints
  * Red lines for misaligned joints
* 📈 **Pose Score**: Ranges from 0 to 100
* 🔢 **Rep Counter**: Increases on each push-up cycle
* ↔️ **Flipped Camera**: Horizontally flipped for natural mirror effect
* 📺 **Reference Pose Support**: Overlay or side-by-side demo video (optional)



## 🧠 Logic Summary

* `ideal_pushup_pose.py`: Contains ideal angles (e.g., elbow: 160-180 degrees) and tolerances
* `utils.py`: Contains helper functions for angle computation and drawing
* `pushup_scoring.py`: Orchestrates real-time video capture, scoring, feedback display, and counting logic