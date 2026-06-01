from __future__ import annotations

from typing import Any

from app.core.knowledge.keys import DEFAULT_TOPICS, build_chart_lookup_keys, build_tiaohou_key
from app.core.knowledge.keys_dayun import build_dayun_lookup_keys
from app.core.knowledge.keys_liunian import build_liunian_lookup_keys
from app.core.knowledge.keys_meihua import MEIHUA_TOPICS, build_meihua_lookup_keys
from app.core.knowledge.keys_liuren import LIUREN_TOPICS, build_liuren_lookup_keys
from app.core.knowledge.keys_qimen import QIMEN_TOPICS, build_qimen_lookup_keys
from app.core.knowledge.models import CompressedContext, KnowledgeLookupResult
from app.core.knowledge.store import KnowledgeStore
from app.core.knowledge.tiers import INTERPRET_TIERS, allow_safe_auto_answer, hit_to_public
from app.core.paipan.interactions import GAN_HE, ZHI_CHONG, ZHI_HAI, ZHI_HE

PILLAR_KEYS = ("year", "month", "day", "hour")


class KnowledgeService:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    @property
    def store(self) -> KnowledgeStore:
        return self._store

    @property
    def enabled(self) -> bool:
        return self._store.enabled

    def lookup_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
        *,
        question: str = "",
    ) -> KnowledgeLookupResult:
        wanted = topics or list(DEFAULT_TOPICS)
        lookup_keys = build_chart_lookup_keys(chart)
        hits = []
        missing: list[str] = []

        if "dayun" in wanted:
            dayun_keys = build_dayun_lookup_keys(question)
            lookup_keys["dayun"] = dayun_keys
            dayun_hits: list = []
            seen_dayun: set[str] = set()
            for key in dayun_keys:
                for row in self._store.lookup("dayun", key):
                    if row.get("sourceTier") not in INTERPRET_TIERS:
                        continue
                    rid = str(row.get("id", ""))
                    if rid in seen_dayun:
                        continue
                    seen_dayun.add(rid)
                    dayun_hits.append(hit_to_public(row))
            if dayun_hits:
                hits.extend(dayun_hits)
            else:
                missing.append("dayun")

        if "liunian" in wanted:
            liunian_keys = build_liunian_lookup_keys(question)
            lookup_keys["liunian"] = liunian_keys
            liunian_hits: list = []
            seen_ln: set[str] = set()
            for key in liunian_keys:
                for row in self._store.lookup("liunian", key):
                    if row.get("sourceTier") not in INTERPRET_TIERS:
                        continue
                    rid = str(row.get("id", ""))
                    if rid in seen_ln:
                        continue
                    seen_ln.add(rid)
                    liunian_hits.append(hit_to_public(row))
            if liunian_hits:
                hits.extend(liunian_hits)
            else:
                missing.append("liunian")

        if "tiaohou" in wanted:
            key = lookup_keys.get("tiaohou")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("tiaohou", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("tiaohou")
            else:
                missing.append("tiaohou")

        if "ganzhi" in wanted:
            ganzhi_hits = self._lookup_ganzhi(chart)
            if ganzhi_hits:
                hits.extend(ganzhi_hits)
            else:
                missing.append("ganzhi")

        if "shishen" in wanted:
            missing.append("shishen")

        safe_hits = [hit for hit in hits if hit.safeAutoAnswer]
        auto_parts = [hit.summary for hit in safe_hits]
        auto_summary = "；".join(auto_parts) if auto_parts else None
        direct = None
        if len(safe_hits) == 1 and safe_hits[0].topic == "tiaohou":
            direct = self.build_direct_answer_text(chart)

        return KnowledgeLookupResult(
            lookupKeys=lookup_keys,
            hits=hits,
            missingTopics=missing,
            autoAnswerSummary=auto_summary,
            directAnswer=direct if auto_parts else None,
        )

    def lookup_meihua_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
    ) -> KnowledgeLookupResult:
        wanted = topics or list(MEIHUA_TOPICS)
        lookup_keys = build_meihua_lookup_keys(chart)
        hits = []
        missing: list[str] = []

        if "gua" in wanted:
            key = lookup_keys.get("gua")
            if key and key.get("benGuaName"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("gua", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("gua")
            else:
                missing.append("gua")

        if "ti_yong" in wanted:
            key = lookup_keys.get("ti_yong")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("ti_yong", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    rows_general = [
                        hit_to_public(row)
                        for row in self._store.lookup(
                            "ti_yong",
                            {"tiGua": "", "yongGua": "", "relation": "general"},
                        )
                        if row.get("sourceTier") in INTERPRET_TIERS
                    ]
                    if rows_general:
                        hits.extend(rows_general)
                    else:
                        missing.append("ti_yong")
            else:
                missing.append("ti_yong")

        if "leixiang" in wanted:
            key = lookup_keys.get("leixiang")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("leixiang", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("leixiang")
            else:
                missing.append("leixiang")

        return KnowledgeLookupResult(
            lookupKeys=lookup_keys,
            hits=hits,
            missingTopics=missing,
        )

    def lookup_qimen_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
    ) -> KnowledgeLookupResult:
        wanted = topics or list(QIMEN_TOPICS)
        lookup_keys = build_qimen_lookup_keys(chart)
        hits = []
        missing: list[str] = []

        if "ju" in wanted:
            key = lookup_keys.get("ju")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("ju", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("ju")
            else:
                missing.append("ju")

        if "yong" in wanted:
            key = lookup_keys.get("yong")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("yong", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("yong")
            else:
                missing.append("yong")

        for door in lookup_keys.get("doors", []):
            if "men" not in wanted:
                break
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("men", {"door": door})
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)
        if "men" in wanted and not any(
            h.topic == "men" for h in hits
        ):
            if lookup_keys.get("doors"):
                missing.append("men")

        for star in lookup_keys.get("stars", []):
            if "xing" not in wanted:
                break
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("xing", {"star": star})
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)
        if "xing" in wanted and not any(h.topic == "xing" for h in hits):
            if lookup_keys.get("stars"):
                missing.append("xing")

        for god in lookup_keys.get("gods", []):
            if "shen" not in wanted:
                break
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("shen", {"god": god})
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)
        if "shen" in wanted and not any(h.topic == "shen" for h in hits):
            if lookup_keys.get("gods"):
                missing.append("shen")

        return KnowledgeLookupResult(
            lookupKeys=lookup_keys,
            hits=hits,
            missingTopics=missing,
        )

    def lookup_liuren_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
    ) -> KnowledgeLookupResult:
        wanted = topics or list(LIUREN_TOPICS)
        lookup_keys = build_liuren_lookup_keys(chart)
        hits = []
        missing: list[str] = []

        if "yue_jiang" in wanted:
            key = lookup_keys.get("yue_jiang")
            if key and key.get("yueJiang"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("yue_jiang", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("yue_jiang")

        if "ge_ju" in wanted:
            key = lookup_keys.get("ge_ju")
            if key and key.get("name"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("ge_ju", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("ge_ju")

        if "tian_jiang" in wanted:
            key = lookup_keys.get("tian_jiang")
            if key and key.get("general"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("tian_jiang", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("tian_jiang")

        if "si_ke" in wanted:
            key = lookup_keys.get("si_ke")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("si_ke", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("si_ke")

        if "san_chuan" in wanted:
            key = lookup_keys.get("san_chuan")
            if key and key.get("role"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("san_chuan", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("san_chuan")

        if "jinkou" in wanted and lookup_keys.get("jinkou"):
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("jinkou", lookup_keys["jinkou"])
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)
            else:
                missing.append("jinkou")

        if "yong" in wanted:
            key = lookup_keys.get("yong")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("yong", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("yong")

        if "shen_sha" in wanted:
            lr = chart.get("liuren") or {}
            for sha_name in (lr.get("shenSha") or {}):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("shen_sha", {"name": sha_name})
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)

        return KnowledgeLookupResult(
            lookupKeys=lookup_keys,
            hits=hits,
            missingTopics=missing,
        )

    def resolve_for_liuren(
        self,
        chart: dict[str, Any],
        *,
        topics: list[str] | None = None,
        token_budget: int = 1500,
    ) -> CompressedContext:
        result = self.lookup_liuren_chart(chart, topics=topics)
        text_len = sum(len(hit.summary) for hit in result.hits)
        return CompressedContext(
            lookupKeys=result.lookupKeys,
            hits=result.hits,
            missingTopics=result.missingTopics,
            tokenEstimate=text_len,
        )

    def resolve_for_qimen(
        self,
        chart: dict[str, Any],
        *,
        topics: list[str] | None = None,
        token_budget: int = 1500,
    ) -> CompressedContext:
        result = self.lookup_qimen_chart(chart, topics=topics)
        text_len = sum(len(hit.summary) for hit in result.hits)
        for hit in result.hits:
            for claim in hit.claims:
                text_len += len(claim.quote[:120])
        return CompressedContext(
            lookupKeys=result.lookupKeys,
            hits=result.hits,
            missingTopics=result.missingTopics,
            tokenEstimate=text_len,
        )

    def resolve_for_meihua(
        self,
        chart: dict[str, Any],
        *,
        topics: list[str] | None = None,
        token_budget: int = 1500,
    ) -> CompressedContext:
        result = self.lookup_meihua_chart(chart, topics=topics)
        text_len = sum(len(hit.summary) for hit in result.hits)
        for hit in result.hits:
            for claim in hit.claims:
                text_len += len(claim.quote[:120])
        return CompressedContext(
            lookupKeys=result.lookupKeys,
            hits=result.hits,
            missingTopics=result.missingTopics,
            tokenEstimate=text_len,
        )

    def resolve_for_chart(
        self,
        chart: dict[str, Any],
        *,
        topics: list[str] | None = None,
        token_budget: int = 1500,
        question: str = "",
    ) -> CompressedContext:
        result = self.lookup_chart(chart, topics=topics, question=question)
        text_len = sum(len(hit.summary) for hit in result.hits)
        for hit in result.hits:
            for claim in hit.claims:
                text_len += len(claim.quote[:120])
        return CompressedContext(
            lookupKeys=result.lookupKeys,
            hits=result.hits,
            missingTopics=result.missingTopics,
            autoAnswerSummary=result.autoAnswerSummary,
            directAnswer=result.directAnswer,
            tokenEstimate=text_len,
        )

    def _lookup_ganzhi(self, chart: dict[str, Any]) -> list:
        pillars = chart.get("pillars") or {}
        gans = {key: pillars.get(key, {}).get("gan", "") for key in PILLAR_KEYS}
        zhis = {key: pillars.get(key, {}).get("zhi", "") for key in PILLAR_KEYS}
        hits = []

        for a, b in GAN_HE:
            if a in gans.values() and b in gans.values():
                rows = self._store.lookup("ganzhi", {"type": "ganHe", "a": a, "b": b})
                hits.extend(hit_to_public(row) for row in rows)

        for a, b in ZHI_CHONG:
            if a in zhis.values() and b in zhis.values():
                rows = self._store.lookup("ganzhi", {"type": "zhiChong", "a": a, "b": b})
                hits.extend(hit_to_public(row) for row in rows)

        for a, b in ZHI_HE:
            if a in zhis.values() and b in zhis.values():
                rows = self._store.lookup("ganzhi", {"type": "zhiHe", "a": a, "b": b})
                hits.extend(hit_to_public(row) for row in rows)

        for a, b in ZHI_HAI:
            if a in zhis.values() and b in zhis.values():
                rows = self._store.lookup("ganzhi", {"type": "zhiHai", "a": a, "b": b})
                hits.extend(hit_to_public(row) for row in rows)

        return hits

    def build_direct_answer_text(self, chart: dict[str, Any]) -> str | None:
        if not self.enabled:
            return None
        try:
            key = build_tiaohou_key(chart)
        except ValueError:
            return None
        rows = self._store.lookup("tiaohou", key)
        if not rows:
            return None
        row = rows[0]
        if not allow_safe_auto_answer(row):
            return None
        month_label = key.get("monthLabel") or key.get("monthZhi", "")
        day_gan = key.get("dayGan", "")
        return f"{day_gan}日主生于{month_label}({key.get('monthZhi', '')}月): {row.get('summary', '')}"
