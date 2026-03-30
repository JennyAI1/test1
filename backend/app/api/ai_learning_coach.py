import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import AIEvaluationLog, EmbeddedApp, LearningGoal, LearningSession, LiteratureReview, ProjectIdea, User
from app.schemas.ai_learning_coach import LearningCoachRecommendation, LearningCoachResponse
from app.services.learning_coach_service import generate_learning_coach_recommendations
from app.services.rate_limit_service import enforce_rate_limit

router = APIRouter(prefix="/ai/learning-coach", tags=["ai-learning-coach"])


@router.get("/recommendations", response_model=LearningCoachResponse)
def get_learning_coach_recommendations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    enforce_rate_limit(f"{user.id}:ai_learning_coach", max_requests=5, window_seconds=60)
    sessions = db.query(LearningSession).filter(LearningSession.user_id == user.id).order_by(LearningSession.occurred_at.desc()).all()
    goals = db.query(LearningGoal).filter(LearningGoal.user_id == user.id).all()
    reviews = db.query(LiteratureReview).filter(LiteratureReview.user_id == user.id).all()
    ideas = db.query(ProjectIdea).filter(ProjectIdea.user_id == user.id).all()
    apps = db.query(EmbeddedApp).filter(EmbeddedApp.user_id == user.id, EmbeddedApp.is_active.is_(True)).all()

    recs, meta = generate_learning_coach_recommendations(sessions, goals, reviews, ideas, apps)

    db.add(
        AIEvaluationLog(
            user_id=user.id,
            task_type="learning_coach",
            prompt_template=meta.get("prompt_template", ""),
            input_snapshot=json.dumps(meta.get("input_snapshot", {})),
            output_snapshot=json.dumps(meta.get("output_snapshot", [])),
            quality_score=meta.get("quality_score"),
        )
    )
    db.commit()

    return LearningCoachResponse(recommendations=[LearningCoachRecommendation(**item) for item in recs])
