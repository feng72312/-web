from __future__ import annotations

from typing import Any

from app.core.analysis.base import AnalysisModule
from app.core.analysis.modules.dayun import DayunAnalysisModule
from app.core.analysis.modules.shishen import ShishenAnalysisModule
from app.core.analysis.modules.summary import SummaryAnalysisModule
from app.core.analysis.modules.wuxing import WuxingAnalysisModule


class AnalysisRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, AnalysisModule] = {}

    def register(self, module: AnalysisModule) -> None:
        self._modules[module.id] = module

    def unregister(self, module_id: str) -> None:
        self._modules.pop(module_id, None)

    def list_modules(self) -> list[dict[str, str | int]]:
        return sorted(
            [
                {"id": m.id, "name": m.name, "order": m.order}
                for m in self._modules.values()
            ],
            key=lambda x: x["order"],
        )

    def run_all(self, chart: dict[str, Any]) -> list[dict[str, Any]]:
        modules = sorted(self._modules.values(), key=lambda m: m.order)
        return [module.to_section(chart) for module in modules]


def build_default_registry() -> AnalysisRegistry:
    registry = AnalysisRegistry()
    registry.register(SummaryAnalysisModule())
    registry.register(WuxingAnalysisModule())
    registry.register(ShishenAnalysisModule())
    registry.register(DayunAnalysisModule())
    return registry
