import mediapipe as mp
import cv2
import numpy as np


#initialize mediapipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, 
                    min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a = np.array(a)  # Shoulder
    b = np.array(b)  # Elbow
    c = np.array(c)  # Wrist

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    return int(angle)

counter = 0
stage = None

#initializing webcam

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    frame = cv2.flip(frame,1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        landmarks = results.pose_landmarks.landmark
        #coordinates
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
        
        #calculate angle
        angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        #display angle 
        cv2.putText(frame, f"Angle: {angle}", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        #curls
        if angle > 160:
            stage = "down"
        if angle < 45 and stage == "down":
            stage = "up"
            counter += 1
            print(f"Rep count: {counter}")
        
        #display counter
        cv2.putText(frame, f"Counter: {counter}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    #show cam
    cv2.imshow("Bicep Counter", frame)

    #esc on q
    if cv2.waitKey(1) & 0xFF ==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
