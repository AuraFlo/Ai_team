# app/services/bicep_curl_service.py
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


class BicepCurlService:
    def __init__(self):
        self.state = "down"
        self.rep_count = 0

    def reset(self):
        """Reset state + rep count"""
        self.state = "down"
        self.rep_count = 0

    def process_landmarks(self, landmarks: List[dict], frame=None) -> Dict[str, Any]:
        """
        Process MoveNet landmarks to count bicep curls.
        Uses elbow flexion (shoulder-elbow-wrist angle).
        If frame is provided, returns base64 with skeleton overlay.
        """
        # MoveNet indices
        try:
            LSH, LELB, LWR = landmarks[5], landmarks[7], landmarks[9]
            RSH, RELB, RWR = landmarks[6], landmarks[8], landmarks[10]
        except Exception:
            return {
                "exercise": "bicep_curls",
                "rep_count": self.rep_count,
                "state": self.state,
                "detail": "missing landmarks"
            }

        # calculate angles
        la = _angle(LSH["x"], LSH["y"], LELB["x"], LELB["y"], LWR["x"], LWR["y"])
        ra = _angle(RSH["x"], RSH["y"], RELB["x"], RELB["y"], RWR["x"], RWR["y"])
        if la is None or ra is None:
            return {
                "exercise": "bicep_curls",
                "rep_count": self.rep_count,
                "state": self.state,
                "detail": "angle failed"
            }

        elbow = (la + ra) / 2.0

        # thresholds
        CURL_DOWN = 160.0   # arm extended
        CURL_UP = 40.0      # arm fully curled

        # state machine
        if elbow < CURL_UP and self.state == "down":
            self.state = "up"
            self.rep_count += 1
        elif elbow > CURL_DOWN:
            self.state = "down"

        # accuracy heuristic
        accuracy = 100.0 if elbow < 50 else 70.0 if elbow < 90 else 50.0
        good_form = accuracy >= 70

        # overlay skeleton
        frame_b64 = None
        if frame is not None:
            annotated = draw_skeleton(frame.copy(), landmarks, good_form=good_form)
            frame_b64 = frame_to_base64(annotated)

        return {
            "exercise": "bicep_curls",
            "rep_count": self.rep_count,
            "state": self.state,
            "angles": {"elbow_angle": elbow},
            "accuracy": accuracy,
            "instructions": EXERCISE_INSTRUCTIONS["bicep_curls"],  # ✅
            "frame": frame_b64
        }
