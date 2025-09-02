# app/services/arm_circles_service.py
from typing import Dict, Any, List
import math
import numpy as np
from app.core.visualizer import draw_skeleton, frame_to_base64
from app.core.instructions import EXERCISE_INSTRUCTIONS

FULL_TURN_DEG = 300.0
ELBOW_STRAIGHT_MIN = 150
RADIUS_RATIO_MIN = 0.75
ANGLE_SMOOTH_DEG = 1.0


def calculate_angle(a, b, c):
    """Angle at b given 3 points (x, y)."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) -
                       math.atan2(a[1]-b[1], a[0]-b[0]))
    ang = abs(ang)
    return 360 - ang if ang > 180 else ang


def polar_angle_deg(origin, point):
    dy = point[1] - origin[1]
    dx = point[0] - origin[0]
    ang = math.degrees(math.atan2(dy, dx))
    return ang + 360 if ang < 0 else ang


def ang_delta(a, b):
    d = b - a
    if d > 180:
        d -= 360
    if d <= -180:
        d += 360
    return d


class ArmState:
    """Keeps track of one arm's circular motion."""
    def __init__(self):
        self.last_angle = None
        self.direction = 0
        self.cum = 0.0
        self.reps = 0
        self.last_rep_score = 0


class ArmCirclesService:
    def __init__(self):
        self.left_state = ArmState()
        self.right_state = ArmState()

    def reset(self):
        self.left_state = ArmState()
        self.right_state = ArmState()

    def _update_arm(self, state: ArmState, shoulder, elbow, wrist):
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        arm_len = np.linalg.norm(np.array(shoulder) - np.array(elbow)) + \
                  np.linalg.norm(np.array(elbow) - np.array(wrist))
        radius = np.linalg.norm(np.array(wrist) - np.array(shoulder))
        radius_ratio = 0 if arm_len < 1e-3 else (radius / arm_len)

        ang = polar_angle_deg(shoulder, wrist)

        if state.last_angle is None:
            state.last_angle = ang
            score = max(0, 100
                        - max(0, (ELBOW_STRAIGHT_MIN - elbow_angle)) * 0.8
                        - max(0, (RADIUS_RATIO_MIN - radius_ratio) / RADIUS_RATIO_MIN) * 40)
            return int(score), elbow_angle, radius_ratio, state.reps

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

        score = max(0, 100
                    - max(0, (ELBOW_STRAIGHT_MIN - elbow_angle)) * 0.8
                    - max(0, (RADIUS_RATIO_MIN - radius_ratio) / RADIUS_RATIO_MIN) * 40)

        if state.cum >= FULL_TURN_DEG and \
           elbow_angle >= ELBOW_STRAIGHT_MIN and \
           radius_ratio >= RADIUS_RATIO_MIN:
            state.reps += 1
            state.last_rep_score = int(score)
            state.cum = 0.0

        return int(score), elbow_angle, radius_ratio, state.reps

    def process_landmarks(self, landmarks: List[dict], frame=None) -> Dict[str, Any]:
        """
        landmarks: list of dicts with {x, y, score}
        frame: optional OpenCV BGR frame → returns base64 with skeleton overlay
        """
        try:
            LSH, LELB, LWR = landmarks[5], landmarks[7], landmarks[9]
            RSH, RELB, RWR = landmarks[6], landmarks[8], landmarks[10]
        except Exception:
            return {"exercise": "arm_circles", "error": "missing landmarks"}

        l_score, l_elbow, l_rad, l_reps = self._update_arm(
            self.left_state,
            (LSH["x"], LSH["y"]), (LELB["x"], LELB["y"]), (LWR["x"], LWR["y"])
        )
        r_score, r_elbow, r_rad, r_reps = self._update_arm(
            self.right_state,
            (RSH["x"], RSH["y"]), (RELB["x"], RELB["y"]), (RWR["x"], RWR["y"])
        )

        avg_score = (l_score + r_score) / 2.0
        good_form = avg_score >= 70

        frame_b64 = None
        if frame is not None:
            annotated = draw_skeleton(frame.copy(), landmarks, good_form=good_form)
            frame_b64 = frame_to_base64(annotated)

        return {
            "exercise": "arm_circles",
            "left": {"reps": l_reps, "elbow_angle": l_elbow,
                     "radius_ratio": l_rad, "score": l_score},
            "right": {"reps": r_reps, "elbow_angle": r_elbow,
                      "radius_ratio": r_rad, "score": r_score},
            "instructions": EXERCISE_INSTRUCTIONS["arm_circles"],  # ✅ from core
            "frame": frame_b64
        }
