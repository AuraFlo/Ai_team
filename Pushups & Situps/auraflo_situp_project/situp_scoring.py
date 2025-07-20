# import cv2
# import mediapipe as mp
# import numpy as np
# from ideal_situp_pose import ideal_situp_pose

# mp_pose = mp.solutions.pose
# mp_drawing = mp.solutions.drawing_utils

# def calculate_angle(a, b, c):
#     a, b, c = np.array(a), np.array(b), np.array(c)
#     radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     angle = np.abs(radians*180.0/np.pi)
#     return 360 - angle if angle > 180 else angle

# cap = cv2.VideoCapture(0)

# situp_count = 0
# stage = None
# score = 0

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frame = cv2.flip(frame, 1)
#         h, w, _ = frame.shape
#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False

#         results = pose.process(image)

#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         try:
#             landmarks = results.pose_landmarks.landmark

#             # Get coordinates
#             shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
#                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
#             hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
#                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
#             ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x * w,
#                    landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y * h]

#             torso_angle = calculate_angle(ear, shoulder, hip)

#             # Feedback
#             color = (0, 255, 0) if abs(torso_angle - ideal_situp_pose["up_torso_angle"]) < ideal_situp_pose["angle_tolerance"] else (0, 0, 255)

#             # Count sit-ups
#             if torso_angle > ideal_situp_pose["down_torso_angle"] - ideal_situp_pose["angle_tolerance"]:
#                 stage = "down"
#             if torso_angle < ideal_situp_pose["up_torso_angle"] + ideal_situp_pose["angle_tolerance"] and stage == "down":
#                 stage = "up"
#                 situp_count += 1
#                 score += max(0, 100 - abs(torso_angle - ideal_situp_pose["up_torso_angle"]))

#             # Visuals
#             cv2.putText(image, f'Sit-Ups: {situp_count}', (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
#             cv2.putText(image, f'Score: {score}', (10, 70),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#             # Color-coded feedback point
#             cv2.circle(image, tuple(np.int32(shoulder)), 10, color, -1)

#         except:
#             pass

#         # Draw pose
#         mp_drawing.draw_landmarks(
#             image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

#         cv2.imshow('Sit-Up Tracker', image)

#         if cv2.waitKey(10) & 0xFF == ord('q'):
#             break

# cap.release()
# cv2.destroyAllWindows()






# import cv2
# import mediapipe as mp
# import math
# from ideal_situp_pose import ideal_situp_pose

# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose

# def calculate_angle(a, b, c):
#     ba = [a[0] - b[0], a[1] - b[1]]
#     bc = [c[0] - b[0], c[1] - b[1]]
#     cosine_angle = (ba[0]*bc[0] + ba[1]*bc[1]) / (
#         math.sqrt(ba[0]**2 + ba[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2)
#     )
#     return math.degrees(math.acos(min(1, max(cosine_angle, -1))))

# def get_coordinates(landmark, shape):
#     return int(landmark.x * shape[1]), int(landmark.y * shape[0])

# # 🧠 Open both webcam and instructional video
# webcam = cv2.VideoCapture(0)
# reference_video = cv2.VideoCapture('correct_pose.mp4')

# situp_count = 0
# stage = None

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while webcam.isOpened():
#         ret, frame = webcam.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)
#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False
#         results = pose.process(image)
#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         shape = image.shape
#         feedback_color = (0, 0, 255)

#         if results.pose_landmarks:
#             landmarks = results.pose_landmarks.landmark

#             ear = get_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_EAR], shape)
#             shoulder = get_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER], shape)
#             hip = get_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_HIP], shape)

#             torso_angle = calculate_angle(ear, shoulder, hip)
#             tolerance = ideal_situp_pose["tolerance"]
#             ideal_angle = ideal_situp_pose["torso_angle"]

#             if abs(torso_angle - ideal_angle) <= tolerance:
#                 feedback_color = (0, 255, 0)

#             if torso_angle > (ideal_angle + tolerance):
#                 stage = "down"
#             if torso_angle < (ideal_angle - tolerance) and stage == "down":
#                 stage = "up"
#                 situp_count += 1

