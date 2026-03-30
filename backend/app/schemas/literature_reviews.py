from datetime import datetime

from pydantic import BaseModel


class LiteratureReviewCreate(BaseModel):
    title: str
    authors: list[str] = []
    publication_year: int | None = None
    methods: str = ""
    findings: str = ""
    limitations: str = ""
    summary: str
    status: str = "to-read"
    tags: list[str] = []


class LiteratureReviewUpdate(BaseModel):
    title: str | None = None
    authors: list[str] | None = None
    publication_year: int | None = None
    methods: str | None = None
    findings: str | None = None
    limitations: str | None = None
    summary: str | None = None
    status: str | None = None
    tags: list[str] | None = None


class LinkedNoteCreate(BaseModel):
    title: str
    body: str
    tags: list[str] = []


class LinkedNoteResponse(BaseModel):
    id: int
    title: str
    body: str
    tags: list[str]
    created_at: datetime


class LiteratureReviewResponse(BaseModel):
    id: int
    title: str
    authors: list[str]
    publication_year: int | None
    methods: str
    findings: str
    limitations: str
    summary: str
    status: str
    tags: list[str]
    linked_notes: list[LinkedNoteResponse]
    created_at: datetime
    updated_at: datetime
