from collections import Counter

from app.models.models import LiteratureReview, Note

CONFIDENCE_LABELS = [
    "High confidence: multiple sources converge on this direction.",
    "Moderate confidence: promising pattern, but evidence is still partial.",
    "Exploratory confidence: hypothesis worth testing with more data.",
]


def generate_project_suggestions(reviews: list[LiteratureReview], notes: list[Note]) -> list[dict]:
    if not reviews and not notes:
        return [
            {
                "idea": "Start a discovery sprint by collecting 10 papers and 10 notes in one theme.",
                "influencing_review_ids": [],
                "influencing_note_ids": [],
                "why_promising": "Creates the minimum evidence base needed to detect trends and gaps.",
                "confidence_language": "Exploratory confidence: limited prior evidence available.",
            }
        ]

    token_counter: Counter[str] = Counter()
    for review in reviews:
        token_counter.update(
            token.lower().strip(".,!?()[]{}\"'")
            for token in f"{review.title} {review.summary} {review.tags}".split()
            if len(token) > 3
        )
    for note in notes:
        token_counter.update(
            token.lower().strip(".,!?()[]{}\"'")
            for token in f"{note.title} {note.body} {note.tags}".split()
            if len(token) > 3
        )

    top_terms = [term for term, _ in token_counter.most_common(3)] or ["research"]

    suggestions = []
    for idx in range(3):
        term = top_terms[idx % len(top_terms)]
        influencing_reviews = [review.id for review in reviews[idx:idx + 2]]
        influencing_notes = [note.id for note in notes[idx:idx + 3]]

        suggestions.append(
            {
                "idea": f"Run a focused project on {term} combining literature synthesis with a small experiment.",
                "influencing_review_ids": influencing_reviews,
                "influencing_note_ids": influencing_notes,
                "why_promising": f"{term.title()} appears repeatedly across your reviews and notes, indicating strong thematic momentum.",
                "confidence_language": CONFIDENCE_LABELS[idx % len(CONFIDENCE_LABELS)],
            }
        )

    return suggestions