#             cv2.putText(image, f"Angle: {int(torso_angle)}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, feedback_color, 2)
#             cv2.putText(image, f"Sit-ups: {situp_count}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

#             cv2.line(image, ear, shoulder, feedback_color, 3)
#             cv2.line(image, shoulder, hip, feedback_color, 3)

#             mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
#                                       mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
#                                       mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))

#         # 🖼️ Read one frame from instructional video
#         ref_ret, ref_frame = reference_video.read()
#         if not ref_ret:
#             reference_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             ref_ret, ref_frame = reference_video.read()

#         ref_frame = cv2.resize(ref_frame, (image.shape[1], image.shape[0]))

#         # 🪞 Side-by-side view
#         combined = cv2.hconcat([image, ref_frame])
#         cv2.imshow("Sit-Up Counter + Reference", combined)

#         if cv2.waitKey(10) & 0xFF == ord('q'):
#             break

# webcam.release()
# reference_video.release()
# cv2.destroyAllWindows()
















# # File: situp_scoring.py
# import cv2
# import mediapipe as mp
# import math
# import numpy as np

# # Ideal sit-up pose configuration
# ideal_situp_pose = {
#     "torso_angle": 50,      # Ideal angle between ear-shoulder-hip
#     "tolerance": 15,        # Tolerance for full score
#     "partial_tolerance": 25 # Wider tolerance for partial score
# }

# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose

# def calculate_angle(a, b, c):
#     ba = [a[0] - b[0], a[1] - b[1]]
#     bc = [c[0] - b[0], c[1] - b[1]]
#     cosine_angle = (ba[0]*bc[0] + ba[1]*bc[1]) / (
#         math.sqrt(ba[0]**2 + ba[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2) + 1e-6
#     )
#     return math.degrees(math.acos(np.clip(cosine_angle, -1.0, 1.0)))

# def get_coordinates(landmark, shape):
#     return int(landmark.x * shape[1]), int(landmark.y * shape[0])

# cap = cv2.VideoCapture(0)
# pose_video = cv2.VideoCapture("pose_reference.mp4")  # Ideal form video

# score = 0
# stage = None

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         frame = cv2.flip(frame, 1)
#         shape = frame.shape

#         # === Read Reference Video Frame ===
#         ret2, ref_frame = pose_video.read()
#         if not ret2:
#             pose_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             ret2, ref_frame = pose_video.read()

#         ref_frame = cv2.resize(ref_frame, (200, 150))

#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False
#         results = pose.process(image)
#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         feedback_color = (0, 0, 255)  # Red by default

#         if results.pose_landmarks:
#             lm = results.pose_landmarks.landmark

#             ear = get_coordinates(lm[mp_pose.PoseLandmark.LEFT_EAR], shape)
#             shoulder = get_coordinates(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], shape)
#             hip = get_coordinates(lm[mp_pose.PoseLandmark.LEFT_HIP], shape)

#             torso_angle = calculate_angle(ear, shoulder, hip)

#             # Compare angle to ideal
#             ideal = ideal_situp_pose["torso_angle"]
#             tol = ideal_situp_pose["tolerance"]
#             partial = ideal_situp_pose["partial_tolerance"]

#             if abs(torso_angle - ideal) <= tol:
#                 feedback_color = (0, 255, 0)
#                 if stage == "down":
#                     score += 1
#                     stage = "up"
#             elif abs(torso_angle - ideal) <= partial:
#                 feedback_color = (0, 165, 255)  # Orange for partial
#                 if stage == "down":
#                     score += 0.5
#                     stage = "up"
#             else:
#                 if stage == "up":
#                     score = max(0, score - 0.2)
#                     stage = "down"

#             # Draw feedback lines
#             cv2.line(image, ear, shoulder, feedback_color, 3)
#             cv2.line(image, shoulder, hip, feedback_color, 3)

#             # Draw landmarks
#             mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

#             # Show angle
#             cv2.putText(image, f"Torso Angle: {int(torso_angle)}", (20, 60),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, feedback_color, 2)

