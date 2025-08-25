import numpy as np
from utils import calculate_angle, polar_angle_deg, ang_delta
from config import ELBOW_STRAIGHT_MIN, RADIUS_RATIO_MIN, FULL_TURN_DEG, ANGLE_SMOOTH_DEG

class ArmState:
    def __init__(self):
        self.last_angle = None
        self.direction = 0
        self.cum = 0.0
        self.reps = 0
        self.last_rep_score = 0

def update_arm_circle(state, shoulder, elbow, wrist):
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    arm_len = np.linalg.norm(np.array(shoulder)-np.array(elbow)) + np.linalg.norm(np.array(elbow)-np.array(wrist))
    radius = np.linalg.norm(np.array(wrist)-np.array(shoulder))
    radius_ratio = 0 if arm_len < 1e-3 else (radius/arm_len)

    ang = polar_angle_deg(shoulder, wrist)

    if state.last_angle is None:
        state.last_angle = ang
        status = "Extend Arm" if elbow_angle < ELBOW_STRAIGHT_MIN else "Good"
        score = 100
        return ang, elbow_angle, radius_ratio, status, score

    d = ang_delta(state.last_angle, ang)
    if abs(d) < ANGLE_SMOOTH_DEG: d = 0.0

    if d != 0:
        s = 1 if d > 0 else -1
        if state.direction == 0: state.direction = s
        elif s != state.direction and abs(d) > 10:
            state.direction, state.cum = s, 0.0

    state.cum += abs(d)
    state.last_angle = ang

    status = "Good" if elbow_angle >= ELBOW_STRAIGHT_MIN else "Elbow Bent"
    if radius_ratio < RADIUS_RATIO_MIN:
        status += " + Short Radius"

    score = max(0, 100 - max(0, ELBOW_STRAIGHT_MIN - elbow_angle)*0.8 - max(0, (RADIUS_RATIO_MIN-radius_ratio)/RADIUS_RATIO_MIN)*40)

    if state.cum >= FULL_TURN_DEG and elbow_angle >= ELBOW_STRAIGHT_MIN and radius_ratio >= RADIUS_RATIO_MIN:
        state.reps += 1
        state.last_rep_score = int(score)
        state.cum = 0.0

    return ang, elbow_angle, radius_ratio, status, int(score)
