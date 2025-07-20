# import cv2
# import mediapipe as mp
# import numpy as np
# from utils import calculate_angle
# from ideal_pushup_pose import ideal_pushup_pose, joint_weights

# # Initialize MediaPipe
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose()
# mp_drawing = mp.solutions.drawing_utils

# # Start webcam
# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Resize and flip
#     frame = cv2.flip(frame, 1)
#     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = pose.process(image)
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#         landmarks = results.pose_landmarks.landmark

#         # Extract required coordinates
#         def get_point(landmark):
#             return [landmarks[landmark.value].x, landmarks[landmark.value].y]

#         shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
#         elbow = get_point(mp_pose.PoseLandmark.LEFT_ELBOW)
#         wrist = get_point(mp_pose.PoseLandmark.LEFT_WRIST)
#         hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
#         knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)

#         # Calculate angles
#         elbow_angle = calculate_angle(shoulder, elbow, wrist)
#         shoulder_angle = calculate_angle(elbow, shoulder, hip)
#         back_angle = calculate_angle(shoulder, hip, knee)
#         hip_angle = calculate_angle(shoulder, hip, knee)  # same as back_angle

#         # Compare with ideal pose
#         elbow_diff = abs(elbow_angle - ideal_pushup_pose["elbow_angle"])
#         shoulder_diff = abs(shoulder_angle - ideal_pushup_pose["shoulder_angle"])
#         back_diff = abs(back_angle - ideal_pushup_pose["back_angle"])
#         hip_diff = abs(hip_angle - ideal_pushup_pose["hip_angle"])

#         # Weighted scoring
#         score = 100 - (
#             elbow_diff * joint_weights["elbow_angle"] +
#             shoulder_diff * joint_weights["shoulder_angle"] +
#             back_diff * joint_weights["back_angle"] +
#             hip_diff * joint_weights["hip_angle"]
#         )
#         score = max(0, min(100, score))  # Clamp between 0–100

#         # Visual feedback
#         cv2.putText(image, f'Elbow: {int(elbow_angle)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
#         cv2.putText(image, f'Shoulder: {int(shoulder_angle)}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
#         cv2.putText(image, f'Back: {int(back_angle)}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
#         cv2.putText(image, f'Score: {int(score)}', (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3)

#         # Color-coded joint feedback (elbow)
#         elbow_px = tuple(np.multiply(elbow, [frame.shape[1], frame.shape[0]]).astype(int))
#         elbow_color = (0, 255, 0) if elbow_diff < 15 else (0, 0, 255)
#         cv2.circle(image, elbow_px, 10, elbow_color, -1)

#     cv2.imshow('Push-up Scoring', image)
#     if cv2.waitKey(10) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()



# import cv2
# import mediapipe as mp
# import numpy as np
# from utils import calculate_angle
# from ideal_pushup_pose import ideal_pushup_pose, joint_weights

# # ========== USER INPUT ==========
# user_height_cm = float(input("Enter your height (in cm): "))
# user_weight_kg = float(input("Enter your weight (in kg): "))

# # Calories burned per push-up (approx.)
# def estimate_calories_burned(pushup_count, weight):
#     MET = 8
#     time_per_pushup_hours = 2 / 3600  # 2 seconds per push-up
#     return round(MET * weight * time_per_pushup_hours * pushup_count, 2)

# # ========== MediaPipe Setup ==========
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose()
# mp_drawing = mp.solutions.drawing_utils

# # ========== Initialize Counter Variables ==========
# pushup_count = 0
# stage = None  # "UP" or "DOWN"

# # ========== Start Webcam ==========
# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame = cv2.flip(frame, 1)
#     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = pose.process(image)
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#         landmarks = results.pose_landmarks.landmark

#         def get_point(landmark):
#             return [landmarks[landmark.value].x, landmarks[landmark.value].y]

#         # Keypoints
#         shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
#         elbow = get_point(mp_pose.PoseLandmark.LEFT_ELBOW)
#         wrist = get_point(mp_pose.PoseLandmark.LEFT_WRIST)
#         hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
#         knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)

#         # Angles
#         elbow_angle = calculate_angle(shoulder, elbow, wrist)
#         shoulder_angle = calculate_angle(elbow, shoulder, hip)
#         back_angle = calculate_angle(shoulder, hip, knee)
#         hip_angle = calculate_angle(shoulder, hip, knee)  # same