#         # === Score Display ===
#         cv2.putText(image, f"Sit-up Score: {round(score, 1)}", (20, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3)

#         # === Display Reference Video Frame ===
#         image[10:160, shape[1]-210:shape[1]-10] = ref_frame

#         cv2.imshow("Sit-Up Scoring System", image)
#         if cv2.waitKey(10) & 0xFF == ord('q'):
#             break

# cap.release()
# pose_video.release()
# cv2.destroyAllWindows()































# import cv2
# import mediapipe as mp
# import numpy as np
# import json
# import math

# # Load ideal pose angles from JSON
# with open('ideal_pose.json', 'r') as f:
#     ideal_pose_data = json.load(f)

# ideal_angles = ideal_pose_data['angles']
# tolerance = ideal_pose_data['tolerance']

# # MediaPipe setup
# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose

# # Angle calculation
# def calculate_angle(a, b, c):
#     a = np.array(a)
#     b = np.array(b)
#     c = np.array(c)

#     radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     angle = np.abs(radians * 180.0 / np.pi)

#     if angle > 180.0:
#         angle = 360 - angle
#     return angle

# # Evaluate user's pose
# def evaluate_pose(landmarks, width, height):
#     if not landmarks:
#         return {}, {}

#     joints = {
#         'left_elbow': [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
#                        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
#                        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]],
#         'right_elbow': [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
#                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
#                         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]],
#         'left_knee': [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
#                       landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
#                       landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]],
#         'right_knee': [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
#                        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
#                        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]]
#     }

#     angles = {}
#     feedback = {}

#     for joint, points in joints.items():
#         a = [int(points[0].x * width), int(points[0].y * height)]
#         b = [int(points[1].x * width), int(points[1].y * height)]
#         c = [int(points[2].x * width), int(points[2].y * height)]

#         angle = calculate_angle(a, b, c)
#         angles[joint] = angle

#         ideal = ideal_angles[joint]
#         tol = tolerance[joint]

#         if abs(angle - ideal) <= tol:
#             feedback[joint] = 'green'
#         elif abs(angle - ideal) <= tol * 1.5:
#             feedback[joint] = 'yellow'
#         else:
#             feedback[joint] = 'red'

#     return angles, feedback

# # Draw lines with color based on correctness
# def draw_colored_lines(image, landmarks, feedback, width, height):
#     joint_connections = {
#         'left_elbow': (mp_pose.PoseLandmark.LEFT_SHOULDER.value,
#                        mp_pose.PoseLandmark.LEFT_ELBOW.value,
#                        mp_pose.PoseLandmark.LEFT_WRIST.value),
#         'right_elbow': (mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
#                         mp_pose.PoseLandmark.RIGHT_ELBOW.value,
#                         mp_pose.PoseLandmark.RIGHT_WRIST.value),
#         'left_knee': (mp_pose.PoseLandmark.LEFT_HIP.value,
#                       mp_pose.PoseLandmark.LEFT_KNEE.value,
#                       mp_pose.PoseLandmark.LEFT_ANKLE.value),
#         'right_knee': (mp_pose.PoseLandmark.RIGHT_HIP.value,
#                        mp_pose.PoseLandmark.RIGHT_KNEE.value,
#                        mp_pose.PoseLandmark.RIGHT_ANKLE.value)
#     }

#     for joint, connection in joint_connections.items():
#         a = landmarks[connection[0]]
#         b = landmarks[connection[1]]
#         c = landmarks[connection[2]]

#         points = [a, b, c]
#         color = (0, 0, 255)  # Red

#         if feedback.get(joint) == 'green':
#             color = (0, 255, 0)
#         elif feedback.get(joint) == 'yellow':
#             color = (0, 255, 255)

#         for i in range(len(points) - 1):
#             pt1 = int(points[i].x * width), int(points[i].y * height)
#             pt2 = int(points[i + 1].x * width), int(points[i + 1].y * height)
#             cv2.line(image, pt1, pt2, color, 3)

# # Setup camera and reference video
# cap = cv2.VideoCapture(0)
# pose_video = cv2.VideoCapture("pose_reference.mp4")

