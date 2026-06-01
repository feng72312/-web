from __future__ import annotations

from pathlib import Path

from app.benchmark.contest8_dataset import load_split, split_summary


def test_contest8_splits_exist() -> None:
    summary = split_summary()
    assert summary["train"] == 120
    assert summary["val"] == 40
    assert summary["test"] == 40


def test_train_questions_have_answers() -> None:
    items = load_split("train")
    assert len(items) == 120
    for q in items[:5]:
        assert q.answer in ("A", "B", "C", "D")
        assert q.birth.get("year")


def test_data_dir_override(tmp_path: Path) -> None:
    import json
    import shutil

    src = Path(__file__).resolve().parents[3] / "命理师大赛试题" / "data"
    if not src.is_dir():
        return
    for year in (2025,):
        shutil.copy(src / f"contest8_{year}.json", tmp_path / f"contest8_{year}.json")
    items = load_split("test", data_dir=tmp_path)
    assert len(items) == 40
