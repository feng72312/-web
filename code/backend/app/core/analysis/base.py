from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AnalysisModule(ABC):
    """Pluggable analysis block. Register new modules without changing the API."""

    id: str
    name: str
    order: int = 100

    @abstractmethod
    def analyze(self, chart: dict[str, Any]) -> dict[str, Any]:
        """Return a JSON-serializable section for the frontend."""

    def to_section(self, chart: dict[str, Any]) -> dict[str, Any]:
        payload = self.analyze(chart)
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "data": payload,
        }
