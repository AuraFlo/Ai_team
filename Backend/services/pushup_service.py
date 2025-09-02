# app/services/pushup_service.py
from typing import Dict, Any, List, Optional
import os, math
from app.core.visualizer import draw_skeleton, frame_to_base64
from app.core.instructions import EXERCISE_INSTRUCTIONS


class PushupService:
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.use_ml = False
        if model_path and os.path.exists(model_path):
            try:
                import tensorflow as tf
                self.interp = tf.lite.Interpreter(model_path=model_path)
                self.interp.allocate_tensors()
                self.input_details = self.interp.get_input_details()
                self.output_details = self.interp.get_output_details()
                self.use_ml = True
            except Exception:
                self.use_ml = False

        self._state = {"rep_count": 0, "state": "up"}

    def reset(self):
        """Reset counter + phase for new workout"""
        self._state = {"rep_count": 0, "state": "up"}

    def _angle(self, a, b, c) -> float:
        """Compute angle ABC given 3 landmarks"""
        ax, ay = a["x"], a["y"]
        bx, by = b["x"], b["y"]
        cx, cy = c["x"], c["y"]
        v1 = (ax - bx, ay - by)
        v2 = (cx - bx, cy - by)
        d1 = (v1[0]**2 + v1[1]**2) ** 0.5 or 1e-6
        d2 = (v2[0]**2 + v2[1]**2) ** 0.5 or 1e-6
        cos = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (d1 * d2)))
        return math.degrees(math.acos(cos))

    def _heuristic(self, lms: List[dict], frame=None) -> Dict[str, Any]:
        # MoveNet indices
        LSH, LSE, LAW, RSH, RSE, RAW = 5, 7, 9, 6, 8, 10
        try:
            left = self._angle(lms[LSH], lms[LSE], lms[LAW])
            right = self._angle(lms[RSH], lms[RSE], lms[RAW])
            elbow = (left + right) / 2.0

            # simple form-quality metric
            accuracy = 100.0 if elbow < 60 else 80.0 if elbow < 90 else 50.0
            good_form = accuracy >= 70

            # phase detection
            if elbow < 70:  # going down
                self._state["state"] = "down"
            elif elbow > 150 and self._state["state"] == "down":
                self._state["state"] = "up"
                self._state["rep_count"] += 1

            # overlay skeleton
            frame_b64 = None
            if frame is not None:
                annotated = draw_skeleton(frame.copy(), lms, good_form=good_form)
                frame_b64 = frame_to_base64(annotated)

            return {
                "exercise": "pushups",
                "rep_count": self._state["rep_count"],
                "state": self._state["state"],
                "angles": {"elbow": elbow},
                "accuracy": accuracy,
                "instructions": EXERCISE_INSTRUCTIONS["pushup"],
                "frame": frame_b64
            }
        except Exception as e:
            return {
                "exercise": "pushups",
                "rep_count": self._state["rep_count"],
                "state": self._state["state"],
                "error": str(e)
            }

    def process_landmarks(self, landmarks: List[dict], frame=None) -> Dict[str, Any]:
        if self.use_ml:
            # TODO: preprocess + run inference with TFLite model
            pass
        return self._heuristic(landmarks, frame=frame)
