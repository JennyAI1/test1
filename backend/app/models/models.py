from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entries: Mapped[list["ResearchEntry"]] = relationship(back_populates="user")
    progress_events: Mapped[list["LearningProgressEvent"]] = relationship(back_populates="user")
    literature_reviews: Mapped[list["LiteratureReview"]] = relationship(back_populates="user")
    notes: Mapped[list["Note"]] = relationship(back_populates="user")
    project_ideas: Mapped[list["ProjectIdea"]] = relationship(back_populates="user")
    sources: Mapped[list["Source"]] = relationship()


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    notes: Mapped[list["Note"]] = relationship(back_populates="topic")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    authors: Mapped[str] = mapped_column(String(1024), default="")
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="paper")
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    takeaway: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reviews: Mapped[list["LiteratureReview"]] = relationship(back_populates="source")
    notes: Mapped[list["Note"]] = relationship(back_populates="source")


class LiteratureReview(Base):
    __tablename__ = "literature_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    authors: Mapped[str] = mapped_column(String(1024), default="")
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    methods: Mapped[str] = mapped_column(Text, default="")
    findings: Mapped[str] = mapped_column(Text, default="")
    limitations: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="to-read", index=True)
    tags: Mapped[str] = mapped_column(String(1024), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="literature_reviews")
    source: Mapped[Source | None] = relationship(back_populates="reviews")
    citations: Mapped[list["ReviewCitation"]] = relationship(back_populates="review", cascade="all, delete-orphan")
    idea_links: Mapped[list["ProjectIdeaReviewLink"]] = relationship(back_populates="review", cascade="all, delete-orphan")


class ReviewCitation(Base):
    __tablename__ = "review_citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("literature_reviews.id"), index=True)
    citation_text: Mapped[str] = mapped_column(Text)
    citation_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    review: Mapped[LiteratureReview] = relationship(back_populates="citations")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True, index=True)
    review_id: Mapped[int | None] = mapped_column(ForeignKey("literature_reviews.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    body: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(String(1024), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="notes")
    topic: Mapped[Topic | None] = relationship(back_populates="notes")
    source: Mapped[Source | None] = relationship(back_populates="notes")
    idea_links: Mapped[list["ProjectIdeaNoteLink"]] = relationship(back_populates="note", cascade="all, delete-orphan")


class EmbeddedApp(Base):
    __tablename__ = "embedded_apps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    url: Mapped[str] = mapped_column(String(1024))
    category: Mapped[str] = mapped_column(String(80), index=True)
    panel_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_metadata: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usage_events: Mapped[list["EmbeddedAppUsage"]] = relationship(back_populates="app", cascade="all, delete-orphan")


class EmbeddedAppUsage(Base):
    __tablename__ = "embedded_app_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    app_id: Mapped[int] = mapped_column(ForeignKey("embedded_apps.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    session_ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    minutes_spent: Mapped[float] = mapped_column(Float, default=0)
    usage_metadata: Mapped[str] = mapped_column(Text, default="{}")

    app: Mapped[EmbeddedApp] = relationship(back_populates="usage_events")


class ProjectIdea(Base):
    __tablename__ = "project_ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    rationale: Mapped[str] = mapped_column(Text)
    estimated_difficulty: Mapped[str] = mapped_column(String(40), default="medium")
    suggested_next_step: Mapped[str] = mapped_column(Text, default="")
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    generation_model: Mapped[str] = mapped_column(String(120), default="heuristic")
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="project_ideas")
    note_links: Mapped[list["ProjectIdeaNoteLink"]] = relationship(back_populates="idea", cascade="all, delete-orphan")
    review_links: Mapped[list["ProjectIdeaReviewLink"]] = relationship(back_populates="idea", cascade="all, delete-orphan")


class ProjectIdeaNoteLink(Base):
    __tablename__ = "project_idea_note_links"

    idea_id: Mapped[int] = mapped_column(ForeignKey("project_ideas.id"), primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"), primary_key=True)

    idea: Mapped[ProjectIdea] = relationship(back_populates="note_links")
    note: Mapped[Note] = relationship(back_populates="idea_links")


class ProjectIdeaReviewLink(Base):
    __tablename__ = "project_idea_review_links"

    idea_id: Mapped[int] = mapped_column(ForeignKey("project_ideas.id"), primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("literature_reviews.id"), primary_key=True)

    idea: Mapped[ProjectIdea] = relationship(back_populates="review_links")
    review: Mapped[LiteratureReview] = relationship(back_populates="idea_links")


class LearningMilestone(Base):
    __tablename__ = "learning_milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="planned", index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class LearningReflection(Base):
    __tablename__ = "learning_reflections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    milestone_id: Mapped[int | None] = mapped_column(ForeignKey("learning_milestones.id"), nullable=True)
    reflection_text: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)




class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", index=True)
    skill_area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SkillArea(Base):
    __tablename__ = "skill_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    proficiency_level: Mapped[str] = mapped_column(String(40), default="beginner")
    milestone_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    embedded_app_id: Mapped[int | None] = mapped_column(ForeignKey("embedded_apps.id"), nullable=True, index=True)
    app_key: Mapped[str] = mapped_column(String(80), index=True)
    duration_minutes: Mapped[float] = mapped_column(Float, default=0)
    topic: Mapped[str] = mapped_column(String(255))
    session_notes: Mapped[str] = mapped_column(Text, default="")
    perceived_difficulty: Mapped[str] = mapped_column(String(40), default="medium")
    research_topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True, index=True)
    research_source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


# Legacy tables kept for API backward compatibility
class ResearchEntry(Base):
    __tablename__ = "research_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    entry_type: Mapped[str] = mapped_column(String(50), default="note")
    tags: Mapped[str] = mapped_column(String(1024), default="")
    encrypted_content: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="entries")


class LearningProgressEvent(Base):
    __tablename__ = "learning_progress_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    app_key: Mapped[str] = mapped_column(String(80), index=True)
    activity_type: Mapped[str] = mapped_column(String(80))
    minutes_spent: Mapped[float] = mapped_column(Float, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="progress_events")


class AIEvaluationLog(Base):
    __tablename__ = "ai_evaluation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(80), index=True)
    prompt_template: Mapped[str] = mapped_column(Text)
    input_snapshot: Mapped[str] = mapped_column(Text)
    output_snapshot: Mapped[str] = mapped_column(Text)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
