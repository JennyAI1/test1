from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

BASE_URL = "https://api.crossref.org"


@dataclass
class CrossrefClient:
    mailto: str | None = None
    timeout: int = 30

    def _params(self, **kwargs: Any) -> dict[str, Any]:
        params = dict(kwargs)
        if self.mailto:
            params["mailto"] = self.mailto
        return params

    def lookup_doi(self, doi: str) -> dict[str, Any] | None:
        clean = doi.strip()
        if not clean:
            return None
        response = requests.get(
            f"{BASE_URL}/works/{clean}",
            params=self._params(),
            timeout=self.timeout,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json().get("message")
