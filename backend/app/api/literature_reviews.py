from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import LiteratureReview, Note, User
from app.schemas.literature_reviews import (
    LinkedNoteCreate,
    LinkedNoteResponse,
    LiteratureReviewCreate,
    LiteratureReviewResponse,
    LiteratureReviewUpdate,
)

router = APIRouter(prefix="/literature-reviews", tags=["literature-reviews"])


@router.post("", response_model=LiteratureReviewResponse)
def create_review(payload: LiteratureReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    review = LiteratureReview(
        user_id=user.id,
        title=payload.title,
        authors=",".join(payload.authors),
        publication_year=payload.publication_year,
        methods=payload.methods,
        findings=payload.findings,
        limitations=payload.limitations,
        summary=payload.summary,
        status=payload.status,
        tags=",".join(payload.tags),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return _to_response(db, review)


@router.get("", response_model=list[LiteratureReviewResponse])
def list_reviews(
    query: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(LiteratureReview).filter(LiteratureReview.user_id == user.id)

    if status:
        q = q.filter(LiteratureReview.status == status)

    if tag:
        q = q.filter(LiteratureReview.tags.ilike(f"%{tag}%"))

    if query:
        q = q.filter(
            text(
                "to_tsvector('english', coalesce(title,'') || ' ' || coalesce(authors,'') || ' ' || "
                "coalesce(summary,'') || ' ' || coalesce(methods,'') || ' ' || coalesce(findings,'') || ' ' || "
                "coalesce(limitations,'')) @@ plainto_tsquery('english', :query)"
            )
        ).params(query=query)

    reviews = q.order_by(LiteratureReview.updated_at.desc()).all()
    return [_to_response(db, review) for review in reviews]


@router.patch("/{review_id}", response_model=LiteratureReviewResponse)
def update_review(
    review_id: int,
    payload: LiteratureReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review = db.query(LiteratureReview).filter(LiteratureReview.id == review_id, LiteratureReview.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "authors" and value is not None:
            setattr(review, "authors", ",".join(value))
        elif field == "tags" and value is not None:
            setattr(review, "tags", ",".join(value))
        else:
            setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return _to_response(db, review)


@router.post("/{review_id}/notes", response_model=LinkedNoteResponse)
def create_linked_note(
    review_id: int,
    payload: LinkedNoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review = db.query(LiteratureReview).filter(LiteratureReview.id == review_id, LiteratureReview.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    note = Note(
        user_id=user.id,
        review_id=review_id,
        title=payload.title,
        body=payload.body,
        tags=",".join(payload.tags),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return LinkedNoteResponse(
        id=note.id,
        title=note.title,
        body=note.body,
        tags=[tag for tag in note.tags.split(",") if tag],
        created_at=note.created_at,
    )


def _to_response(db: Session, review: LiteratureReview) -> LiteratureReviewResponse:
    notes = db.query(Note).filter(Note.review_id == review.id, Note.user_id == review.user_id).order_by(Note.created_at.desc()).all()
    return LiteratureReviewResponse(
        id=review.id,
        title=review.title,
        authors=[item for item in review.authors.split(",") if item],
        publication_year=review.publication_year,
        methods=review.methods,
        findings=review.findings,
        limitations=review.limitations,
        summary=review.summary,
        status=review.status,
        tags=[item for item in review.tags.split(",") if item],
        linked_notes=[
            LinkedNoteResponse(
                id=note.id,
                title=note.title,
                body=note.body,
                tags=[tag for tag in note.tags.split(",") if tag],
                created_at=note.created_at,
            )
            for note in notes
        ],
        created_at=review.created_at,
        updated_at=review.updated_at,
    )
