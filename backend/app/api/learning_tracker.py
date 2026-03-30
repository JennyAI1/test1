from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.models import LearningGoal, LearningMilestone, LearningSession, ProjectIdea, SkillArea, User
from app.schemas.learning_tracker import (
    GoalProgressItem,
    LearningDashboardResponse,
    LearningGoalCreate,
    LearningGoalResponse,
    LearningSessionCreate,
    LearningSessionResponse,
    MilestoneResponse,
    SessionIdeaCorrelation,
    SkillAreaCreate,
    SkillAreaResponse,
    WeeklyProgressItem,
)

router = APIRouter(prefix="/learning-tracker", tags=["learning-tracker"])


@router.post("/goals", response_model=LearningGoalResponse)
def create_goal(payload: LearningGoalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = LearningGoal(
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        target_date=payload.target_date,
        skill_area=payload.skill_area,
        status="active",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _goal_response(goal)


@router.get("/goals", response_model=list[LearningGoalResponse])
def list_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goals = db.query(LearningGoal).filter(LearningGoal.user_id == user.id).order_by(LearningGoal.created_at.desc()).all()
    return [_goal_response(goal) for goal in goals]


@router.post("/skill-areas", response_model=SkillAreaResponse)
def create_skill_area(payload: SkillAreaCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    skill = SkillArea(
        user_id=user.id,
        name=payload.name,
        proficiency_level=payload.proficiency_level,
        milestone_text=payload.milestone_text,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return _skill_response(skill)


@router.get("/skill-areas", response_model=list[SkillAreaResponse])
def list_skill_areas(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    skills = db.query(SkillArea).filter(SkillArea.user_id == user.id).order_by(SkillArea.created_at.desc()).all()
    return [_skill_response(skill) for skill in skills]


@router.post("/sessions", response_model=LearningSessionResponse)
def create_session(payload: LearningSessionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    session = LearningSession(
        user_id=user.id,
        embedded_app_id=payload.embedded_app_id,
        app_key=payload.app_key,
        duration_minutes=payload.duration_minutes,
        topic=payload.topic,
        session_notes=payload.session_notes,
        perceived_difficulty=payload.perceived_difficulty,
        research_topic_id=payload.research_topic_id,
        research_source_id=payload.research_source_id,
        occurred_at=payload.occurred_at or datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _session_response(session)


@router.get("/sessions", response_model=list[LearningSessionResponse])
def list_sessions(
    week_start: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(LearningSession).filter(LearningSession.user_id == user.id)
    if week_start:
        q = q.filter(LearningSession.occurred_at >= week_start, LearningSession.occurred_at < week_start + timedelta(days=7))
    sessions = q.order_by(LearningSession.occurred_at.desc()).all()
    return [_session_response(item) for item in sessions]


@router.get("/weekly-progress", response_model=WeeklyProgressItem)
def weekly_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    sessions = (
        db.query(LearningSession)
        .filter(LearningSession.user_id == user.id, LearningSession.occurred_at >= week_start)
        .all()
    )

    by_app: dict[str, float] = {}
    total = 0.0
    for session in sessions:
        by_app[session.app_key] = by_app.get(session.app_key, 0.0) + session.duration_minutes
        total += session.duration_minutes

    return WeeklyProgressItem(week_start=week_start.date(), total_minutes=round(total, 2), by_app=by_app)


@router.get("/milestones", response_model=list[MilestoneResponse])
def list_milestones(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    milestones = db.query(LearningMilestone).filter(LearningMilestone.user_id == user.id).order_by(LearningMilestone.id.desc()).all()
    return [
        MilestoneResponse(id=item.id, title=item.title, status=item.status, target_date=item.target_date)
        for item in milestones
    ]


@router.get("/dashboard", response_model=LearningDashboardResponse)
def learning_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = db.query(LearningSession).filter(LearningSession.user_id == user.id).order_by(LearningSession.occurred_at.desc()).all()
    ideas = db.query(ProjectIdea).filter(ProjectIdea.user_id == user.id).all()
    milestones = db.query(LearningMilestone).filter(LearningMilestone.user_id == user.id).all()
    goals = db.query(LearningGoal).filter(LearningGoal.user_id == user.id).all()

    total_minutes = round(sum(s.duration_minutes for s in sessions), 2)

    session_dates = sorted({s.occurred_at.date() for s in sessions}, reverse=True)
    streak = 0
    if session_dates:
        day = datetime.now(timezone.utc).date()
        allowed_start = {day, day - timedelta(days=1)}
        if session_dates[0] in allowed_start:
            cursor = session_dates[0]
            for d in session_dates:
                if d == cursor:
                    streak += 1
                    cursor -= timedelta(days=1)
                elif d < cursor:
                    break

    topic_distribution: dict[str, float] = {}
    for s in sessions:
        topic_distribution[s.topic] = topic_distribution.get(s.topic, 0.0) + s.duration_minutes

    milestones_completed = len([m for m in milestones if m.status == "completed"])

    active_goals_progress = []
    for goal in goals:
        if goal.status != "active":
            continue
        related_minutes = sum(
            s.duration_minutes for s in sessions if goal.skill_area and goal.skill_area.lower() in s.topic.lower()
        )
        progress = min(100.0, round((related_minutes / 300.0) * 100.0, 1)) if goal.skill_area else 0.0
        active_goals_progress.append(
            GoalProgressItem(goal_id=goal.id, title=goal.title, status=goal.status, estimated_progress_percent=progress)
        )

    correlations: list[SessionIdeaCorrelation] = []
    for s in sessions[:20]:
        for idea in ideas[:20]:
            score = 0.0
            reason_parts = []
            text = f"{idea.title} {idea.rationale}".lower()
            if s.topic.lower() in text:
                score += 0.6
                reason_parts.append("session topic overlaps idea text")
            if s.perceived_difficulty in idea.estimated_difficulty:
                score += 0.2
                reason_parts.append("difficulty alignment")
            if s.research_source_id is not None and str(s.research_source_id) in idea.evidence_json:
                score += 0.2
                reason_parts.append("shared research source linkage")
            if score >= 0.4:
                correlations.append(
                    SessionIdeaCorrelation(
                        session_id=s.id,
                        idea_id=idea.id,
                        score=round(score, 2),
                        reason=", ".join(reason_parts),
                    )
                )

    correlations = sorted(correlations, key=lambda item: item.score, reverse=True)[:15]

    return LearningDashboardResponse(
        total_learning_minutes=total_minutes,
        streak_days=streak,
        topic_distribution=topic_distribution,
        milestones_completed=milestones_completed,
        active_goals_progress=active_goals_progress,
        session_idea_correlations=correlations,
    )


def _goal_response(goal: LearningGoal) -> LearningGoalResponse:
    return LearningGoalResponse(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        target_date=goal.target_date,
        status=goal.status,
        skill_area=goal.skill_area,
        created_at=goal.created_at,
    )


def _skill_response(skill: SkillArea) -> SkillAreaResponse:
    return SkillAreaResponse(
        id=skill.id,
        name=skill.name,
        proficiency_level=skill.proficiency_level,
        milestone_text=skill.milestone_text,
        created_at=skill.created_at,
    )


def _session_response(item: LearningSession) -> LearningSessionResponse:
    return LearningSessionResponse(
        id=item.id,
        embedded_app_id=item.embedded_app_id,
        app_key=item.app_key,
        duration_minutes=item.duration_minutes,
        topic=item.topic,
        session_notes=item.session_notes,
        perceived_difficulty=item.perceived_difficulty,
        research_topic_id=item.research_topic_id,
        research_source_id=item.research_source_id,
        occurred_at=item.occurred_at,
    )
