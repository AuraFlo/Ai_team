🏋️‍♂️ Sit-Up Pose Scoring System with Real-Time Feedback

This project evaluates a user’s sit-up form using computer vision, MediaPipe Pose estimation, and angle-based scoring. It gives a score out of 100 based on pose accuracy and counts reps regardless of scoring. A reference video plays beside the live feed for guidance.

🔧 Features
	•	Real-time pose detection using webcam
	•	Scoring system (0–100) based on knee and elbow angles
	•	Green/red feedback lines for correct/incorrect joints
	•	Reference video side-by-side with live feed
	•	Flip webcam view for better alignment
	•	Continuous sit-up counter (independent of score)

⸻

📁 Directory Structure

situp-scoring-system/
│
├── ideal_pose.json           # Ideal angle values and tolerance per joint
├── pose_reference.mp4        # Video showing the correct sit-up form
├── situp_pose_score.py       # Main application file
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation

🚀 How to Run

1. Clone the Repository
git clone https://github.com/AuraFlo/situp-scoring-system.git
cd situp-scoring-system

2. Create a Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Add Pose Reference Video and Ideal Pose JSON
	•	Place a reference video named pose_reference.mp4 showing the correct sit-up posture.
	•	Use the provided ideal_pose.json (already in the repo) or modify as needed.

5. Run the Application
python situp_pose_score.py




⚙️ Configuration

You can tweak:
	•	ideal_pose.json – Define angles and tolerances for different joints.
	•	pose_reference.mp4 – Replace with your own instructional video.
	•	Webcam angle – Camera should be placed sideways for sit-up detection.




📊 Output
	•	🟢 Green lines: Joint within ideal angle range
	•	🔴 Red lines: Joint outside acceptable range
	•	🧠 Pose Score: From 0 (bad form) to 100 (perfect form)
	•	🔢 Sit-Up Counter: Counts reps regardless of form

⸻

📌 Dependencies
	•	Python 3.7–3.11
	•	OpenCV
	•	MediaPipe
	•	NumPy

Install all using requirements.txt.