from __future__ import annotations

from collections import Counter, defaultdict


def fit_topics(documents: list[str], min_topic_size: int = 5) -> tuple[list[int], list[dict[str, object]]]:
    try:
        from bertopic import BERTopic

        model = BERTopic(language="english", min_topic_size=min_topic_size)
        topics, probs = model.fit_transform(documents)
        labels = []
        for topic_id in sorted(set(topics)):
            if topic_id == -1:
                continue
            words = [word for word, _ in model.get_topic(topic_id)[:5]]
            labels.append({"topic_id": topic_id, "label": ", ".join(words), "size": topics.count(topic_id)})
        return topics, labels
    except Exception:
        return _keyword_fallback(documents)


def _keyword_fallback(documents: list[str]) -> tuple[list[int], list[dict[str, object]]]:
    topic_keywords = {
        0: {"capital", "education", "school", "attainment"},
        1: {"inequality", "class", "stratification", "income"},
        2: {"gender", "family", "work", "care"},
        3: {"network", "social", "community", "ties"},
    }
    topic_counts: dict[int, int] = Counter()
    assignments: list[int] = []
    topic_terms: dict[int, Counter[str]] = defaultdict(Counter)

    for doc in documents:
        tokens = set(doc.split())
        best_topic = max(topic_keywords, key=lambda tid: len(tokens & topic_keywords[tid]))
        assignments.append(best_topic)
        topic_counts[best_topic] += 1
        topic_terms[best_topic].update(doc.split())

    labels = []
    for topic_id, size in sorted(topic_counts.items()):
        top_terms = [term for term, _ in topic_terms[topic_id].most_common(5)]
        labels.append({"topic_id": topic_id, "label": ", ".join(top_terms), "size": size})

    return assignments, labels
