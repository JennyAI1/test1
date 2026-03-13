from __future__ import annotations

import re

_DEFAULT_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "for",
    "on",
    "by",
    "with",
    "is",
    "are",
    "that",
    "this",
}


def _load_spacy():
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except Exception:
        return None


_NLP = _load_spacy()


def clean_text(text: str) -> str:
    raw = (text or "").strip().lower()
    raw = re.sub(r"\s+", " ", raw)
    if not raw:
        return ""

    if _NLP is None:
        tokens = re.findall(r"[a-zA-Z]+", raw)
        return " ".join(t for t in tokens if t not in _DEFAULT_STOPWORDS)

    doc = _NLP(raw)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]
    return " ".join(tokens)


def combine_title_abstract(title: str | None, abstract: str | None) -> str:
    return " ".join(part for part in [title or "", abstract or ""] if part).strip()
