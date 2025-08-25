import cv2
from movenet import detect_pose
from utils import calculate_angle, draw_skeleton
from config import *

counter = 0
stage = None
last_rep_score = 0

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    keypoints = detect_pose(frame)[0]   # (17,3)

    
    left_hip     = (keypoints[11][1] * w, keypoints[11][0] * h)
    left_knee    = (keypoints[13][1] * w, keypoints[13][0] * h)
    left_ankle   = (keypoints[15][1] * w, keypoints[15][0] * h)
    left_shoulder= (keypoints[5][1] * w, keypoints[5][0] * h)
    left_elbow   = (keypoints[7][1] * w, keypoints[7][0] * h)
    left_wrist   = (keypoints[9][1] * w, keypoints[9][0] * h)
    left_ear     = (keypoints[3][1] * w, keypoints[3][0] * h)

    knee_angle  = calculate_angle(left_hip, left_knee, left_ankle)
    elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    torso_angle = calculate_angle(left_hip, left_shoulder, left_ear)

    score = 100
    joint_status = "Correct"
    if not (ELBOW_MIN <= elbow_angle <= ELBOW_MAX):
        score -= 30; joint_status = "Incorrect"
    if not (TORSO_MIN <= torso_angle <= TORSO_MAX):
        score -= 30; joint_status = "Incorrect"
    if not (KNEE_MIN <= knee_angle <= KNEE_MAX):
        score -= 40; joint_status = "Incorrect"

    if knee_angle > 160:
        stage = "up"
    if knee_angle < 90 and stage == "up":
        stage = "down"
        counter += 1
        last_rep_score = score

    frame = draw_skeleton(frame, keypoints)

    cv2.putText(frame, f"Knee: {int(knee_angle)} deg", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, f"Elbow: {int(elbow_angle)} deg", (50,130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, f"Torso: {int(torso_angle)} deg", (50,160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    color = (0,255,0) if joint_status=="Correct" else (0,0,255)
    cv2.putText(frame, f"Status: {joint_status}", (50,200), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 3)

    cv2.putText(frame, f"Rep Count: {counter}", (50,250), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,255), 3)
    cv2.putText(frame, f"Last Rep Score: {last_rep_score}", (50,300), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,0), 3)

    cv2.imshow("Lunge Detector", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