# score = 0

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Rotate sideways camera upright
#         frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
#         frame = cv2.resize(frame, (640, 480))

#         # Read and resize reference video
#         ref_ret, ref_frame = pose_video.read()
#         if not ref_ret or ref_frame is None:
#             pose_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             ref_ret, ref_frame = pose_video.read()

#         if ref_ret and ref_frame is not None:
#             ref_frame = cv2.resize(ref_frame, (640, 480))
#         else:
#             ref_frame = np.zeros((480, 640, 3), dtype=np.uint8)

#         # Process live camera frame
#         img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = pose.process(img_rgb)

#         if results.pose_landmarks:
#             mp_drawing.draw_landmarks(
#                 frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

#             landmarks = results.pose_landmarks.landmark
#             angles, feedback = evaluate_pose(landmarks, frame.shape[1], frame.shape[0])
#             draw_colored_lines(frame, landmarks, feedback, frame.shape[1], frame.shape[0])

#             if feedback:
#                 greens = list(feedback.values()).count('green')
#                 yellows = list(feedback.values()).count('yellow')

#                 if greens >= 3:
#                     score += 1
#                 elif yellows >= 2:
#                     score += 0.5
#                 else:
#                     score = max(score - 0.5, 0)

#         # Combine both frames horizontally
#         combined = cv2.hconcat([frame, ref_frame])
#         cv2.putText(combined, f"Sit-up Score: {score:.1f}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX,
#                     1.2, (255, 255, 255), 3)

#         cv2.imshow("Live (Left) vs Reference (Right)", combined)

#         if cv2.waitKey(10) & 0xFF == ord('q'):
#             break

# cap.release()
# pose_video.release()
# cv2.destroyAllWindows()\
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# import cv2
# import mediapipe as mp
# import numpy as np
# import json

# # Load ideal angles and tolerance
# with open("ideal_pose.json") as f:
#     ideal_pose = json.load(f)

# ideal_angles = ideal_pose["angles"]
# tolerance = ideal_pose["tolerance"]

# # MediaPipe setup
# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose

# cap = cv2.VideoCapture(0)
# ref_video = cv2.VideoCapture("pose_reference.mp4")

# def calculate_angle(a, b, c):
#     """Calculates angle between three points."""
#     a = np.array(a)
#     b = np.array(b)
#     c = np.array(c)

#     radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     angle = np.abs(radians * 180.0 / np.pi)

#     if angle > 180:
#         angle = 360 - angle

#     return angle

# def get_landmark_coords(landmarks, frame_width, frame_height, indices):
#     return [(int(landmarks[i].x * frame_width), int(landmarks[i].y * frame_height)) for i in indices]

# # Rep counting state
# state = "down"
# rep_count = 0

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         ref_ret, ref_frame = ref_video.read()

#         if not ret:
#             print("Camera frame missing!")
#             break

#         if not ref_ret:
#             ref_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             ref_ret, ref_frame = ref_video.read()

#         # Flip the frame horizontally
#         frame = cv2.flip(frame, 1)

#         # Resize ref video to match height
#         frame_height, frame_width = frame.shape[:2]
#         ref_frame = cv2.resize(ref_frame, (frame_width // 2, frame_height))

#         # Convert image to RGB
#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False
#         results = pose.process(image)

#         # Restore image to BGR
#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         if results.pose_landmarks:
#             h, w, _ = image.shape
#             lm = results.pose_landmarks.landmark

#             # Get joint coordinates
#             joints = {
#                 "left_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [11, 13, 15])),
#                 "right_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [12, 14, 16])),
#                 "left_knee": calculate_angle(*get_landmark_coords(lm, w, h, [23, 25, 27])),
#                 "right_knee": calculate_angle(*get_landmark_coords(lm, w, h, [24, 26, 28])),
#             }

#             # Draw feedback lines
#             for joint, angle in joints.items():
#                 expected = ideal_angles[joint]
#                 tol = tolerance[joint]
#                 within_range = abs(angle - expected) <= tol

#                 # Choose color
#                 color = (0, 255, 0) if within_range else (0, 0, 255)

