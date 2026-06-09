from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/platform", tags=["platform"])

_BLUEPRINT_PATH = Path(__file__).resolve().parents[2] / "docs" / "module_blueprint.json"


@router.get("/blueprint")
async def module_blueprint() -> dict[str, Any]:
    if not _BLUEPRINT_PATH.is_file():
        return {"version": "0", "modules": {}, "layers": {}}
    return json.loads(_BLUEPRINT_PATH.read_text(encoding="utf-8"))


@router.get("/quality-metrics")
async def quality_metrics() -> dict[str, Any]:
    return {
        "contest8Scope": "chart_disciplines_only",
        "questionLevelFeedback": True,
        "metrics": [
            "first_token_ms",
            "interpret_success_rate",
            "consensus_agreement_rate",
            "evidence_hit_rate",
            "user_adoption_rate",
        ],
    }

