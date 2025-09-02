# app/core/visualizer.py
import cv2
import base64

# COCO keypoint edges (17-point MoveNet/MediaPipe format)
EDGES = [
    (0,1), (0,2), (1,3), (2,4),
    (0,5), (0,6), (5,7), (7,9), (6,8), (8,10),
    (5,6), (5,11), (6,12),
    (11,12), (11,13), (13,15), (12,14), (14,16)
]

def draw_skeleton(frame, landmarks, confidence_threshold=0.3, good_form=True):
    """
    Draw skeleton overlay on the frame.
    Green = correct form, Red = incorrect form.
    
    Args:
        frame: np.array (OpenCV BGR frame)
        landmarks: list of dicts like [{x, y, score}, ...]
        confidence_threshold: min confidence to draw
        good_form: bool → controls skeleton color
    """
    h, w, _ = frame.shape
    color = (0, 255, 0) if good_form else (0, 0, 255)

    # draw joints
    for i, kp in enumerate(landmarks):
        if kp.get("score", 1.0) > confidence_threshold:
            cx, cy = int(kp["x"] * w), int(kp["y"] * h)
            cv2.circle(frame, (cx, cy), 4, color, -1)

    # draw edges
    for p1, p2 in EDGES:
        if landmarks[p1].get("score", 1.0) > confidence_threshold and landmarks[p2].get("score", 1.0) > confidence_threshold:
            x1, y1 = int(landmarks[p1]["x"] * w), int(landmarks[p1]["y"] * h)
            x2, y2 = int(landmarks[p2]["x"] * w), int(landmarks[p2]["y"] * h)
            cv2.line(frame, (x1, y1), (x2, y2), color, 2)

    return frame


def frame_to_base64(frame):
    """Convert OpenCV BGR frame → base64 JPEG string for frontend."""
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")
