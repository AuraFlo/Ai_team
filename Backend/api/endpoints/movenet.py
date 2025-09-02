# app/api/endpoints/movenet.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import cv2
import numpy as np
from app.services.movenet_service import detect_landmarks

router = APIRouter(prefix="/movenet", tags=["MoveNet"])


@router.post("/detect")
async def movenet_detect(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        landmarks = detect_landmarks(frame)
        return {"success": True, "landmarks": landmarks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