#                 # Draw line for knees and elbows
#                 if "left" in joint:
#                     i1, i2, i3 = [11, 13, 15] if "elbow" in joint else [23, 25, 27]
#                 else:
#                     i1, i2, i3 = [12, 14, 16] if "elbow" in joint else [24, 26, 28]

#                 pts = get_landmark_coords(lm, w, h, [i1, i2, i3])
#                 cv2.line(image, pts[0], pts[1], color, 3)
#                 cv2.line(image, pts[1], pts[2], color, 3)
#                 cv2.circle(image, pts[1], 5, color, -1)

#             # Sit-up logic based on knee or torso angle
#             knee_angle = (joints["left_knee"] + joints["right_knee"]) / 2
#             if knee_angle < 100:
#                 if state == "down":
#                     state = "up"
#                     rep_count += 1
#             elif knee_angle > 130:
#                 if state == "up":
#                     state = "down"

#             # Show rep count
#             cv2.putText(image, f"Sit-Ups: {rep_count}", (50, 80),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

#         # Combine frame and reference horizontally
#         combined = np.hstack((ref_frame, cv2.resize(image, (frame.shape[1], frame.shape[0]))))

#         cv2.imshow("Sit-Up Feedback", combined)

#         if cv2.waitKey(5) & 0xFF == 27:  # ESC key
#             break

# cap.release()
# ref_video.release()
# cv2.destroyAllWindows()























# import cv2
# import mediapipe as mp
# import numpy as np
# import json

# # Load ideal angles and tolerance
# with open("ideal_pose.json") as f:
#     ideal_pose = json.load(f)

# ideal_angles = ideal_pose["angles"]
# tolerance = ideal_pose["tolerance"]

# # MediaPipe setup
# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose

# cap = cv2.VideoCapture(0)
# ref_video = cv2.VideoCapture("pose_reference.mp4")

# def calculate_angle(a, b, c):
#     """Calculates angle between three points."""
#     a = np.array(a)
#     b = np.array(b)
#     c = np.array(c)

#     radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     angle = np.abs(radians * 180.0 / np.pi)

#     if angle > 180:
#         angle = 360 - angle

#     return angle

# def get_landmark_coords(landmarks, frame_width, frame_height, indices):
#     return [(int(landmarks[i].x * frame_width), int(landmarks[i].y * frame_height)) for i in indices]

# # Rep counting and score
# state = "down"
# rep_count = 0
# score = 0

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         ref_ret, ref_frame = ref_video.read()

#         if not ret:
#             print("Camera frame missing!")
#             break

#         if not ref_ret:
#             ref_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             ref_ret, ref_frame = ref_video.read()

#         frame = cv2.flip(frame, 1)

#         # Resize reference video
#         frame_height, frame_width = frame.shape[:2]
#         ref_frame = cv2.resize(ref_frame, (frame_width // 2, frame_height))

#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False
#         results = pose.process(image)
#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         if results.pose_landmarks:
#             h, w, _ = image.shape
#             lm = results.pose_landmarks.landmark

#             joints = {
#                 "left_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [11, 13, 15])),
#                 "right_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [12, 14, 16])),
#                 "left_knee": calculate_angle(*get_landmark_coords(lm, w, h, [23, 25, 27])),
#                 "right_knee": calculate_angle(*get_landmark_coords(lm, w, h, [24, 26, 28])),
#             }

#             correct_joints = 0

#             for joint, angle in joints.items():
#                 expected = ideal_angles[joint]
#                 tol = tolerance[joint]
#                 within_range = abs(angle - expected) <= tol
#                 if within_range:
#                     correct_joints += 1

#                 color = (0, 255, 0) if within_range else (0, 0, 255)

#                 if "left" in joint:
#                     i1, i2, i3 = [11, 13, 15] if "elbow" in joint else [23, 25, 27]
#                 else:
#                     i1, i2, i3 = [12, 14, 16] if "elbow" in joint else [24, 26, 28]

