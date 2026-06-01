from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.knowledge.tiers import allow_safe_auto_answer

logger = logging.getLogger(__name__)


def _canonical_key(topic: str, lookup_key: dict[str, str]) -> tuple[str, ...]:
    if topic == "tiaohou":
        return (topic, lookup_key.get("dayGan", ""), lookup_key.get("monthZhi", ""))
    if topic == "shishen":
        return (topic, lookup_key.get("shishen", ""))
    if topic == "ganzhi":
        return (
            topic,
            lookup_key.get("type", ""),
            lookup_key.get("a", ""),
            lookup_key.get("b", ""),
        )
    if topic == "gua":
        return (topic, lookup_key.get("benGuaName", ""))
    if topic == "ti_yong":
        return (
            topic,
            lookup_key.get("tiGua", ""),
            lookup_key.get("yongGua", ""),
            lookup_key.get("relation", ""),
        )
    if topic == "leixiang":
        return (
            topic,
            lookup_key.get("tiElement", ""),
            lookup_key.get("yongElement", ""),
        )
    if topic == "liunian":
        return (topic, lookup_key.get("category", ""))
    if topic == "dayun":
        return (topic, lookup_key.get("category", ""))
    return (topic, json.dumps(lookup_key, sort_keys=True, ensure_ascii=False))


class KnowledgeStore:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._nodes: list[dict] = []
        self._index: dict[tuple[str, ...], list[dict]] = {}
        self._manifest: dict = {}
        self._enabled = False
        self._load_error: str | None = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def load_error(self) -> str | None:
        return self._load_error

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    def disable(self, reason: str) -> None:
        self._enabled = False
        self._load_error = reason

    def load(self) -> None:
        graph_path = self._data_dir / "graph" / "nodes.jsonl"
        meihua_path = self._data_dir / "graph" / "meihua_nodes.jsonl"
        qimen_path = self._data_dir / "graph" / "qimen_nodes.jsonl"
        liuren_path = self._data_dir / "graph" / "liuren_nodes.jsonl"
        manifest_path = self._data_dir / "manifest.json"
        if (
            not graph_path.exists()
            and not meihua_path.exists()
            and not qimen_path.exists()
            and not liuren_path.exists()
        ):
            self._enabled = False
            self._load_error = f"graph not found: {graph_path}"
            logger.warning("knowledge store disabled: %s", self._load_error)
            return

        nodes: list[dict] = []
        for path in (graph_path, meihua_path, qimen_path, liuren_path):
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                node = json.loads(line)
                if node.get("safeAutoAnswer") and not allow_safe_auto_answer(node):
                    node = dict(node)
                    node["safeAutoAnswer"] = False
                nodes.append(node)

        index: dict[tuple[str, ...], list[dict]] = {}
        for node in nodes:
            topic = node.get("topic") or ""
            lookup_key = node.get("lookupKey") or {}
            key = _canonical_key(topic, lookup_key)
            index.setdefault(key, []).append(node)

        self._nodes = nodes
        self._index = index
        self._manifest = {}
        if manifest_path.exists():
            self._manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self._enabled = True
        self._load_error = None
        logger.info("knowledge store loaded nodes=%s dir=%s", len(nodes), self._data_dir)

    def lookup(self, topic: str, lookup_key: dict[str, str]) -> list[dict]:
        if not self._enabled:
            return []
        key = _canonical_key(topic, lookup_key)
        rows = list(self._index.get(key, []))
        rows.sort(key=lambda item: item.get("sourceTier", "T9"))
        return rows

    def stats(self) -> dict:
        by_tier: dict[str, int] = {}
        by_topic: dict[str, int] = {}
        for node in self._nodes:
            tier = node.get("sourceTier", "?")
            topic = node.get("topic", "?")
            by_tier[tier] = by_tier.get(tier, 0) + 1
            by_topic[topic] = by_topic.get(topic, 0) + 1
        return {
            "enabled": self._enabled,
            "nodeCount": len(self._nodes),
            "byTier": by_tier,
            "byTopic": by_topic,
            "manifestVersion": self._manifest.get("version", ""),
            "01FilesIndexed": self._manifest.get("01FilesIndexed", 0),
            "crossCategoryCount": self._manifest.get("crossCategoryCount", 0),
            "loadError": self._load_error,
        }
