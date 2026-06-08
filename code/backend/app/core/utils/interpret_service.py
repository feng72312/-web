from __future__ import annotations

from typing import Any

from app.config import settings


class UtilsInterpretService:
    RAG_CATEGORY = settings.utils_rag_category

    def build_zhuge_query(self, result: dict[str, Any], question: str) -> str:
        parts = [
            "诸葛神数",
            f"报字 {result.get('chars', '')}",
            f"签号 {result.get('qianNo', '')}",
            result.get("qianText", ""),
        ]
        if question.strip():
            parts.append(f"问事 {question.strip()}")
        return "\n".join(p for p in parts if p)

    def build_jiemeng_query(self, matches: list[dict[str, str]], question: str) -> str:
        parts = ["周公解梦", f"梦境 {question.strip()}"]
        for index, row in enumerate(matches[:5], start=1):
            parts.append(f"{index}. [{row.get('section', '')}] {row.get('text', '')}")
        return "\n".join(parts)

    def build_cewen_query(self, chars: str, question: str) -> str:
        parts = ["测字", f"所测字 {chars.strip()}"]
        if question.strip():
            parts.append(f"问事 {question.strip()}")
        return "\n".join(parts)

    def build_naming_query(self, analysis: dict[str, Any], question: str) -> str:
        parts = ["起名", f"姓名 {analysis.get('fullName', '')}"]
        wuge = analysis.get("wuge") or {}
        for row in wuge.get("grids") or []:
            parts.append(
                f"{row.get('grid', '')} {row.get('strokes', '')} "
                f"({row.get('wuxing', '')}/{row.get('luck', '')})"
            )
        profile = analysis.get("baziProfile") or {}
        if profile:
            parts.append(
                "八字喜忌 "
                f"日主{profile.get('dayMasterWuxing', '')} "
                f"{profile.get('strength', '')} "
                f"宜补 {' '.join(profile.get('favoredWuxing') or [])}"
            )
        for row in (analysis.get("shuowen") or [])[:6]:
            ch = row.get("char", "")
            exp = (row.get("explanation") or "")[:80]
            if ch and exp:
                parts.append(f"《说文》{ch}: {exp}")
        if question.strip():
            parts.append(f"问事 {question.strip()}")
        return "\n".join(p for p in parts if p)

    def build_response(
        self,
        *,
        tool: str,
        payload: dict[str, Any],
        excerpts: list[dict[str, str]],
        summary: str | None,
        agent_id: str | None,
    ) -> dict[str, Any]:
        return {
            "tool": tool,
            "payload": payload,
            "excerpts": excerpts,
            "summary": summary,
            "agentId": agent_id,
        }
