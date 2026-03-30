import json
from collections import Counter
from pathlib import Path

from openai import OpenAI

from app.core.config import settings
from app.models.models import LearningMilestone, LiteratureReview, Note

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
SYSTEM_TEMPLATE = (PROMPT_DIR / "project_idea_system_prompt.txt").read_text()
USER_TEMPLATE = (PROMPT_DIR / "project_idea_user_prompt.txt").read_text()


def _extract_theme_tokens(reviews: list[LiteratureReview], notes: list[Note]) -> list[str]:
    tokens = Counter()
    for review in reviews:
        for token in f"{review.title} {review.tags}".lower().replace(",", " ").split():
            if len(token) > 3:
                tokens[token] += 1
    for note in notes:
        for token in f"{note.title} {note.tags}".lower().replace(",", " ").split():
            if len(token) > 3:
                tokens[token] += 1
    return [t for t, _ in tokens.most_common(8)]


def _build_context(reviews: list[LiteratureReview], notes: list[Note], milestones: list[LearningMilestone]) -> dict:
    recurring_themes = _extract_theme_tokens(reviews, notes)

    missing_methods_reviews = [r.id for r in reviews if not r.methods.strip()]
    missing_limitations_reviews = [r.id for r in reviews if not r.limitations.strip()]
    sparse_notes = [n.id for n in notes if len(n.body.split()) < 30]

    gaps = {
        "reviews_missing_methods": missing_methods_reviews,
        "reviews_missing_limitations": missing_limitations_reviews,
        "short_notes": sparse_notes,
    }

    topic_pool = recurring_themes[:6]
    underexplored_combinations = []
    for i in range(len(topic_pool)):
        for j in range(i + 1, len(topic_pool)):
            underexplored_combinations.append(f"{topic_pool[i]} + {topic_pool[j]}")
    underexplored_combinations = underexplored_combinations[:6]

    learning_goals = [m.title for m in milestones if m.status in {"planned", "in_progress"}]

    return {
        "reviews": [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary,
                "tags": r.tags,
                "status": r.status,
            }
            for r in reviews[:30]
        ],
        "notes": [
            {
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "tags": n.tags,
            }
            for n in notes[:30]
        ],
        "analysis": {
            "gaps": gaps,
            "recurring_themes": recurring_themes,
            "underexplored_combinations": underexplored_combinations,
            "learning_goals": learning_goals,
        },
    }


def _fallback_generate(context: dict, count: int) -> list[dict]:
    themes = context["analysis"]["recurring_themes"] or ["research-planning"]
    combos = context["analysis"]["underexplored_combinations"] or ["theme + evaluation"]
    goals = context["analysis"]["learning_goals"] or ["Strengthen research fundamentals"]

    note_ids = [n["id"] for n in context["notes"]]
    review_ids = [r["id"] for r in context["reviews"]]

    ideas = []
    for idx in range(count):
        theme = themes[idx % len(themes)]
        combo = combos[idx % len(combos)]
        goal = goals[idx % len(goals)]
        ideas.append(
            {
                "title": f"{theme.title()} for {goal}",
                "rationale": f"Closes documentation gaps while exploring underexplored combination: {combo}.",
                "estimated_difficulty": ["low", "medium", "high"][idx % 3],
                "suggested_next_step": "Outline hypothesis, dataset, and success metric for a 2-week sprint.",
                "evidence": {
                    "note_ids": note_ids[idx:idx + 2],
                    "review_ids": review_ids[idx:idx + 2],
                    "reason": "Grounded in recurring themes and pending learning goals.",
                },
            }
        )
    return ideas


def evaluate_ideas(ideas: list[dict], context: dict) -> float:
    score = 0.0
    goals = set(context["analysis"]["learning_goals"])
    for idea in ideas:
        rationale = idea.get("rationale", "").lower()
        if any(keyword in rationale for keyword in ["gap", "theme", "underexplored", "goal"]):
            score += 1
        if idea.get("estimated_difficulty") in {"low", "medium", "high"}:
            score += 0.5
        if idea.get("evidence", {}).get("note_ids") or idea.get("evidence", {}).get("review_ids"):
            score += 0.5
        if goals and any(goal.lower()[:20] in rationale for goal in goals):
            score += 0.5
    return round(score / max(len(ideas), 1), 2)


def generate_ideas(
    reviews: list[LiteratureReview],
    notes: list[Note],
    milestones: list[LearningMilestone],
    count: int = 5,
) -> tuple[list[dict], dict]:
    count = max(1, min(count, 10))
    context = _build_context(reviews, notes, milestones)

    user_prompt = USER_TEMPLATE.replace("{{CONTEXT_JSON}}", json.dumps(context)).replace("{{COUNT}}", str(count))

    if not settings.openai_api_key:
        ideas = _fallback_generate(context, count)
        return ideas, {
            "prompt_template": "fallback",
            "input_snapshot": context,
            "output_snapshot": ideas,
            "quality_score": evaluate_ideas(ideas, context),
            "generation_model": "heuristic",
        }

    client = OpenAI(api_key=settings.openai_api_key)
    schema = {
        "type": "object",
        "properties": {
            "ideas": {
                "type": "array",
                "minItems": count,
                "maxItems": count,
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "rationale": {"type": "string"},
                        "estimated_difficulty": {"type": "string", "enum": ["low", "medium", "high"]},
                        "suggested_next_step": {"type": "string"},
                        "evidence": {
                            "type": "object",
                            "properties": {
                                "note_ids": {"type": "array", "items": {"type": "integer"}},
                                "review_ids": {"type": "array", "items": {"type": "integer"}},
                                "reason": {"type": "string"},
                            },
                            "required": ["note_ids", "review_ids", "reason"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["title", "rationale", "estimated_difficulty", "suggested_next_step", "evidence"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["ideas"],
        "additionalProperties": False,
    }

    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_TEMPLATE},
            {"role": "user", "content": user_prompt},
        ],
        text={"format": {"type": "json_schema", "name": "project_ideas", "schema": schema, "strict": True}},
    )

    ideas = json.loads(response.output_text)["ideas"]
    return ideas, {
        "prompt_template": f"SYSTEM:\n{SYSTEM_TEMPLATE}\n\nUSER:\n{USER_TEMPLATE}",
        "input_snapshot": context,
        "output_snapshot": ideas,
        "quality_score": evaluate_ideas(ideas, context),
        "generation_model": settings.openai_model,
    }