#         # Diffs from ideal
#         elbow_diff = abs(elbow_angle - ideal_pushup_pose["elbow_angle"])
#         shoulder_diff = abs(shoulder_angle - ideal_pushup_pose["shoulder_angle"])
#         back_diff = abs(back_angle - ideal_pushup_pose["back_angle"])
#         hip_diff = abs(hip_angle - ideal_pushup_pose["hip_angle"])

#         # Score
#         score = 100 - (
#             elbow_diff * joint_weights["elbow_angle"] +
#             shoulder_diff * joint_weights["shoulder_angle"] +
#             back_diff * joint_weights["back_angle"] +
#             hip_diff * joint_weights["hip_angle"]
#         )
#         score = max(0, min(100, score))

#         # ---------- PUSH-UP STAGE LOGIC ----------
#         # Detect full push-up: DOWN → UP = 1 rep
#         if elbow_angle <= 90:
#             stage = "DOWN"
#         elif elbow_angle >= 160 and stage == "DOWN":
#             stage = "UP"
#             pushup_count += 1

#         # ---------- Display Info ----------
#         cv2.putText(image, f'Push-Ups: {pushup_count}', (10, 40),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
#         cv2.putText(image, f'Score: {int(score)}', (10, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

#         # Elbow color feedback
#         elbow_px = tuple(np.multiply(elbow, [frame.shape[1], frame.shape[0]]).astype(int))
#         elbow_color = (0, 255, 0) if elbow_diff < 15 else (0, 0, 255)
#         cv2.circle(image, elbow_px, 10, elbow_color, -1)

#         # Show calories burned
#         calories = estimate_calories_burned(pushup_count, user_weight_kg)
#         cv2.putText(image, f'Calories: {calories} kcal', (10, 120),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#     # ---------- Show Output ----------
#     cv2.imshow('Push-up Scoring System', image)
#     if cv2.waitKey(10) & 0xFF == ord('q'):
#         break

# # ========== Cleanup ==========
# cap.release()
# cv2.destroyAllWindows()





# import cv2
# import mediapipe as mp
# import numpy as np
# from utils import calculate_angle
# from ideal_pushup_pose import ideal_pushup_pose, joint_weights

# # ========== USER INPUT ==========
# user_height_cm = float(input("Enter your height (in cm): "))
# user_weight_kg = float(input("Enter your weight (in kg): "))

# def estimate_calories_burned(pushup_count, weight):
#     MET = 8  # Metabolic equivalent for push-ups
#     time_per_pushup_hours = 2 / 3600  # 2 seconds per push-up
#     return round(MET * weight * time_per_pushup_hours * pushup_count, 2)

# # ========== MediaPipe Setup ==========
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose()
# mp_drawing = mp.solutions.drawing_utils

# # ========== Initialize Counter Variables ==========
# pushup_count = 0
# stage = None  # "UP" or "DOWN"

# # ========== Start Webcam ==========
# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame = cv2.flip(frame, 1)
#     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = pose.process(image)
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#         landmarks = results.pose_landmarks.landmark

#         def get_point(landmark):
#             return [landmarks[landmark.value].x, landmarks[landmark.value].y]

#         # Keypoints (Left Side)
#         shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
#         elbow = get_point(mp_pose.PoseLandmark.LEFT_ELBOW)
#         wrist = get_point(mp_pose.PoseLandmark.LEFT_WRIST)
#         hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
#         knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)

#         # Angles
#         elbow_angle = calculate_angle(shoulder, elbow, wrist)
#         shoulder_angle = calculate_angle(elbow, shoulder, hip)
#         back_angle = calculate_angle(shoulder, hip, knee)
#         hip_angle = calculate_angle(shoulder, hip, knee)  # same as back_angle

#         # Diffs from ideal
#         elbow_diff = abs(elbow_angle - ideal_pushup_pose["elbow_angle"])
#         shoulder_diff = abs(shoulder_angle - ideal_pushup_pose["shoulder_angle"])
#         back_diff = abs(back_angle - ideal_pushup_pose["back_angle"])
#         hip_diff = abs(hip_angle - ideal_pushup_pose["hip_angle"])

