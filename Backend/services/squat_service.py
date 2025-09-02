# app/services/squat_service.py
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


class SquatService:
    def __init__(self):
        self.state = "up"
        self.rep_count = 0

    def reset(self):
        """Reset state + rep count"""
        self.state = "up"
        self.rep_count = 0

    def process_landmarks(self, landmarks: List[dict], frame=None) -> Dict[str, Any]:
        # MoveNet indices
        try:
            LHIP, LKNEE, LANK = landmarks[11], landmarks[13], landmarks[15]
            RHIP, RKNEE, RANK = landmarks[12], landmarks[14], landmarks[16]
        except Exception:
            return {
                "exercise": "squats",
                "rep_count": self.rep_count,
                "state": self.state,
                "detail": "missing landmarks"
            }

        # validate
        for lm in (LHIP, LKNEE, LANK, RHIP, RKNEE, RANK):
            if lm is None or "x" not in lm or "y" not in lm:
                return {
                    "exercise": "squats",
                    "rep_count": self.rep_count,
                    "state": self.state,
                    "detail": "invalid landmarks"
                }

        # calculate angles
        la = _angle(LHIP["x"], LHIP["y"], LKNEE["x"], LKNEE["y"], LANK["x"], LANK["y"])
        ra = _angle(RHIP["x"], RHIP["y"], RKNEE["x"], RKNEE["y"], RANK["x"], RANK["y"])
        if la is None or ra is None:
            return {
                "exercise": "squats",
                "rep_count": self.rep_count,
                "state": self.state,
                "detail": "angle failed"
            }

        knee = (la + ra) / 2.0

        # thresholds
        DOWN_ANGLE = 100.0
        UP_ANGLE = 160.0

        # state machine
        if knee < DOWN_ANGLE and self.state == "up":
            self.state = "down"
        elif knee > UP_ANGLE and self.state == "down":
            self.state = "up"
            self.rep_count += 1

        # accuracy heuristic
        accuracy = 100.0 if knee < 80 else 70.0 if knee < 100 else 50.0
        good_form = accuracy >= 70

        # overlay skeleton
        frame_b64 = None
        if frame is not None:
            annotated = draw_skeleton(frame.copy(), landmarks, good_form=good_form)
            frame_b64 = frame_to_base64(annotated)

        return {
            "exercise": "squats",
            "rep_count": self.rep_count,
            "state": self.state,
            "angles": {"left_knee": la, "right_knee": ra},
            "accuracy": accuracy,
            "instructions": EXERCISE_INSTRUCTIONS["squat"],  # ✅ pulls from instructions.py
            "frame": frame_b64
        }
