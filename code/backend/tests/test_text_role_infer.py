from __future__ import annotations

import sys
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parents[2] / "rag"
if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))

from chunker import infer_text_role  # noqa: E402


def test_infer_text_role_toc() -> None:
    text = "目录\n第一部份(函测命例)......\n函测命例一......"
    assert infer_text_role(text) == "toc"


def test_infer_text_role_case() -> None:
    text = "乾造 甲子 丙寅 丁卯 辛未 此造..."
    assert infer_text_role(text) == "case"


def test_infer_text_role_original() -> None:
    text = "月令司权, 当以旺衰为先, 再看格局清浊。"
    assert infer_text_role(text) == "original"