#                 pts = get_landmark_coords(lm, w, h, [i1, i2, i3])
#                 cv2.line(image, pts[0], pts[1], color, 3)
#                 cv2.line(image, pts[1], pts[2], color, 3)
#                 cv2.circle(image, pts[1], 5, color, -1)

#             # Score logic
#             score = int((correct_joints / len(joints)) * 100)

#             # Sit-up logic based on knee angle
#             knee_angle = (joints["left_knee"] + joints["right_knee"]) / 2
#             if knee_angle < 100:
#                 if state == "down":
#                     state = "up"
#                     rep_count += 1
#             elif knee_angle > 130:
#                 if state == "up":
#                     state = "down"

#             # Show rep count and score
#             cv2.putText(image, f"Sit-Ups: {rep_count}", (50, 80),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
#             cv2.putText(image, f"Score: {score}%", (50, 140),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

#         combined = np.hstack((ref_frame, cv2.resize(image, (frame.shape[1], frame.shape[0]))))
#         cv2.imshow("Sit-Up Feedback", combined)

#         if cv2.waitKey(5) & 0xFF == 27:
#             break

# cap.release()
# ref_video.release()
# cv2.destroyAllWindows()







# import cv2
# import mediapipe as mp
# import numpy as np
# import json

# # Load ideal angles and tolerance
# with open("ideal_pose.json") as f:
#     ideal_pose = json.load(f)

# ideal_angles = ideal_pose["angles"]
# tolerance = ideal_pose["tolerance"]

# # MediaPipe setup
# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose

# cap = cv2.VideoCapture(0)
# ref_video = cv2.VideoCapture("pose_reference.mp4")

# def calculate_angle(a, b, c):
#     a, b, c = np.array(a), np.array(b), np.array(c)
#     radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     angle = np.abs(radians * 180.0 / np.pi)
#     return 360 - angle if angle > 180 else angle

# def get_landmark_coords(landmarks, frame_width, frame_height, indices):
#     return [(int(landmarks[i].x * frame_width), int(landmarks[i].y * frame_height)) for i in indices]

# # Tracking state
# rep_count = 0
# score = 0
# state = "down"

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         ref_ret, ref_frame = ref_video.read()

#         if not ret:
#             print("Camera frame missing!")
#             break

#         if not ref_ret:
#             ref_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
#             ref_ret, ref_frame = ref_video.read()

#         # Flip camera and resize
#         frame = cv2.flip(frame, 1)
#         frame_height, frame_width = frame.shape[:2]
#         ref_frame = cv2.resize(ref_frame, (frame_width // 2, frame_height))

#         # Pose estimation
#         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False
#         results = pose.process(image)
#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         frame_score = 0
#         max_score = len(ideal_angles)  # 4 joints

#         if results.pose_landmarks:
#             h, w = image.shape[:2]
#             lm = results.pose_landmarks.landmark

#             # Get joint angles
#             joints = {
#                 "left_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [11, 13, 15])),
#                 "right_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [12, 14, 16])),
#                 "left_knee": calculate_angle(*get_landmark_coords(lm, w, h, [23, 25, 27])),
#                 "right_knee": calculate_angle(*get_landmark_coords(lm, w, h, [24, 26, 28])),
#             }

#             for joint, angle in joints.items():
#                 expected = ideal_angles[joint]
#                 tol = tolerance[joint]
#                 within_range = abs(angle - expected) <= tol
#                 color = (0, 255, 0) if within_range else (0, 0, 255)

#                 if within_range:
#                     frame_score += 1

#                 # Get points to draw
#                 if "left" in joint:
#                     i1, i2, i3 = [11, 13, 15] if "elbow" in joint else [23, 25, 27]
#                 else:
#                     i1, i2, i3 = [12, 14, 16] if "elbow" in joint else [24, 26, 28]

#                 pts = get_landmark_coords(lm, w, h, [i1, i2, i3])
#                 cv2.line(image, pts[0], pts[1], color, 3)
#                 cv2.line(image, pts[1], pts[2], color, 3)
#                 cv2.circle(image, pts[1], 6, color, -1)

