from datetime import date as dt_date, datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func, cast, Date
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models import Call
from app.schemas.call import CallCreate, CallResponse, CallListResponse

router = APIRouter(prefix="/calls", tags=["Calls"])

@router.post("", response_model=CallResponse, status_code=status.HTTP_201_CREATED, summary="Create Call Log")
def create_call_log(payload: CallCreate, db: Session = Depends(get_db)):
    started_at = payload.started_at or datetime.now(timezone.utc)
    new_call = Call(
        patient_id=payload.patient_id,
        phone_number=payload.phone_number.strip(),
        started_at=started_at,
        ended_at=payload.ended_at,
        duration_seconds=payload.duration_seconds,
        intent=payload.intent.strip(),
        specialty_detected=payload.specialty_detected.strip() if payload.specialty_detected else None,
        outcome=payload.outcome,
        escalated=payload.escalated
    )
    db.add(new_call)
    db.commit()
    db.refresh(new_call)

    return CallResponse(
        id=new_call.id,
        patient_id=new_call.patient_id,
        phone_number=new_call.phone_number,
        started_at=new_call.started_at,
        ended_at=new_call.ended_at,
        duration_seconds=new_call.duration_seconds,
        intent=new_call.intent,
        specialty_detected=new_call.specialty_detected,
        outcome=new_call.outcome.value,
        escalated=new_call.escalated,
        created_at=new_call.created_at
    )

@router.get("", response_model=CallListResponse, summary="List Call Logs")
def list_calls(
    date: dt_date | None = Query(None, description="Filter by date"),
    patient_id: int | None = Query(None, description="Filter by patient ID"),
    outcome: str | None = Query(None, description="Filter by outcome"),
    escalated: bool | None = Query(None, description="Filter by escalated status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = select(Call)
    count_query = select(func.count(Call.id))

    if date:
        query = query.where(cast(Call.started_at, Date) == date)
        count_query = count_query.where(cast(Call.started_at, Date) == date)
    if patient_id:
        query = query.where(Call.patient_id == patient_id)
        count_query = count_query.where(Call.patient_id == patient_id)
    if outcome:
        query = query.where(Call.outcome == outcome)
        count_query = count_query.where(Call.outcome == outcome)
    if escalated is not None:
        query = query.where(Call.escalated == escalated)
        count_query = count_query.where(Call.escalated == escalated)

    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    calls = db.scalars(query.order_by(Call.started_at.desc()).offset(offset).limit(page_size)).all()

    items = [
        CallResponse(
            id=c.id,
            patient_id=c.patient_id,
            phone_number=c.phone_number,
            started_at=c.started_at,
            ended_at=c.ended_at,
            duration_seconds=c.duration_seconds,
            intent=c.intent,
            specialty_detected=c.specialty_detected,
            outcome=c.outcome.value,
            escalated=c.escalated,
            created_at=c.created_at
        )
        for c in calls
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
