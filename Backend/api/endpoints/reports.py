# app/api/endpoints/reports.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from app.services.report_generator import generate_session_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/session/{session_id}")
def get_session_report(session_id: int):
    try:
        path = generate_session_report(session_id)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Report not found")
        return FileResponse(path, media_type="application/pdf", filename=f"session_{session_id}.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
