# Yoga Pose Detection – Arm Circles

This project detects **Arm Circles Exercise** using [MoveNet](https://tfhub.dev/google/movenet/singlepose/lightning/4), with:
- Real-time **pose detection & stick figure visualization**
- **Threshold-based scoring (arm straightness, radius, smoothness)
- Repetition counting
- Color-coded feedback
- Bilingual instructions (English + Hindi)

## Installation

 1. Clone the repo
```bash
git clone https://github.com/yourusername/yoga-task.git
cd yoga-task

2. Create a virtual environment (recommended)
python -m venv yoga_env
source yoga_env/bin/activate      # Linux / Mac
yoga_env\Scripts\activate         # Windows PowerShell

3. Install dependencies
pip install -r requirements.txt

Controls:

Press s → toggle skeleton overlay
Press q → quit program

Features
Detects Left & Right Arm Circles separately
Computes:

  Elbow Angle
  Circle Radius Ratio
  Accuracy Score (0–100 per rep)
  Tracks Repetition Count
  Overlays Bilingual Instructions:
  English: "Stand straight, extend arms, draw big circles."

Hindi: "निर्देश: सीधे खड़े हों, बाँहें सीधी रखें, बड़े गोल घुमाएँ।"
