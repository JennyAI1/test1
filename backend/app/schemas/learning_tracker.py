from datetime import datetime, date

from pydantic import BaseModel


class LearningGoalCreate(BaseModel):
    title: str
    description: str | None = None
    target_date: datetime | None = None
    skill_area: str | None = None


class LearningGoalResponse(BaseModel):
    id: int
    title: str
    description: str | None
    target_date: datetime | None
    status: str
    skill_area: str | None
    created_at: datetime


class SkillAreaCreate(BaseModel):
    name: str
    proficiency_level: str = "beginner"
    milestone_text: str | None = None


class SkillAreaResponse(BaseModel):
    id: int
    name: str
    proficiency_level: str
    milestone_text: str | None
    created_at: datetime


class LearningSessionCreate(BaseModel):
    embedded_app_id: int | None = None
    app_key: str
    duration_minutes: float
    topic: str
    session_notes: str = ""
    perceived_difficulty: str = "medium"
    research_topic_id: int | None = None
    research_source_id: int | None = None
    occurred_at: datetime | None = None


class LearningSessionResponse(BaseModel):
    id: int
    embedded_app_id: int | None
    app_key: str
    duration_minutes: float
    topic: str
    session_notes: str
    perceived_difficulty: str
    research_topic_id: int | None
    research_source_id: int | None
    occurred_at: datetime


class WeeklyProgressItem(BaseModel):
    week_start: date
    total_minutes: float
    by_app: dict[str, float]


class MilestoneResponse(BaseModel):
    id: int
    title: str
    status: str
    target_date: datetime | None


class GoalProgressItem(BaseModel):
    goal_id: int
    title: str
    status: str
    estimated_progress_percent: float


class SessionIdeaCorrelation(BaseModel):
    session_id: int
    idea_id: int
    score: float
    reason: str


class LearningDashboardResponse(BaseModel):
    total_learning_minutes: float
    streak_days: int
    topic_distribution: dict[str, float]
    milestones_completed: int
    active_goals_progress: list[GoalProgressItem]
    session_idea_correlations: list[SessionIdeaCorrelation]