#         # Score
#         score = 100 - (
#             elbow_diff * joint_weights["elbow_angle"] +
#             shoulder_diff * joint_weights["shoulder_angle"] +
#             back_diff * joint_weights["back_angle"] +
#             hip_diff * joint_weights["hip_angle"]
#         )
#         score = max(0, min(100, score))

#         # ---------- PUSH-UP COUNTER ----------
#         if elbow_angle <= 90:
#             stage = "DOWN"
#         elif elbow_angle >= 160 and stage == "DOWN":
#             stage = "UP"
#             pushup_count += 1

#         # ---------- Calories Burned ----------
#         calories = estimate_calories_burned(pushup_count, user_weight_kg)

#         # ---------- Visual Feedback ----------
#         cv2.putText(image, f'Push-Ups: {pushup_count}', (10, 40),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
#         cv2.putText(image, f'Score: {int(score)}', (10, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#         cv2.putText(image, f'Calories: {calories} kcal', (10, 120),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#         # ---------- Color-Coded Stick Figure ----------
#         def draw_joint(img, pt, color):
#             px = tuple(np.multiply(pt, [frame.shape[1], frame.shape[0]]).astype(int))
#             cv2.circle(img, px, 10, color, -1)

#         def draw_limb(img, pt1, pt2, color):
#             p1 = tuple(np.multiply(pt1, [frame.shape[1], frame.shape[0]]).astype(int))
#             p2 = tuple(np.multiply(pt2, [frame.shape[1], frame.shape[0]]).astype(int))
#             cv2.line(img, p1, p2, color, 4)

#         THRESHOLD = 15

#         elbow_color = (0, 255, 0) if elbow_diff < THRESHOLD else (0, 0, 255)
#         shoulder_color = (0, 255, 0) if shoulder_diff < THRESHOLD else (0, 0, 255)
#         back_color = (0, 255, 0) if back_diff < THRESHOLD else (0, 0, 255)
#         hip_color = (0, 255, 0) if hip_diff < THRESHOLD else (0, 0, 255)

#         # Draw joints
#         draw_joint(image, shoulder, shoulder_color)
#         draw_joint(image, elbow, elbow_color)
#         draw_joint(image, wrist, elbow_color)
#         draw_joint(image, hip, hip_color)
#         draw_joint(image, knee, back_color)

#         # Draw limbs
#         draw_limb(image, shoulder, elbow, elbow_color)
#         draw_limb(image, elbow, wrist, elbow_color)
#         draw_limb(image, shoulder, hip, back_color)
#         draw_limb(image, hip, knee, hip_color)

#     # ---------- Show Output ----------
#     cv2.imshow('Push-up Scoring System', image)
#     if cv2.waitKey(10) & 0xFF == ord('q'):
#         break

# # ========== Cleanup ==========
# cap.release()
# cv2.destroyAllWindows()






import cv2
import mediapipe as mp
import numpy as np
from utils import calculate_angle
from ideal_pushup_pose import ideal_pushup_pose, joint_weights

# ========== USER INPUT ==========
user_height_cm = float(input("Enter your height (in cm): "))
user_weight_kg = float(input("Enter your weight (in kg): "))

def estimate_calories_burned(pushup_count, weight):
    MET = 8  # Metabolic equivalent for push-ups
    time_per_pushup_hours = 2 / 3600  # 2 seconds per push-up
    return round(MET * weight * time_per_pushup_hours * pushup_count, 2)

# ========== MediaPipe Setup ==========
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# ========== Counter ==========
pushup_count = 0
stage = None  # "DOWN" or "UP"

