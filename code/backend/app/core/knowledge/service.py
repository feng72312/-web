from __future__ import annotations

from typing import Any

from app.core.knowledge.keys import DEFAULT_TOPICS, build_chart_lookup_keys, build_tiaohou_key
from app.core.knowledge.keys_dayun import build_dayun_lookup_keys
from app.core.knowledge.keys_liunian import build_liunian_lookup_keys
from app.core.knowledge.keys_liuyao import LIUYAO_TOPICS, build_liuyao_lookup_keys
from app.core.knowledge.keys_meihua import MEIHUA_TOPICS, build_meihua_lookup_keys
from app.core.knowledge.keys_liuren import LIUREN_TOPICS, build_liuren_lookup_keys
from app.core.knowledge.keys_ziwei import ZIWEI_TOPICS, build_ziwei_lookup_keys
from app.core.knowledge.keys_qimen import QIMEN_TOPICS, build_qimen_lookup_keys
from app.core.knowledge.keys_fengshui import FENGSHUI_TOPICS, build_fengshui_lookup_keys
from app.core.knowledge.keys_xingming import XINGMING_TOPICS, build_xingming_lookup_keys
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

    def lookup_liuyao_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
    ) -> KnowledgeLookupResult:
        wanted = topics or list(LIUYAO_TOPICS)
        lookup_keys = build_liuyao_lookup_keys(chart)
        hits = []
        missing: list[str] = []

        if "gua" in wanted:
            key = lookup_keys.get("gua")
            if key and key.get("benGuaName"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("gua", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                    and row.get("domain") == "liuyao"
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("gua")
            else:
                missing.append("gua")

        if "yong_shen" in wanted:
            rows = [
                hit_to_public(row)
                for row in self._store.lookup(
                    "yong_shen",
                    {"relation": "general"},
                )
                if row.get("sourceTier") in INTERPRET_TIERS
                and row.get("domain") == "liuyao"
            ]
            if rows:
                hits.extend(rows)
            else:
                missing.append("yong_shen")

        return KnowledgeLookupResult(
            lookupKeys=lookup_keys,
            hits=hits,
            missingTopics=missing,
        )

    def lookup_ziwei_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
    ) -> KnowledgeLookupResult:
        wanted = topics or list(ZIWEI_TOPICS)
        lookup_keys = build_ziwei_lookup_keys(chart)
        hits = []
        missing: list[str] = []

        if "ziwei_palace" in wanted:
            key = lookup_keys.get("ziwei_palace")
            if key and key.get("palaceName"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("ziwei_palace", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("ziwei_palace")
            else:
                missing.append("ziwei_palace")

        if "ziwei_star" in wanted:
            star_hits: list = []
            seen: set[str] = set()
            for key in lookup_keys.get("ziwei_star") or []:
                for row in self._store.lookup("ziwei_star", key):
                    if row.get("sourceTier") not in INTERPRET_TIERS:
                        continue
                    rid = str(row.get("id", ""))
                    if rid in seen:
                        continue
                    seen.add(rid)
                    star_hits.append(hit_to_public(row))
            if star_hits:
                hits.extend(star_hits)
            else:
                missing.append("ziwei_star")

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

    def lookup_fengshui_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
    ) -> KnowledgeLookupResult:
        wanted = topics or list(FENGSHUI_TOPICS)
        lookup_keys = build_fengshui_lookup_keys(chart)
        hits: list = []
        missing: list[str] = []

        if "scene" in wanted:
            key = lookup_keys.get("scene")
            if key:
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("scene", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("scene")

        if "shan" in wanted:
            key = lookup_keys.get("shan")
            if key and key.get("mountainId"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("shan", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("shan")

        if "ming_gua" in wanted:
            key = lookup_keys.get("ming_gua")
            if key and key.get("guaNumber"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("ming_gua", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("ming_gua")

        if "period" in wanted:
            key = lookup_keys.get("period")
            if key and key.get("period"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("period", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("period")

        for label in lookup_keys.get("ji_xiong_labels", []):
            if "ji_xiong_fang" not in wanted:
                break
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("ji_xiong_fang", {"type": "", "label": label})
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)

        for star in lookup_keys.get("stars", []):
            if "star" not in wanted:
                break
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("star", {"starNumber": str(star)})
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)

        return KnowledgeLookupResult(
            lookupKeys=lookup_keys,
            hits=hits,
            missingTopics=missing,
        )

    def lookup_xingming_chart(
        self,
        chart: dict[str, Any],
        topics: list[str] | None = None,
    ) -> KnowledgeLookupResult:
        wanted = topics or list(XINGMING_TOPICS)
        lookup_keys = build_xingming_lookup_keys(chart)
        hits: list = []
        missing: list[str] = []

        for entry in lookup_keys.get("shou_ming") or []:
            if "shou_ming" not in wanted:
                break
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("shou_ming", entry)
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)

        if "palace" in wanted:
            key = lookup_keys.get("palace")
            if key and key.get("branch"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("palace", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)
                else:
                    missing.append("palace")

        if "tai_sui" in wanted:
            key = lookup_keys.get("tai_sui")
            if key and key.get("branch"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("tai_sui", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)

        for entry in lookup_keys.get("si_yu") or []:
            if "si_yu" not in wanted:
                break
            rows = [
                hit_to_public(row)
                for row in self._store.lookup("si_yu", entry)
                if row.get("sourceTier") in INTERPRET_TIERS
            ]
            if rows:
                hits.extend(rows)

        if "mansion" in wanted:
            key = lookup_keys.get("mansion")
            if key and key.get("mansion"):
                rows = [
                    hit_to_public(row)
                    for row in self._store.lookup("mansion", key)
                    if row.get("sourceTier") in INTERPRET_TIERS
                ]
                if rows:
                    hits.extend(rows)

        return KnowledgeLookupResult(
            lookupKeys=lookup_keys,
            hits=hits,
            missingTopics=missing,
        )

    def resolve_for_xingming(
        self,
        chart: dict[str, Any],
        *,
        topics: list[str] | None = None,
        token_budget: int = 1500,
    ) -> CompressedContext:
        result = self.lookup_xingming_chart(chart, topics=topics)
        text_len = sum(len(hit.summary) for hit in result.hits)
        return CompressedContext(
            lookupKeys=result.lookupKeys,
            hits=result.hits,
            missingTopics=result.missingTopics,
            tokenEstimate=text_len,
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

    def resolve_for_liuyao(
        self,
        chart: dict[str, Any],
        *,
        topics: list[str] | None = None,
        token_budget: int = 1500,
    ) -> CompressedContext:
        result = self.lookup_liuyao_chart(chart, topics=topics)
        text_len = sum(len(hit.summary) for hit in result.hits)
        return CompressedContext(
            lookupKeys=result.lookupKeys,
            hits=result.hits,
            missingTopics=result.missingTopics,
            tokenEstimate=text_len,
        )

    def resolve_for_ziwei(
        self,
        chart: dict[str, Any],
        *,
        topics: list[str] | None = None,
        token_budget: int = 1500,
    ) -> CompressedContext:
        result = self.lookup_ziwei_chart(chart, topics=topics)
        text_len = sum(len(hit.summary) for hit in result.hits)
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
