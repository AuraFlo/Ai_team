from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import cv2, numpy as np, base64
from app.services.lunge_service import LungeService

router = APIRouter(prefix="/lunges", tags=["Lunges"])
service = LungeService()


class Landmark(BaseModel):
    x: float
    y: float
    score: Optional[float] = 1.0


class LungeRequest(BaseModel):
    landmarks: List[Landmark]
    frame_b64: Optional[str] = None


@router.post("/process")
def process_lunges(data: LungeRequest) -> Dict[str, Any]:
    try:
        landmarks_dicts = [lm.dict() for lm in data.landmarks]

        frame = None
        if data.frame_b64:
            nparr = np.frombuffer(base64.b64decode(data.frame_b64), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        result = service.process_landmarks(landmarks_dicts, frame=frame)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
