import json
from pathlib import Path

from openai import OpenAI

from app.core.config import settings
from app.models.models import EmbeddedApp, LearningGoal, LearningSession, LiteratureReview, ProjectIdea

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
SYSTEM_TEMPLATE = (PROMPT_DIR / "learning_coach_system_prompt.txt").read_text()
USER_TEMPLATE = (PROMPT_DIR / "learning_coach_user_prompt.txt").read_text()


def _fallback(context: dict) -> list[dict]:
    goals = context.get("active_goals") or []
    apps = context.get("embedded_apps") or []
    themes = context.get("themes") or ["research methodology"]

    recommendations = []
    for idx in range(3):
        goal = goals[idx % len(goals)]["title"] if goals else "Strengthen research execution"
        app = apps[idx % len(apps)]["title"] if apps else "ArXiv"
        theme = themes[idx % len(themes)]
        recommendations.append(
            {
                "next_skill": f"Deepen {theme}",
                "recommended_embedded_app": app,
                "weekly_plan": f"Spend 3 sessions this week using {app} to practice {theme} and summarize outcomes.",
                "why_it_matters": f"This improves progress toward '{goal}' and increases readiness for higher-quality future projects.",
            }
        )
    return recommendations


def generate_learning_coach_recommendations(
    sessions: list[LearningSession],
    goals: list[LearningGoal],
    reviews: list[LiteratureReview],
    ideas: list[ProjectIdea],
    apps: list[EmbeddedApp],
) -> tuple[list[dict], dict]:
    themes = []
    for review in reviews[:20]:
        themes.extend([token for token in review.tags.split(",") if token])

    context = {
        "learning_sessions": [
            {
                "app_key": s.app_key,
                "duration_minutes": s.duration_minutes,
                "topic": s.topic,
                "difficulty": s.perceived_difficulty,
            }
            for s in sessions[:40]
        ],
        "active_goals": [
            {"title": g.title, "skill_area": g.skill_area, "status": g.status}
            for g in goals
            if g.status == "active"
        ],
        "literature_reviews": [
            {"title": r.title, "tags": r.tags, "status": r.status}
            for r in reviews[:25]
        ],
        "project_ideas": [
            {"title": i.title, "difficulty": i.estimated_difficulty, "next_step": i.suggested_next_step}
            for i in ideas[:25]
        ],
        "embedded_apps": [{"title": a.title, "category": a.category} for a in apps[:20]],
        "themes": themes,
    }

    if not settings.openai_api_key:
        recs = _fallback(context)
        return recs, {
            "prompt_template": "fallback-learning-coach",
            "input_snapshot": context,
            "output_snapshot": recs,
            "quality_score": 0.7,
            "generation_model": "heuristic",
        }

    client = OpenAI(api_key=settings.openai_api_key)
    user_prompt = USER_TEMPLATE.replace("{{CONTEXT_JSON}}", json.dumps(context))

    schema = {
        "type": "object",
        "properties": {
            "recommendations": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "next_skill": {"type": "string"},
                        "recommended_embedded_app": {"type": "string"},
                        "weekly_plan": {"type": "string"},
                        "why_it_matters": {"type": "string"},
                    },
                    "required": ["next_skill", "recommended_embedded_app", "weekly_plan", "why_it_matters"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["recommendations"],
        "additionalProperties": False,
    }

    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_TEMPLATE},
            {"role": "user", "content": user_prompt},
        ],
        text={"format": {"type": "json_schema", "name": "learning_coach", "schema": schema, "strict": True}},
    )

    recs = json.loads(response.output_text)["recommendations"]
    return recs, {
        "prompt_template": f"SYSTEM:\n{SYSTEM_TEMPLATE}\n\nUSER:\n{USER_TEMPLATE}",
        "input_snapshot": context,
        "output_snapshot": recs,
        "quality_score": 0.9,
        "generation_model": settings.openai_model,
    }
