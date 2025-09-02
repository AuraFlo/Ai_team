from sqlalchemy.orm import Session
from . import models

def get_session(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()