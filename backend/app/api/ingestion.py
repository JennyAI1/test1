import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import Note, Source, User
from app.schemas.ingestion import (
    PdfMetadataPlaceholderRequest,
    PdfMetadataPlaceholderResponse,
    SourceIngestionCreate,
    SourceNoteCreate,
    SourceNoteResponse,
    SourceResponse,
)

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/sources", response_model=SourceResponse)
def create_source(payload: SourceIngestionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    source = Source(
        user_id=user.id,
        title=payload.title,
        authors=",".join(payload.authors),
        source_url=str(payload.source_url) if payload.source_url else None,
        source_type=payload.source_type,
        publication_year=payload.publication_year,
        summary=payload.summary,
        takeaway=payload.takeaway,
        metadata_json=json.dumps({"created_by": user.id, "ingestion_flow": payload.source_type}),
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return _source_to_response(source)


@router.get("/sources", response_model=list[SourceResponse])
def list_sources(query: str | None = Query(default=None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _ = user
    q = db.query(Source).filter(Source.user_id == user.id)
    if query:
        q = q.filter(Source.title.ilike(f"%{query}%"))
    sources = q.order_by(Source.created_at.desc()).all()
    return [_source_to_response(source) for source in sources]


@router.post("/sources/{source_id}/notes", response_model=SourceNoteResponse)
def create_source_note(
    source_id: int,
    payload: SourceNoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    source = db.query(Source).filter(Source.id == source_id, Source.user_id == user.id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    note = Note(
        user_id=user.id,
        source_id=source.id,
        title=payload.title,
        body=payload.body,
        tags=",".join(payload.tags),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return SourceNoteResponse(
        id=note.id,
        source_id=source.id,
        title=note.title,
        body=note.body,
        tags=[tag for tag in note.tags.split(",") if tag],
        created_at=note.created_at,
    )


@router.post("/pdf-metadata-placeholder", response_model=PdfMetadataPlaceholderResponse)
def pdf_metadata_placeholder(payload: PdfMetadataPlaceholderRequest):
    stem = payload.filename.rsplit(".", maxsplit=1)[0]
    return PdfMetadataPlaceholderResponse(
        title=stem.replace("_", " ").title(),
        authors=["Unknown Author"],
        publication_year=None,
        notes="Placeholder only: wire this endpoint to a PDF parser/extractor later.",
    )


def _source_to_response(source: Source) -> SourceResponse:
    return SourceResponse(
        id=source.id,
        title=source.title,
        authors=[item for item in source.authors.split(",") if item],
        source_url=source.source_url,
        source_type=source.source_type,
        publication_year=source.publication_year,
        summary=source.summary,
        takeaway=source.takeaway,
        created_at=source.created_at,
    )
