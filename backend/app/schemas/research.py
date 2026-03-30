from datetime import datetime

from pydantic import BaseModel


class EntryCreate(BaseModel):
    title: str
    entry_type: str = "note"
    tags: list[str] = []
    rich_text: str
    source_url: str | None = None


class EntryResponse(BaseModel):
    id: int
    title: str
    entry_type: str
    tags: list[str]
    rich_text: str
    source_url: str | None
    created_at: datetime


class SuggestionItem(BaseModel):
    idea: str
    influencing_review_ids: list[int]
    influencing_note_ids: list[int]
    why_promising: str
    confidence_language: str


class SuggestionResponse(BaseModel):
    suggestions: list[SuggestionItem]
