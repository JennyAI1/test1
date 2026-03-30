import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import (
    AIEvaluationLog,
    LearningMilestone,
    LiteratureReview,
    Note,
    ProjectIdea,
    ProjectIdeaNoteLink,
    ProjectIdeaReviewLink,
    User,
)
from app.schemas.ai_ideas import ProjectIdeaEvidence, ProjectIdeaGenerateRequest, ProjectIdeaItem, ProjectIdeasGenerateResponse
from app.services.project_idea_service import generate_ideas
from app.services.rate_limit_service import enforce_rate_limit

router = APIRouter(prefix="/ai/project-ideas", tags=["ai-project-ideas"])


@router.post("/generate", response_model=ProjectIdeasGenerateResponse)
def generate_project_ideas(
    payload: ProjectIdeaGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enforce_rate_limit(f"{user.id}:ai_project_ideas", max_requests=5, window_seconds=60)

    reviews = db.query(LiteratureReview).filter(LiteratureReview.user_id == user.id).all()
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    milestones = db.query(LearningMilestone).filter(LearningMilestone.user_id == user.id).all()

    generated, meta = generate_ideas(reviews, notes, milestones, payload.count)

    result_items: list[ProjectIdeaItem] = []
    valid_note_ids = {note.id for note in notes}
    valid_review_ids = {review.id for review in reviews}

    for idea in generated:
        evidence = idea.get("evidence", {})
        note_ids = [note_id for note_id in evidence.get("note_ids", []) if note_id in valid_note_ids]
        review_ids = [review_id for review_id in evidence.get("review_ids", []) if review_id in valid_review_ids]

        row = ProjectIdea(
            user_id=user.id,
            title=idea["title"],
            rationale=idea["rationale"],
            estimated_difficulty=idea.get("estimated_difficulty", "medium"),
            suggested_next_step=idea.get("suggested_next_step", ""),
            evidence_json=json.dumps({"note_ids": note_ids, "review_ids": review_ids, "reason": evidence.get("reason", "")}),
            generation_model=meta.get("generation_model", "heuristic"),
        )
        db.add(row)
        db.flush()

        for note_id in note_ids:
            db.add(ProjectIdeaNoteLink(idea_id=row.id, note_id=note_id))
        for review_id in review_ids:
            db.add(ProjectIdeaReviewLink(idea_id=row.id, review_id=review_id))

        result_items.append(
            ProjectIdeaItem(
                id=row.id,
                title=row.title,
                rationale=row.rationale,
                estimated_difficulty=row.estimated_difficulty,
                suggested_next_step=row.suggested_next_step,
                evidence=ProjectIdeaEvidence(note_ids=note_ids, review_ids=review_ids, reason=evidence.get("reason", "")),
                generation_model=row.generation_model,
                created_at=row.created_at,
            )
        )

    db.add(
        AIEvaluationLog(
            user_id=user.id,
            task_type="project_idea_generation",
            prompt_template=meta.get("prompt_template", ""),
            input_snapshot=json.dumps(meta.get("input_snapshot", {})),
            output_snapshot=json.dumps(meta.get("output_snapshot", [])),
            quality_score=meta.get("quality_score"),
        )
    )

    db.commit()
    return ProjectIdeasGenerateResponse(ideas=result_items)
