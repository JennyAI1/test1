from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai_ideas, ai_learning_coach, auth, embedded_apps, ingestion, learning_tracker, literature_reviews, progress, research
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(research.router)
app.include_router(progress.router)
app.include_router(embedded_apps.router)
app.include_router(literature_reviews.router)
app.include_router(ingestion.router)
app.include_router(ai_ideas.router)
app.include_router(learning_tracker.router)
app.include_router(ai_learning_coach.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
