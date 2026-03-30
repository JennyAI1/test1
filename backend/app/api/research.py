import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import AIEvaluationLog, LiteratureReview, Note, ResearchEntry, User
from app.schemas.research import EntryCreate, EntryResponse, SuggestionResponse
from app.services.crypto_service import decrypt_text, encrypt_text
from app.services.rate_limit_service import enforce_rate_limit
from app.services.suggestion_service import generate_project_suggestions

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/entries", response_model=EntryResponse)
def create_entry(
    payload: EntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = ResearchEntry(
        user_id=user.id,
        title=payload.title,
        entry_type=payload.entry_type,
        tags=",".join(payload.tags),
        encrypted_content=encrypt_text(payload.rich_text),
        source_url=payload.source_url,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _entry_to_response(entry)


@router.get("/entries", response_model=list[EntryResponse])
def list_entries(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = (
        db.query(ResearchEntry)
        .filter(ResearchEntry.user_id == user.id)
        .order_by(ResearchEntry.created_at.desc())
        .all()
    )
    return [_entry_to_response(entry) for entry in entries]


@router.post("/suggestions", response_model=SuggestionResponse)
def get_suggestions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(f"{user.id}:research_suggestions", max_requests=10, window_seconds=60)

    reviews = db.query(LiteratureReview).filter(LiteratureReview.user_id == user.id).all()
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    suggestions = generate_project_suggestions(reviews, notes)

    db.add(
        AIEvaluationLog(
            user_id=user.id,
            task_type="research_suggestions",
            prompt_template="heuristic_suggestions_v1",
            input_snapshot=json.dumps(
                {
                    "review_ids": [r.id for r in reviews],
                    "note_ids": [n.id for n in notes],
                }
            ),
            output_snapshot=json.dumps(suggestions),
            quality_score=None,
        )
    )
    db.commit()

    return SuggestionResponse(suggestions=suggestions)


def _entry_to_response(entry: ResearchEntry) -> EntryResponse:
    return EntryResponse(
        id=entry.id,
        title=entry.title,
        entry_type=entry.entry_type,
        tags=[tag for tag in entry.tags.split(",") if tag],
        rich_text=decrypt_text(entry.encrypted_content),
        source_url=entry.source_url,
        created_at=entry.created_at,
    )
