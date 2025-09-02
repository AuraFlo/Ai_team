# app/core/processor.py
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from ..core.logger import log_event
from ..core import preprocessor
from app.services.pushup_service import PushupService
from app.services.squat_service import SquatService
from app.services.lunge_service import LungeService
from app.services.highKnees_service import HighKneesService
from app.services.bicepCurl_service import BicepCurlService
from app.services.armCircles_service import ArmCirclesService
from app.services.emotion_service import EmotionService
from app.services.breathing_service import BreathingEstimator
from app.services.movenet_service import detect_landmarks


class FrameProcessor:
    def __init__(self, models_dir="app/models/"):
        self.pushup_service = PushupService()
        self.squat_service = SquatService()
        self.lunge_service = LungeService()
        self.high_knees_service = HighKneesService()
        self.bicep_curl_service = BicepCurlService()
        self.arm_circles_service = ArmCirclesService()

        # ✅ Shared monitors
        self.breathing_monitor = BreathingEstimator()
        self.emotion_service = EmotionService(model_path=f"{models_dir}/emotion_model.tflite")

    def _get_user_age(self, user_id: int) -> int:
        """Fetch user age from DB; default 25 if not found."""
        db: Session = SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            return user.age if user and user.age else 25
        finally:
            db.close()

    def process(self, frame, workout_type: str, user_id: int, face_box=None) -> Dict[str, Any]:
        # 1️⃣ Pose detection
        raw_landmarks = detect_landmarks(frame)
        norm_landmarks = preprocessor.normalize_keypoints(raw_landmarks, frame.shape)

        # 2️⃣ Exercise-specific analysis
        if workout_type == "pushup":
            ex_out = self.pushup_service.process_landmarks(norm_landmarks)
        elif workout_type == "squat":
            ex_out = self.squat_service.process_landmarks(norm_landmarks)
        elif workout_type == "lunge":
            ex_out = self.lunge_service.process_landmarks(norm_landmarks)
        elif workout_type == "high_knees":
            ex_out = self.high_knees_service.process_landmarks(norm_landmarks)
        elif workout_type == "bicep_curls":
            ex_out = self.bicep_curl_service.process_landmarks(norm_landmarks)
        elif workout_type == "arm_circles":
            ex_out = self.arm_circles_service.process_landmarks(norm_landmarks)
        else:
            ex_out = {"rep_count": 0, "angles": {}, "state": "idle", "accuracy": 0}

        # 3️⃣ Emotion detection
        emo_result = self.emotion_service.detect(frame, face_box)

        # 4️⃣ Breathing detection (with age-awareness)
        user_age = self._get_user_age(user_id)
        breath_result = self.breathing_monitor.process_frame(frame, age=user_age)

        # 5️⃣ Combine results
        result = {
            "exercise": workout_type,
            "rep_count": ex_out.get("rep_count", 0),
            "angles": ex_out.get("angles", {}),
            "state": ex_out.get("state", "idle"),
            "accuracy": ex_out.get("accuracy", 0),
            "emotion": emo_result.get("label", "Neutral"),
            "confidence": emo_result.get("confidence", 0.0),
            "breathing": breath_result,
        }

        # 6️⃣ Log results
        log_data = {**result, "timestamp": datetime.now()}
        log_event(user_id, log_data)

        return result
