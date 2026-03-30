from datetime import datetime

from pydantic import BaseModel


class ProjectIdeaGenerateRequest(BaseModel):
    count: int = 5


class ProjectIdeaEvidence(BaseModel):
    note_ids: list[int] = []
    review_ids: list[int] = []
    reason: str


class ProjectIdeaItem(BaseModel):
    id: int
    title: str
    rationale: str
    estimated_difficulty: str
    suggested_next_step: str
    evidence: ProjectIdeaEvidence
    generation_model: str
    created_at: datetime


class ProjectIdeasGenerateResponse(BaseModel):
    ideas: list[ProjectIdeaItem]
