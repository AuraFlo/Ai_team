import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import ImageFont, ImageDraw, Image
import time
from collections import deque

movenet = hub.load("https://tfhub.dev/google/movenet/singlepose/thunder/4")

def put_text_hindi(frame, text, position, font_size=22, color=(0, 255, 255)):
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/Nirmala.ttf", font_size)
    except:
        font = ImageFont.load_default()
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)
    draw.text(position, text, font=font, fill=color)
    return np.array(img_pil)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def detect_pose(frame):
    img = cv2.resize(frame, (256, 256))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    input_img = tf.expand_dims(img, axis=0)
    input_img = tf.cast(input_img, dtype=tf.int32)
    outputs = movenet.signatures['serving_default'](input_img)
    keypoints = outputs['output_0'].numpy().reshape((1, 17, 3))
    return keypoints

EDGES = {
    (0,1), (0,2), (1,3), (2,4),
    (0,5), (0,6), (5,7), (7,9), (6,8), (8,10),
    (5,6), (5,11), (6,12),
    (11,12), (11,13), (13,15), (12,14), (14,16)
}

def draw_skeleton(frame, keypoints, confidence_threshold=0.3, color=(0,255,0)):
    h, w, _ = frame.shape
    for kp in keypoints:
        y, x, c = kp
        if c > confidence_threshold:
            cx, cy = int(x * w), int(y * h)
            cv2.circle(frame, (cx, cy), 4, color, -1)
    for p1, p2 in EDGES:
        y1, x1, c1 = keypoints[p1]
        y2, x2, c2 = keypoints[p2]
        if c1 > confidence_threshold and c2 > confidence_threshold:
            x1, y1 = int(x1 * w), int(y1 * h)
            x2, y2 = int(x2 * w), int(y2 * h)
            cv2.line(frame, (x1, y1), (x2, y2), color, 2)
    return frame

counter = 0
stage = None
last_rep_score = 0
last_rep_time = 0

down_frames_required = 3
up_frames_required   = 3
cooldown_time = 0.6

knee_history = deque(maxlen=5)
elbow_history = deque(maxlen=5)
torso_history = deque(maxlen=5)

elbow_min, elbow_max = 150, 180
torso_min, torso_max = 80, 100
knee_min, knee_max   = 80, 100

down_counter = 0
up_counter   = 0

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    keypoints = detect_pose(frame)
    landmarks = keypoints[0, :, :]
    h, w, _ = frame.shape

    left_hip   = (landmarks[11][1] * w, landmarks[11][0] * h)
    left_knee  = (landmarks[13][1] * w, landmarks[13][0] * h)
    left_ankle = (landmarks[15][1] * w, landmarks[15][0] * h)
    left_shoulder = (landmarks[5][1] * w, landmarks[5][0] * h)
    left_elbow    = (landmarks[7][1] * w, landmarks[7][0] * h)
    left_wrist    = (landmarks[9][1] * w, landmarks[9][0] * h)
    left_ear      = (landmarks[3][1] * w, landmarks[3][0] * h)

    knee_angle  = calculate_angle(left_hip, left_knee, left_ankle)
    elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    torso_angle = calculate_angle(left_hip, left_shoulder, left_ear)

    knee_history.append(knee_angle)
    elbow_history.append(elbow_angle)
    torso_history.append(torso_angle)

    knee_angle  = np.mean(knee_history)
    elbow_angle = np.mean(elbow_history)
    torso_angle = np.mean(torso_history)

    score = 100
    if not (elbow_min <= elbow_angle <= elbow_max): score -= 30
    if not (torso_min <= torso_angle <= torso_max): score -= 30
    if not (knee_min <= knee_angle <= knee_max): score -= 40

    current_time = time.time()
    if knee_angle > 150:
        up_counter += 1
        down_counter = 0
        if up_counter >= up_frames_required:
            stage = "up"
    elif knee_angle < 100:
        down_counter += 1
        up_counter = 0
        if stage == "up" and down_counter >= down_frames_required and (current_time - last_rep_time > cooldown_time):
            stage = "down"
            counter += 1
            last_rep_score = score
            last_rep_time = current_time

    color = (0,255,0) if score >= 70 else (0,0,255)
    frame = draw_skeleton(frame, landmarks, color=color)

    panel_width = 350
    panel = np.zeros((frame.shape[0], panel_width, 3), dtype=np.uint8)

    cv2.putText(panel, "Instructions:", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.putText(panel, "- Keep back straight", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(panel, "- Bend knee ~90 deg", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
    cv2.putText(panel, "- Do controlled reps", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    panel = put_text_hindi(panel, "Nirdesh:", (20, 200), font_size=22, color=(0,255,255))
    panel = put_text_hindi(panel, "- Seedhe khade raho", (20, 230), font_size=20, color=(255,255,255))
    panel = put_text_hindi(panel, "- Ghutna 90 deg par modho", (20, 260), font_size=20, color=(255,255,255))
    panel = put_text_hindi(panel, "- Control ke sath rep karo", (20, 290), font_size=20, color=(255,255,255))

    cv2.putText(panel, f"Reps: {counter}", (20, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
    cv2.putText(panel, f"Last Score: {last_rep_score}", (20, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

    combined = np.hstack((frame, panel))

    cv2.imshow("Lunge Detector with Panel", combined)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
