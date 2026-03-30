import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import LearningProgressEvent, User
from app.schemas.progress import ProgressEventCreate, ProgressEventResponse, ProgressSummary

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/events", response_model=ProgressEventResponse)
def create_event(
    payload: ProgressEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = LearningProgressEvent(
        user_id=user.id,
        app_key=payload.app_key,
        activity_type=payload.activity_type,
        minutes_spent=payload.minutes_spent,
        metadata_json=json.dumps(payload.metadata),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return _event_to_response(event)


@router.get("/events", response_model=list[ProgressEventResponse])
def list_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    events = (
        db.query(LearningProgressEvent)
        .filter(LearningProgressEvent.user_id == user.id)
        .order_by(LearningProgressEvent.created_at.desc())
        .all()
    )
    return [_event_to_response(event) for event in events]


@router.get("/summary", response_model=ProgressSummary)
def get_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    events = db.query(LearningProgressEvent).filter(LearningProgressEvent.user_id == user.id).all()
    by_app: dict[str, float] = {}
    total = 0.0
    for event in events:
        by_app[event.app_key] = by_app.get(event.app_key, 0.0) + event.minutes_spent
        total += event.minutes_spent

    return ProgressSummary(total_minutes=round(total, 2), by_app=by_app)


def _event_to_response(event: LearningProgressEvent) -> ProgressEventResponse:
    return ProgressEventResponse(
        id=event.id,
        app_key=event.app_key,
        activity_type=event.activity_type,
        minutes_spent=event.minutes_spent,
        metadata=json.loads(event.metadata_json),
        created_at=event.created_at,
    )
