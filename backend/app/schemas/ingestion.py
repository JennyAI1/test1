from datetime import datetime

from pydantic import BaseModel, HttpUrl


class SourceIngestionCreate(BaseModel):
    title: str
    authors: list[str] = []
    source_url: HttpUrl | None = None
    source_type: str = "manual"
    publication_year: int | None = None
    summary: str = ""
    takeaway: str = ""


class SourceResponse(BaseModel):
    id: int
    title: str
    authors: list[str]
    source_url: str | None
    source_type: str
    publication_year: int | None
    summary: str
    takeaway: str
    created_at: datetime


class SourceNoteCreate(BaseModel):
    title: str
    body: str
    tags: list[str] = []


class SourceNoteResponse(BaseModel):
    id: int
    source_id: int
    title: str
    body: str
    tags: list[str]
    created_at: datetime


class PdfMetadataPlaceholderRequest(BaseModel):
    filename: str


class PdfMetadataPlaceholderResponse(BaseModel):
    title: str
    authors: list[str]
    publication_year: int | None
    notes: str
