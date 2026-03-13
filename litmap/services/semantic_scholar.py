from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

BASE_URL = "https://api.semanticscholar.org/graph/v1"
DEFAULT_FIELDS = (
    "paperId,title,abstract,year,venue,url,citationCount,influentialCitationCount,"
    "referenceCount,authors,externalIds,references.paperId,references.title,citations.paperId,citations.title"
)


@dataclass
class SemanticScholarClient:
    timeout: int = 30
    api_key: str | None = None

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def search_papers(self, query: str, limit: int = 100, fields: str = DEFAULT_FIELDS) -> list[dict[str, Any]]:
        response = requests.get(
            f"{BASE_URL}/paper/search",
            params={"query": query, "limit": limit, "fields": fields},
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("data", [])

    def get_paper(self, paper_id: str, fields: str = DEFAULT_FIELDS) -> dict[str, Any]:
        response = requests.get(
            f"{BASE_URL}/paper/{paper_id}",
            params={"fields": fields},
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def find_by_doi(self, doi: str, fields: str = DEFAULT_FIELDS) -> dict[str, Any] | None:
        normalized = doi.strip()
        if not normalized:
            return None
        response = requests.get(
            f"{BASE_URL}/paper/DOI:{normalized}",
            params={"fields": fields},
            headers=self._headers(),
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def expand_neighborhood(self, seeds: list[dict[str, Any]], max_refs: int = 25, max_citations: int = 25) -> list[dict[str, Any]]:
        papers_by_id: dict[str, dict[str, Any]] = {}

        def maybe_fetch(paper_id: str | None) -> None:
            if not paper_id or paper_id in papers_by_id:
                return
            paper = self.get_paper(paper_id)
            papers_by_id[paper_id] = paper

        for seed in seeds:
            seed_id = seed.get("paperId")
            if not seed_id:
                continue
            papers_by_id[seed_id] = seed
            for ref in seed.get("references", [])[:max_refs]:
                maybe_fetch(ref.get("paperId"))
            for cit in seed.get("citations", [])[:max_citations]:
                maybe_fetch(cit.get("paperId"))

        return list(papers_by_id.values())
