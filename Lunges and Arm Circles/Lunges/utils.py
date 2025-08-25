import cv2
import numpy as np
import math

EDGES = {
    (0,1), (0,2), (1,3), (2,4),
    (0,5), (0,6), (5,7), (7,9), (6,8), (8,10),
    (5,6), (5,11), (6,12),
    (11,12), (11,13), (13,15), (12,14), (14,16)
}

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians*180.0/np.pi)
    return angle if angle <= 180.0 else 360 - angle

def draw_skeleton(frame, keypoints, confidence_threshold=0.3):
    h, w, _ = frame.shape
    for kp in keypoints:
        y, x, c = kp
        if c > confidence_threshold:
            cx, cy = int(x * w), int(y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

    for p1, p2 in EDGES:
        y1, x1, c1 = keypoints[p1]
        y2, x2, c2 = keypoints[p2]
        if c1 > confidence_threshold and c2 > confidence_threshold:
            x1, y1 = int(x1 * w), int(y1 * h)
            x2, y2 = int(x2 * w), int(y2 * h)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    return frame
