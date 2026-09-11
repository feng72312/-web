from __future__ import annotations

import json
from pathlib import Path

from app.core.personas.registry import MAX_FILE_BYTES, PersonaRegistry


def _write_pack(root: Path, *, status: str = "historical-deceased") -> Path:
    directory = root / "test-persona"
    directory.mkdir(parents=True)
    manifest = {
        "id": "test-persona",
        "name": "测试人物",
        "formal_name": "测试人物 · 字求真",
        "era": "古代",
        "lifespan": "1000—1060",
        "status": status,
        "version": "1.0.0",
        "summary": "这是一个用于验证人物包注册表字段校验与加载流程的完整测试人物简介。",
        "disclosure": "这是基于公开史料构建的人工智能思想模拟，并非历史人物本人或真实意志。",
        "seal_character": "真",
        "themes": ["求真"],
        "suitable_for": ["思想讨论"],
        "not_suitable_for": ["实时事实"],
        "upstream": {"name": "example", "url": "https://example.com"},
        "license": {
            "name": "MIT",
            "attribution": "example",
            "source_url": "https://example.com/license",
        },
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    (directory / "prompt.md").write_text("人物方法论与表达边界。" * 20, encoding="utf-8")
    (directory / "sources.json").write_text(
        json.dumps(
            [{"id": "source", "title": "史料", "kind": "primary", "note": "测试史料"}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (directory / "starters.json").write_text(
        json.dumps(
            [{"label": "开场", "prompt": "请谈谈求真。", "theme": "求真"}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (directory / "LICENSE").write_text("MIT License", encoding="utf-8")
    return directory


def test_registry_loads_valid_pack(tmp_path: Path) -> None:
    _write_pack(tmp_path)
    registry = PersonaRegistry(tmp_path)
    assert registry.require("test-persona").manifest.name == "测试人物"
    assert registry.errors == {}


def test_registry_rejects_missing_field(tmp_path: Path) -> None:
    directory = _write_pack(tmp_path)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    manifest.pop("disclosure")
    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    registry = PersonaRegistry(tmp_path)
    assert registry.get("test-persona") is None
    assert "disclosure" in registry.errors["test-persona"]


def test_registry_rejects_unknown_file(tmp_path: Path) -> None:
    directory = _write_pack(tmp_path)
    (directory / "script.py").write_text("pass", encoding="utf-8")
    registry = PersonaRegistry(tmp_path)
    assert "unknown files" in registry.errors["test-persona"]


def test_registry_rejects_oversize_file(tmp_path: Path) -> None:
    directory = _write_pack(tmp_path)
    (directory / "prompt.md").write_text(
        "字" * (MAX_FILE_BYTES["prompt.md"] + 1), encoding="utf-8"
    )
    registry = PersonaRegistry(tmp_path)
    assert "exceeds size limit" in registry.errors["test-persona"]


def test_registry_rejects_living_or_unknown_status(tmp_path: Path) -> None:
    _write_pack(tmp_path, status="living")
    registry = PersonaRegistry(tmp_path)
    assert registry.get("test-persona") is None
    assert "public_framework" in registry.errors["test-persona"]
