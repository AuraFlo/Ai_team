import os
import cv2
import math
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import ImageFont, ImageDraw, Image

MODEL_HANDLE = "https://tfhub.dev/google/movenet/singlepose/lightning/4"
INPUT_RES = 192
MIN_CONF = 0.2
ANGLE_SMOOTH_DEG = 1.0
FULL_TURN_DEG = 300.0
ELBOW_STRAIGHT_MIN = 150
RADIUS_RATIO_MIN = 0.75
FONT_SIZE = 26
REP_SCORE_THRESHOLD = 75

print("Loading MoveNet…")
movenet = hub.load(MODEL_HANDLE).signatures["serving_default"]

COCO_KP = {
    "nose":0, "left_eye":1, "right_eye":2, "left_ear":3, "right_ear":4,
    "left_shoulder":5, "right_shoulder":6, "left_elbow":7, "right_elbow":8,
    "left_wrist":9, "right_wrist":10, "left_hip":11, "right_hip":12,
    "left_knee":13, "right_knee":14, "left_ankle":15, "right_ankle":16
}

SKELETON = [
    (5,6), (5,7), (7,9), (6,8), (8,10),
    (5,11), (6,12), (11,12),
    (11,13), (13,15), (12,14), (14,16),
    (0,1), (0,2), (1,3), (2,4)
]

def detect_keypoints_both(frame_bgr):
    img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    inp = tf.image.resize_with_pad(tf.expand_dims(img_rgb, 0), INPUT_RES, INPUT_RES)
    inp = tf.cast(inp, dtype=tf.int32)
    out = movenet(inp)
    kps = out["output_0"].numpy()[0, 0, :, :]
    return kps

def to_pixels(kps_norm, w, h):
    xy = np.zeros((17,3), dtype=np.float32)
    xy[:,0] = kps_norm[:,1] * w
    xy[:,1] = kps_norm[:,0] * h
    xy[:,2] = kps_norm[:,2]
    return xy

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ang = math.degrees(
        math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
    )
    ang = abs(ang)
    if ang > 180:
        ang = 360 - ang
    return ang

def polar_angle_deg(origin, point):
    dy = point[1] - origin[1]
    dx = point[0] - origin[0]
    ang = math.degrees(math.atan2(dy, dx))
    if ang < 0:
        ang += 360
    return ang

def ang_delta(a, b):
    d = b - a
    if d > 180: d -= 360
    if d <= -180: d += 360
    return d

def line(frame, p, q, color, thick=3):
    cv2.line(frame, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, thick)

def circ(frame, p, color, r=5):
    cv2.circle(frame, (int(p[0]), int(p[1])), r, color, -1)

class ArmState:
    def __init__(self):
        self.last_angle = None
        self.direction = 0
        self.cum = 0.0
        self.reps = 0
        self.last_rep_score = 0

def get_color(state: ArmState):
    return (0, 255, 0) if state.last_rep_score >= REP_SCORE_THRESHOLD else (0, 0, 255)

right_state = ArmState()
left_state  = ArmState()

def update_arm_circle(state: ArmState, shoulder, elbow, wrist):
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    arm_len = np.linalg.norm(np.array(shoulder) - np.array(elbow)) + \
              np.linalg.norm(np.array(elbow) - np.array(wrist))
    radius = np.linalg.norm(np.array(wrist) - np.array(shoulder))
    radius_ratio = 0 if arm_len < 1e-3 else (radius / arm_len)

    ang = polar_angle_deg(shoulder, wrist)

    if state.last_angle is None:
        state.last_angle = ang
        score = max(0, 100 - max(0, (ELBOW_STRAIGHT_MIN - elbow_angle))*0.8
                         - max(0, (RADIUS_RATIO_MIN - radius_ratio)/RADIUS_RATIO_MIN)*40)
        return ang, elbow_angle, radius_ratio, "Init", int(score)

    d = ang_delta(state.last_angle, ang)
    if abs(d) < ANGLE_SMOOTH_DEG:
        d = 0.0

    if d != 0:
        s = 1 if d > 0 else -1
        if state.direction == 0:
            state.direction = s
        elif s != state.direction and abs(d) > 10:
            state.direction = s
            state.cum = 0.0

    state.cum += abs(d)
    state.last_angle = ang

    status = "Good"
    if elbow_angle < ELBOW_STRAIGHT_MIN:
        status = "Elbow Bent"
    if radius_ratio < RADIUS_RATIO_MIN:
        status = "Short Radius" if status == "Good" else status + " + Short Radius"

    score = max(0, 100 - max(0, (ELBOW_STRAIGHT_MIN - elbow_angle))*0.8
                      - max(0, (RADIUS_RATIO_MIN - radius_ratio)/RADIUS_RATIO_MIN)*40)

    if state.cum >= FULL_TURN_DEG and elbow_angle >= ELBOW_STRAIGHT_MIN and radius_ratio >= RADIUS_RATIO_MIN:
        state.reps += 1
        state.last_rep_score = int(score)
        state.cum = 0.0

    return ang, elbow_angle, radius_ratio, status, int(score)

cap = cv2.VideoCapture(0)
cv2.namedWindow("Arm Circles", cv2.WINDOW_NORMAL)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    h, w = frame.shape[:2]
    kps_norm = detect_keypoints_both(frame)
    kps = to_pixels(kps_norm, w, h)

    def ok_j(*idxs):
        return all(kps[i,2] >= MIN_CONF for i in idxs)

    if ok_j(COCO_KP["right_shoulder"], COCO_KP["right_elbow"], COCO_KP["right_wrist"]):
        rs = kps[COCO_KP["right_shoulder"], :2]
        re = kps[COCO_KP["right_elbow"], :2]
        rw = kps[COCO_KP["right_wrist"], :2]

        r_ang, r_elbow, r_rad, r_status, r_score = update_arm_circle(right_state, rs, re, rw)
        col = get_color(right_state)

        line(frame, rs, re, col, 5)
        line(frame, re, rw, col, 5)
        circ(frame, rs, col, 6)
        circ(frame, re, col, 6)
        circ(frame, rw, col, 6)

        cv2.putText(frame, f"Right Reps: {right_state.reps}  Last Score: {right_state.last_rep_score}",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 2)

    if ok_j(COCO_KP["left_shoulder"], COCO_KP["left_elbow"], COCO_KP["left_wrist"]):
        ls = kps[COCO_KP["left_shoulder"], :2]
        le = kps[COCO_KP["left_elbow"], :2]
        lw = kps[COCO_KP["left_wrist"], :2]

        l_ang, l_elbow, l_rad, l_status, l_score = update_arm_circle(left_state, ls, le, lw)
        col = get_color(left_state)

        line(frame, ls, le, col, 5)
        line(frame, le, lw, col, 5)
        circ(frame, ls, col, 6)
        circ(frame, le, col, 6)
        circ(frame, lw, col, 6)

        cv2.putText(frame, f"Left Reps: {left_state.reps}  Last Score: {left_state.last_rep_score}",
                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 2)

    cv2.putText(frame, "Instructions: Stand straight, extend arms, draw big circles.",
                (20, h-40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Arm Circles", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