# ========== Webcam ==========
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror view
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark

        def get_point(landmark):
            return [landmarks[landmark.value].x, landmarks[landmark.value].y]

        # LEFT SIDE
        l_shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER)
        l_elbow = get_point(mp_pose.PoseLandmark.LEFT_ELBOW)
        l_wrist = get_point(mp_pose.PoseLandmark.LEFT_WRIST)
        l_hip = get_point(mp_pose.PoseLandmark.LEFT_HIP)
        l_knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE)

        # RIGHT SIDE
        r_shoulder = get_point(mp_pose.PoseLandmark.RIGHT_SHOULDER)
        r_elbow = get_point(mp_pose.PoseLandmark.RIGHT_ELBOW)
        r_wrist = get_point(mp_pose.PoseLandmark.RIGHT_WRIST)
        r_hip = get_point(mp_pose.PoseLandmark.RIGHT_HIP)
        r_knee = get_point(mp_pose.PoseLandmark.RIGHT_KNEE)

        # ANGLES (average for scoring)
        elbow_angle = (calculate_angle(l_shoulder, l_elbow, l_wrist) +
                       calculate_angle(r_shoulder, r_elbow, r_wrist)) / 2

        shoulder_angle = (calculate_angle(l_elbow, l_shoulder, l_hip) +
                          calculate_angle(r_elbow, r_shoulder, r_hip)) / 2

        back_angle = (calculate_angle(l_shoulder, l_hip, l_knee) +
                      calculate_angle(r_shoulder, r_hip, r_knee)) / 2

        hip_angle = back_angle

        # Diffs from ideal
        elbow_diff = abs(elbow_angle - ideal_pushup_pose["elbow_angle"])
        shoulder_diff = abs(shoulder_angle - ideal_pushup_pose["shoulder_angle"])
        back_diff = abs(back_angle - ideal_pushup_pose["back_angle"])
        hip_diff = abs(hip_angle - ideal_pushup_pose["hip_angle"])

        # Score
        score = 100 - (
            elbow_diff * joint_weights["elbow_angle"] +
            shoulder_diff * joint_weights["shoulder_angle"] +
            back_diff * joint_weights["back_angle"] +
            hip_diff * joint_weights["hip_angle"]
        )
        score = max(0, min(100, score))

        # COUNTER LOGIC
        if elbow_angle <= 90:
            stage = "DOWN"
        elif elbow_angle >= 160 and stage == "DOWN":
            stage = "UP"
            pushup_count += 1

        calories = estimate_calories_burned(pushup_count, user_weight_kg)

        # INFO TEXT
        cv2.putText(image, f'Push-Ups: {pushup_count}', (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(image, f'Score : {int(score)}', (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.putText(image, f'Calories : {calories} kcal', (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # COLOR-CODED FEEDBACK
        def draw_joint(img, pt, color):
            px = tuple(np.multiply(pt, [frame.shape[1], frame.shape[0]]).astype(int))
            cv2.circle(img, px, 10, color, -1)

        def draw_limb(img, pt1, pt2, color):
            p1 = tuple(np.multiply(pt1, [frame.shape[1], frame.shape[0]]).astype(int))
            p2 = tuple(np.multiply(pt2, [frame.shape[1], frame.shape[0]]).astype(int))
            cv2.line(img, p1, p2, color, 4)

        # Individual arm/joint correctness
        THRESHOLD = 15
        l_elbow_diff = abs(calculate_angle(l_shoulder, l_elbow, l_wrist) - ideal_pushup_pose["elbow_angle"])
        r_elbow_diff = abs(calculate_angle(r_shoulder, r_elbow, r_wrist) - ideal_pushup_pose["elbow_angle"])

        l_color = (0, 255, 0) if l_elbow_diff < THRESHOLD else (0, 0, 255)
        r_color = (0, 255, 0) if r_elbow_diff < THRESHOLD else (0, 0, 255)

        # Draw left arm
        draw_joint(image, l_shoulder, l_color)
        draw_joint(image, l_elbow, l_color)
        draw_joint(image, l_wrist, l_color)
        draw_limb(image, l_shoulder, l_elbow, l_color)
        draw_limb(image, l_elbow, l_wrist, l_color)

        # Draw right arm
        draw_joint(image, r_shoulder, r_color)
        draw_joint(image, r_elbow, r_color)
        draw_joint(image, r_wrist, r_color)
        draw_limb(image, r_shoulder, r_elbow, r_color)
        draw_limb(image, r_elbow, r_wrist, r_color)

        # Draw back/torso
        back_color = (0, 255, 0) if back_diff < THRESHOLD else (0, 0, 255)
        hip_color = (0, 255, 0) if hip_diff < THRESHOLD else (0, 0, 255)
        draw_joint(image, l_hip, hip_color)
        draw_joint(image, l_knee, back_color)
        draw_limb(image, l_shoulder, l_hip, back_color)
        draw_limb(image, l_hip, l_knee, hip_color)

    # SHOW WINDOW
    cv2.imshow('Push-up Scoring System', image)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# CLEANUP
cap.release()
cv2.destroyAllWindows()