# app/services/high_knees_service.py
from typing import Dict, Any, List
import math
from app.core.visualizer import draw_skeleton, frame_to_base64
from app.core.instructions import EXERCISE_INSTRUCTIONS


def _angle(ax, ay, bx, by, cx, cy):
    """Calculate angle at point B given 3 points A-B-C"""
    AB = (ax - bx, ay - by)
    CB = (cx - bx, cy - by)
    dot = AB[0] * CB[0] + AB[1] * CB[1]
    n1 = (AB[0]**2 + AB[1]**2) ** 0.5
    n2 = (CB[0]**2 + CB[1]**2) ** 0.5
    if n1 == 0 or n2 == 0:
        return None
    cosang = max(-1.0, min(1.0, dot / (n1 * n2)))
    return math.degrees(math.acos(cosang))


class HighKneesService:
    def __init__(self):
        self.state = "down"
        self.rep_count = 0

    def reset(self):
        """Reset state and rep count"""
        self.state = "down"
        self.rep_count = 0

    def process_landmarks(self, landmarks: List[dict], frame=None) -> Dict[str, Any]:
        """
        Detect high knees based on hip-knee-ankle angles and knee height.
        Optionally overlay skeleton if frame is provided.
        """
        try:
            LHIP, LKNEE, LANK = landmarks[11], landmarks[13], landmarks[15]
            RHIP, RKNEE, RANK = landmarks[12], landmarks[14], landmarks[16]
        except Exception:
            return {
                "exercise": "high_knees",
                "rep_count": self.rep_count,
                "state": self.state,
                "detail": "missing landmarks"
            }

        # knee angles
        la = _angle(LHIP["x"], LHIP["y"], LKNEE["x"], LKNEE["y"], LANK["x"], LANK["y"])
        ra = _angle(RHIP["x"], RHIP["y"], RKNEE["x"], RKNEE["y"], RANK["x"], RANK["y"])

        # knee height relative to hip (y is normalized → smaller y means higher knee)
        left_knee_height = LHIP["y"] - LKNEE["y"]
        right_knee_height = RHIP["y"] - RKNEE["y"]
        avg_height = (left_knee_height + right_knee_height) / 2.0

        # thresholds
        UP_THRESHOLD = 0.15
        DOWN_THRESHOLD = 0.05

        if avg_height > UP_THRESHOLD and self.state == "down":
            self.state = "up"
            self.rep_count += 1
        elif avg_height < DOWN_THRESHOLD and self.state == "up":
            self.state = "down"

        # accuracy heuristic
        accuracy = 100.0 if avg_height > 0.2 else 70.0
        good_form = accuracy >= 70

        # overlay skeleton
        frame_b64 = None
        if frame is not None:
            annotated = draw_skeleton(frame.copy(), landmarks, good_form=good_form)
            frame_b64 = frame_to_base64(annotated)

        return {
            "exercise": "high_knees",
            "rep_count": self.rep_count,
            "state": self.state,
            "angles": {"left_knee": la, "right_knee": ra},
            "knee_height": avg_height,
            "accuracy": accuracy,
            "instructions": EXERCISE_INSTRUCTIONS["high_knees"],  # ✅
            "frame": frame_b64
        }
