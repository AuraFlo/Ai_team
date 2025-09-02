# app/services/lunge_service.py
from typing import Dict, Any, List
import numpy as np
import time
import math
from collections import deque
from app.core.visualizer import draw_skeleton, frame_to_base64
from app.core.instructions import EXERCISE_INSTRUCTIONS


def calculate_angle(a, b, c):
    """Compute angle at b given 3 points (x, y)."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle


class LungeService:
    def __init__(self):
        self.counter = 0
        self.stage = "up"
        self.last_rep_score = 0
        self.last_rep_time = 0
        self.cooldown_time = 0.6  # seconds

        self.down_frames_required = 3
        self.up_frames_required = 3
        self.down_counter = 0
        self.up_counter = 0

        # smoothing
        self.knee_history = deque(maxlen=5)
        self.elbow_history = deque(maxlen=5)
        self.torso_history = deque(maxlen=5)

        # thresholds
        self.elbow_min, self.elbow_max = 150, 180
        self.torso_min, self.torso_max = 80, 100
        self.knee_min, self.knee_max = 80, 100

    def reset(self):
        """Reset state for a new session"""
        self.__init__()

    def process_landmarks(self, landmarks: List[dict], frame=None) -> Dict[str, Any]:
        """
        landmarks: MoveNet-style list of dicts {x, y, score}.
        frame: optional OpenCV BGR frame → returns base64 with skeleton overlay
        """
        try:
            # MoveNet indices
            hip = (landmarks[11]["x"], landmarks[11]["y"])
            knee = (landmarks[13]["x"], landmarks[13]["y"])
            ankle = (landmarks[15]["x"], landmarks[15]["y"])
            shoulder = (landmarks[5]["x"], landmarks[5]["y"])
            elbow = (landmarks[7]["x"], landmarks[7]["y"])
            wrist = (landmarks[9]["x"], landmarks[9]["y"])
            ear = (landmarks[3]["x"], landmarks[3]["y"])
        except Exception:
            return {"exercise": "lunge", "error": "missing landmarks"}

        # compute angles
        knee_angle = calculate_angle(hip, knee, ankle)
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        torso_angle = calculate_angle(hip, shoulder, ear)

        # smoothing
        self.knee_history.append(knee_angle)
        self.elbow_history.append(elbow_angle)
        self.torso_history.app_
