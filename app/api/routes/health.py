from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Service Health Check")
def health_check():
    return {
        "status": "ok",
        "service": "hospital-ai-receptionist"
    }

@router.get("/db", summary="Database Connectivity Check")
def db_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "hospital_receptionist"
    }
