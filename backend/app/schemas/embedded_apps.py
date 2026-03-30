from datetime import datetime

from pydantic import BaseModel, HttpUrl


class EmbeddedAppCreate(BaseModel):
    title: str
    url: HttpUrl
    category: str


class EmbeddedAppResponse(BaseModel):
    id: int
    title: str
    url: str
    category: str
    panel_order: int
    created_at: datetime


class ReorderEmbeddedAppsRequest(BaseModel):
    ordered_ids: list[int]