#             # Sit-up detection logic (based on average knee angle)
#             knee_angle = (joints["left_knee"] + joints["right_knee"]) / 2
#             if knee_angle < 100 and state == "down":
#                 state = "up"
#                 rep_count += 1
#             elif knee_angle > 130 and state == "up":
#                 state = "down"

#             # Add score based on joints
#             score += int((frame_score / max_score) * 100) // 10  # Increment score with partial correctness

#         # Overlay info
#         cv2.putText(image, f"Sit-Ups: {rep_count}", (50, 70),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 3)
#         cv2.putText(image, f"Pose Score: {score}", (50, 120),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

#         # Combine webcam + reference
#         image = cv2.resize(image, (frame_width, frame_height))
#         combined = np.hstack((ref_frame, image))
#         cv2.imshow("Sit-Up Tracker with Pose Reference", combined)

#         if cv2.waitKey(5) & 0xFF == 27:
#             break

# cap.release()
# ref_video.release()
# cv2.destroyAllWindows()

























import cv2
import mediapipe as mp
import numpy as np
import json

# Load ideal angles and tolerance
with open("ideal_pose.json") as f:
    ideal_pose = json.load(f)

ideal_angles = ideal_pose["angles"]
tolerance = ideal_pose["tolerance"]

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)
ref_video = cv2.VideoCapture("pose_reference.mp4")

def calculate_angle(a, b, c):
    """Calculates angle between three points."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

def get_landmark_coords(landmarks, w, h, indices):
    return [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in indices]

# Sit-up rep tracking
rep_count = 0
state = "down"

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        ref_ret, ref_frame = ref_video.read()

        if not ret:
            print("Webcam issue!")
            break

        if not ref_ret:
            ref_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ref_ret, ref_frame = ref_video.read()

        # Flip and resize
        frame = cv2.flip(frame, 1)
        frame_h, frame_w = frame.shape[:2]
        ref_frame = cv2.resize(ref_frame, (frame_w // 2, frame_h))

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        pose_score = 0

        if results.pose_landmarks:
            h, w = frame.shape[:2]
            lm = results.pose_landmarks.landmark

            joints = {
                "left_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [11, 13, 15])),
                "right_elbow": calculate_angle(*get_landmark_coords(lm, w, h, [12, 14, 16])),
                "left_knee": calculate_angle(*get_landmark_coords(lm, w, h, [23, 25, 27])),
                "right_knee": calculate_angle(*get_landmark_coords(lm, w, h, [24, 26, 28]))
            }

            score_sum = 0
            for joint, angle in joints.items():
                expected = ideal_angles[joint]
                tol = tolerance[joint]
                diff = abs(angle - expected)
                joint_score = max(0, 100 - (diff / tol) * 100) if diff <= tol * 2 else 0
                joint_score = min(joint_score, 100)
                score_sum += joint_score

                # Visual feedback
                color = (0, 255, 0) if diff <= tol else (0, 0, 255)
                if "left" in joint:
                    pts = get_landmark_coords(lm, w, h, [11, 13, 15] if "elbow" in joint else [23, 25, 27])
                else:
                    pts = get_landmark_coords(lm, w, h, [12, 14, 16] if "elbow" in joint else [24, 26, 28])

                cv2.line(image, pts[0], pts[1], color, 3)
                cv2.line(image, pts[1], pts[2], color, 3)
                cv2.circle(image, pts[1], 6, color, -1)

            # Average pose score
            pose_score = round(score_sum / len(joints), 1)

            # Sit-up logic based on knee angle
            avg_knee_angle = (joints["left_knee"] + joints["right_knee"]) / 2
            if avg_knee_angle < 100:
                if state == "down":
                    rep_count += 1
                    state = "up"
            elif avg_knee_angle > 130:
                if state == "up":
                    state = "down"

        # Display score and reps
        cv2.putText(image, f"Score: {pose_score:.1f}/100", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
        cv2.putText(image, f"Sit-Ups: {rep_count}", (50, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

        # Combine views
        combined = np.hstack((ref_frame, cv2.resize(image, (frame_w, frame_h))))
        cv2.imshow("Sit-Up Pose Scoring", combined)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
ref_video.release()
cv2.destroyAllWindows()