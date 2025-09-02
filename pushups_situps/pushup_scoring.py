# Single side stick diagram


# import cv2
# import numpy as np
# import streamlit as st
# from pathlib import Path
# from pose_estimator import PoseEstimator
# from angles import calculate_angle

# def draw_pushup_pose(frame, landmarks, angle, hip_angle):
#     for i in [5, 7, 9, 11, 13]:
#         cv2.circle(frame, landmarks[i], 5, (0, 255, 255), -1)

#     arm_color = (0, 255, 0) if angle < 100 else (0, 0, 255)
#     torso_color = (0, 255, 0) if hip_angle > 150 else (0, 0, 255)

#     cv2.line(frame, landmarks[5], landmarks[7], arm_color, 2)
#     cv2.line(frame, landmarks[7], landmarks[9], arm_color, 2)
#     cv2.line(frame, landmarks[5], landmarks[11], torso_color, 2)
#     cv2.line(frame, landmarks[11], landmarks[13], torso_color, 2)

# def run_pushup_session():
#     st.markdown("## 💪 Push-up Session")
#     st.info("🔄 Live camera will open below. Click **Stop Pushup Session** to end.")

#     # Streamlit stop session control
#     stop_button = st.button("🛑 Stop Pushup Session")
#     frame_window = st.empty()

#     model_path = Path(__file__).resolve().parent.parent / "models" / "movenet.tflite"
#     detector = PoseEstimator(str(model_path))

#     cap = cv2.VideoCapture(0)
#     count, score, stage = 0, 0, None

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret or stop_button:
#             break

#         landmarks = detector.detect(frame)
#         if landmarks and len(landmarks) >= 14:
#             shoulder, elbow, wrist = landmarks[5], landmarks[7], landmarks[9]
#             hip, knee = landmarks[11], landmarks[13]

#             angle = calculate_angle(shoulder, elbow, wrist)
#             hip_angle = calculate_angle(shoulder, hip, knee)

#             if angle > 160:
#                 stage = "down"
#             elif angle < 90 and stage == "down":
#                 stage = "up"
#                 count += 1

#             score = 100 if angle < 100 and hip_angle > 150 else 70 if angle < 100 else 30
#             draw_pushup_pose(frame, landmarks, angle, hip_angle)

#             cv2.putText(frame, f'Push-ups: {count}', (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
#             cv2.putText(frame, f'Pose Score: {score}', (10, 60),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame_window.image(frame, channels="RGB")

#     cap.release()
#     cv2.destroyAllWindows()
#     st.success(f"🏁 Session ended! Total Push-ups: {count}")

# __all__ = ['run_pushup_session']







# Double Stick Diagram





import cv2
import numpy as np
import streamlit as st
from pathlib import Path
from pose_estimator import PoseEstimator
from angles import calculate_angle

def draw_pushup_pose(frame, landmarks, l_angle, l_hip_angle, r_angle, r_hip_angle):
    # Draw joints for both sides
    for idx in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
        cv2.circle(frame, landmarks[idx], 6, (0, 255, 255), -1)

    # Left arm and torso
    l_arm_color = (0, 255, 0) if l_angle < 100 else (0, 0, 255)
    l_torso_color = (0, 255, 0) if l_hip_angle > 150 else (0, 0, 255)

    cv2.line(frame, landmarks[5], landmarks[7], l_arm_color, 3)
    cv2.line(frame, landmarks[7], landmarks[9], l_arm_color, 3)
    cv2.line(frame, landmarks[5], landmarks[11], l_torso_color, 3)
    cv2.line(frame, landmarks[11], landmarks[13], l_torso_color, 3)

    # Right arm and torso
    r_arm_color = (0, 255, 0) if r_angle < 100 else (0, 0, 255)
    r_torso_color = (0, 255, 0) if r_hip_angle > 150 else (0, 0, 255)

    cv2.line(frame, landmarks[6], landmarks[8], r_arm_color, 3)
    cv2.line(frame, landmarks[8], landmarks[10], r_arm_color, 3)
    cv2.line(frame, landmarks[6], landmarks[12], r_torso_color, 3)
    cv2.line(frame, landmarks[12], landmarks[14], r_torso_color, 3)

def run_pushup_session():
    st.markdown("## 💪 Push-up Session")
    st.info("🔄 Live camera will open below. Click **Stop Pushup Session** to end.")

    stop_button = st.button("🛑 Stop Pushup Session")
    frame_window = st.empty()

    model_path = Path(__file__).resolve().parent.parent / "models" / "movenet.tflite"
    detector = PoseEstimator(str(model_path))

    cap = cv2.VideoCapture(0)
    count, score, stage = 0, 0, None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or stop_button:
            break

        landmarks = detector.detect(frame)
        if landmarks and len(landmarks) >= 15:
            # Left side
            l_shoulder = landmarks[5]
            l_elbow = landmarks[7]
            l_wrist = landmarks[9]
            l_hip = landmarks[11]
            l_knee = landmarks[13]

            # Right side
            r_shoulder = landmarks[6]
            r_elbow = landmarks[8]
            r_wrist = landmarks[10]
            r_hip = landmarks[12]
            r_knee = landmarks[14]

            # Calculate angles
            l_angle = calculate_angle(l_shoulder, l_elbow, l_wrist)
            l_hip_angle = calculate_angle(l_shoulder, l_hip, l_knee)

            r_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)
            r_hip_angle = calculate_angle(r_shoulder, r_hip, r_knee)

            # Push-up logic (use average of both arms for stability)
            avg_arm_angle = (l_angle + r_angle) / 2

            if avg_arm_angle > 160:
                stage = "down"
            elif avg_arm_angle < 90 and stage == "down":
                stage = "up"
                count += 1

            # Scoring (simple average logic)
            if l_angle < 100 and r_angle < 100 and l_hip_angle > 150 and r_hip_angle > 150:
                score = 100
            elif (l_angle < 100 and r_angle < 100):
                score = 70
            else:
                score = 30

            draw_pushup_pose(frame, landmarks, l_angle, l_hip_angle, r_angle, r_hip_angle)

            # Overlay metrics
            cv2.putText(frame, f'Push-ups: {count}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(frame, f'Pose Score: {score}', (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame, channels="RGB")

    cap.release()
    cv2.destroyAllWindows()
    st.success(f"🏁 Session ended! Total Push-ups: {count}")

__all__ = ['run_pushup_session']