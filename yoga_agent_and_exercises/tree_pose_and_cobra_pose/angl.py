import math
import numpy as np

def calculate_angle(a, b, c):
    # Points a, b, c are (x, y)
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cos_val = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cos_val = np.clip(cos_val, -1.0, 1.0)
    return math.degrees(math.acos(cos_val))

# MoveNet keypoint indices
KEYPOINT_IDX = {"left_hip":11, "left_knee":13, "left_ankle":15,
                "right_hip":12, "right_knee":14, "right_ankle":16}

def flag_knee_error(keypoints, side="left", lower=90, upper=160):
    hip = keypoints[KEYPOINT_IDX[f"{side}_hip"]][:2][::-1]   # (y,x)→(x,y)
    knee = keypoints[KEYPOINT_IDX[f"{side}_knee"]][:2][::-1]
    ankle = keypoints[KEYPOINT_IDX[f"{side}_ankle"]][:2][::-1]
    angle = calculate_angle(hip, knee, ankle)
    error = angle < lower or angle > upper
    return error, angle
