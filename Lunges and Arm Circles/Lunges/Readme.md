# Lunge Pose Detector (MoveNet + OpenCV)

Features
- Real-time **pose detection** with MoveNet Thunder.
- Tracks **knee, torso, elbow angles**.
- **Threshold-based scoring** (0–100).
- **Automatic repetition counter**.
- Stick-figure **skeleton overlay** for visualization.

Project Structure
- `config.py` → constants and thresholds.
- `utils.py` → helper functions (angles, skeleton drawing).
- `movenet.py` → model loading and inference.
- `lunges.py` → main script to run.
- `requirements.txt` → dependencies.

Run
Create venv
python -m venv yoga_env
yoga_env\Scripts\activate   # (Windows)

Install dependencies
pip install -r requirements.txt

Press q to quit.


Run
python lunges.py
