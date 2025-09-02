import cv2
import base64
import numpy as np
from fastapi import APIRouter, WebSocket
from app.core.processor import FrameProcessor

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Initialize processor with models directory
processor = FrameProcessor(models_dir="app/models/")

@router.websocket("/exercise")
async def exercise_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # 1️⃣ Receive frame from frontend (base64-encoded string)
            data = await websocket.receive_text()
            img_bytes = base64.b64decode(data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # 2️⃣ Run processor (pose detection + rep counting + emotion etc.)
            result = processor.process(
                frame,
                workout_type="bicep",   # or pushup/squat depending on frontend
                face_box=(100, 100, 150, 150)  # dummy face box for now
            )

            # 3️⃣ Send results back to frontend
            await websocket.send_json(result)

        except Exception as e:
            await websocket.send_json({"error": str(e)})
            break
