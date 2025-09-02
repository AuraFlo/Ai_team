from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.services.yoga_agent import recommend_yoga

router = APIRouter(prefix="/yoga", tags=["Yoga Agent"])


class YogaRequest(BaseModel):
    user_id: int
    journal_text: Optional[str] = None
    voice: bool = False
    audio_path: Optional[str] = None


@router.post("/recommend")
def recommend_yoga(data: YogaRequest):
    try:
        result = recommend_yoga_service(
            user_id=data.user_id,
            journal_input=data.audio_path if data.voice else data.journal_text,
            voice=data.voice
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
