# Single side stick diagram

# import cv2
# import numpy as np
# import streamlit as st
# from pathlib import Path
# from pose_estimator import PoseEstimator
# from angles import calculate_angle

# def draw_stick_figure(frame, landmarks, angle):
#     for point in [5, 7, 9]:  # shoulder, elbow, wrist (left side)
#         cv2.circle(frame, landmarks[point], 5, (0, 255, 255), -1)

#     color = (0, 255, 0) if 40 < angle < 150 else (0, 0, 255)
#     cv2.line(frame, landmarks[5], landmarks[7], color, 2)
#     cv2.line(frame, landmarks[7], landmarks[9], color, 2)

# def run_bicep_curl_session():
#     st.markdown("## 🏋️‍♀️ Bicep Curl Session")
#     st.info("🔄 Live camera will open below. Click **Stop Bicep Curl Session** to end.")

#     stop_button = st.button("🛑 Stop Bicep Curl Session")
#     frame_window = st.empty()

#     model_path = Path(__file__).resolve().parent.parent / "models" / "movenet.tflite"
#     detector = PoseEstimator(str(model_path))

#     cap = cv2.VideoCapture(0)
#     count, stage = 0, None

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret or stop_button:
#             break

#         landmarks = detector.detect(frame)
#         if landmarks and len(landmarks) >= 10:
#             shoulder, elbow, wrist = landmarks[5], landmarks[7], landmarks[9]
#             angle = calculate_angle(shoulder, elbow, wrist)

#             if angle > 150:
#                 stage = "down"
#             elif angle < 50 and stage == "down":
#                 stage = "up"
#                 count += 1

#             draw_stick_figure(frame, landmarks, angle)

#             cv2.putText(frame, f'Curls: {count}', (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
#             cv2.putText(frame, f'Angle: {int(angle)}', (10, 60),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame_window.image(frame, channels="RGB")

#     cap.release()
#     cv2.destroyAllWindows()
#     st.success(f"🏁 Session ended! Total Bicep Curls: {count}")

# __all__ = ['run_bicep_curl_session']





# Double side stick diagram




import cv2
import numpy as np
import streamlit as st
from pathlib import Path
from pose_estimator import PoseEstimator
from angles import calculate_angle

# Draw stick figure lines with color based on form
def draw_arm(frame, landmarks, indices, angle):
    shoulder, elbow, wrist = [landmarks[i] for i in indices]

    # Draw joints
    for idx in indices:
        cv2.circle(frame, landmarks[idx], 6, (0, 255, 255), -1)

    # Color coding
    color = (0, 255, 0) if 40 < angle < 150 else (0, 0, 255)
    cv2.line(frame, shoulder, elbow, color, 3)
    cv2.line(frame, elbow, wrist, color, 3)

def run_bicep_curl_session():
    st.title("🏋️‍♂️ Bicep Curl Tracker")
    st.markdown("Track **left** and **right** arm curls using your webcam in real-time.")

    stop_button = st.button("🛑 Stop Bicep Curl Session")
    frame_window = st.empty()

    # Load model
    model_path = Path(__file__).resolve().parent.parent / "models" / "movenet.tflite"
    detector = PoseEstimator(str(model_path))

    cap = cv2.VideoCapture(0)
    right_count, left_count = 0, 0
    right_stage, left_stage = None, None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or stop_button:
            break

        landmarks = detector.detect(frame)

        if landmarks and len(landmarks) >= 12:
            # Right arm: 6 (shoulder), 8 (elbow), 10 (wrist)
            r_angle = calculate_angle(landmarks[6], landmarks[8], landmarks[10])
            draw_arm(frame, landmarks, [6, 8, 10], r_angle)

            if r_angle > 150:
                right_stage = "down"
            elif r_angle < 50 and right_stage == "down":
                right_stage = "up"
                right_count += 1

            # Left arm: 5 (shoulder), 7 (elbow), 9 (wrist)
            l_angle = calculate_angle(landmarks[5], landmarks[7], landmarks[9])
            draw_arm(frame, landmarks, [5, 7, 9], l_angle)

            if l_angle > 150:
                left_stage = "down"
            elif l_angle < 50 and left_stage == "down":
                left_stage = "up"
                left_count += 1

            # Overlay data
            cv2.putText(frame, f'Right Curls: {right_count}', (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f'Right Angle: {int(r_angle)}', (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f'Left Curls: {left_count}', (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f'Left Angle: {int(l_angle)}', (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Show frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame, channels="RGB")

    cap.release()
    cv2.destroyAllWindows()
    st.success(f"🏁 Session Ended!\n\n💪 Right Arm Curls: {right_count} | 💪 Left Arm Curls: {left_count}")

__all__ = ['run_bicep_curl_session']