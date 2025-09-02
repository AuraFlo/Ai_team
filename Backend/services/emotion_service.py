# app/services/emotion_service.py
from typing import Dict, Any
import cv2
from app.services.emotion_detector import EmotionDetector


class EmotionService:
    def __init__(self, model_path="app/models/emotion_model.tflite"):
        # ✅ Load your TFLite model once at startup
        self.detector = EmotionDetector(model_path)

    def detect(self, frame, face_box=None) -> Dict[str, Any]:
        """
        Detect emotion from a frame.
        - frame: BGR image (numpy array)
        - face_box: (x, y, w, h) if face detection is available
        Returns: {"label": str, "confidence": float}
        """
        try:
            if face_box:
                # Crop detected face
                x, y, w, h = face_box
                face_img = frame[y:y + h, x:x + w]
            else:
                # fallback: center crop if no face box is provided
                h, w, _ = frame.shape
                cx, cy = w // 2, h // 2
                size = min(h, w) // 3
                face_img = frame[cy - size:cy + size, cx - size:cx + size]

            if face_img is None or face_img.size == 0:
                return {"label": "Neutral", "confidence": 0.0}

            return self.detector.predict(face_img)

        except Exception as e:
            return {"label": "Error", "confidence": 0.0, "detail": str(e)}
