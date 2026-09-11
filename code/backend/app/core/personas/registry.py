from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.core.personas.models import (
    PersonaManifest,
    PersonaPack,
    PersonaSource,
    PersonaStarter,
)

logger = logging.getLogger(__name__)

ALLOWED_FILES = {
    "manifest.json",
    "prompt.md",
    "sources.json",
    "starters.json",
    "LICENSE",
}
MAX_FILE_BYTES = {
    "manifest.json": 64_000,
    "prompt.md": 64_000,
    "sources.json": 128_000,
    "starters.json": 32_000,
    "LICENSE": 64_000,
}
MAX_PACK_BYTES = 256_000

T = TypeVar("T", bound=BaseModel)


class PersonaPackError(ValueError):
    pass


def default_persona_root() -> Path:
    return Path(__file__).resolve().parent / "packs"


class PersonaRegistry:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or default_persona_root()
        self._packs: dict[str, PersonaPack] = {}
        self._errors: dict[str, str] = {}
        self.reload()

    @property
    def errors(self) -> dict[str, str]:
        return dict(self._errors)

    def list(self) -> list[PersonaPack]:
        return sorted(self._packs.values(), key=lambda item: item.manifest.name)

    def get(self, persona_id: str) -> PersonaPack | None:
        return self._packs.get(persona_id)

    def require(self, persona_id: str) -> PersonaPack:
        pack = self.get(persona_id)
        if pack is None:
            raise KeyError(persona_id)
        return pack

    def reload(self) -> None:
        self._packs = {}
        self._errors = {}
        if not self.root.exists():
            logger.warning("persona pack root does not exist: %s", self.root)
            return
        for entry in sorted(self.root.iterdir()):
            if not entry.is_dir() or entry.name.startswith("."):
                continue
            try:
                pack = self._load_pack(entry)
                if pack.manifest.id != entry.name:
                    raise PersonaPackError(
                        f"manifest id {pack.manifest.id!r} does not match directory {entry.name!r}"
                    )
                if pack.manifest.id in self._packs:
                    raise PersonaPackError(f"duplicate persona id: {pack.manifest.id}")
                self._packs[pack.manifest.id] = pack
            except (OSError, json.JSONDecodeError, ValidationError, PersonaPackError) as err:
                self._errors[entry.name] = str(err)
                logger.error("persona pack rejected path=%s error=%s", entry, err)

    def _load_pack(self, directory: Path) -> PersonaPack:
        names = {item.name for item in directory.iterdir() if item.is_file()}
        unknown = names - ALLOWED_FILES
        missing = ALLOWED_FILES - names
        if unknown:
            raise PersonaPackError(f"unknown files: {', '.join(sorted(unknown))}")
        if missing:
            raise PersonaPackError(f"missing files: {', '.join(sorted(missing))}")

        total_bytes = 0
        for name in ALLOWED_FILES:
            size = (directory / name).stat().st_size
            total_bytes += size
            if size > MAX_FILE_BYTES[name]:
                raise PersonaPackError(f"{name} exceeds size limit")
        if total_bytes > MAX_PACK_BYTES:
            raise PersonaPackError("persona pack exceeds total size limit")

        manifest = PersonaManifest.model_validate(
            self._read_json(directory / "manifest.json")
        )
        prompt = (directory / "prompt.md").read_text(encoding="utf-8").strip()
        license_text = (directory / "LICENSE").read_text(encoding="utf-8").strip()
        if len(prompt) < 100:
            raise PersonaPackError("prompt.md is too short")
        if not license_text:
            raise PersonaPackError("LICENSE is empty")

        sources = self._validate_list(
            self._read_json(directory / "sources.json"), PersonaSource, "sources.json"
        )
        starters = self._validate_list(
            self._read_json(directory / "starters.json"), PersonaStarter, "starters.json"
        )
        if not sources:
            raise PersonaPackError("sources.json must contain at least one source")
        if not starters:
            raise PersonaPackError("starters.json must contain at least one starter")
        return PersonaPack(
            manifest=manifest,
            prompt=prompt,
            sources=sources,
            starters=starters,
            license_text=license_text,
        )

    @staticmethod
    def _read_json(path: Path) -> object:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _validate_list(raw: object, model: type[T], filename: str) -> list[T]:
        if not isinstance(raw, list):
            raise PersonaPackError(f"{filename} must contain a JSON array")
        return [model.model_validate(item) for item in raw]


@lru_cache(maxsize=1)
def get_persona_registry() -> PersonaRegistry:
    return PersonaRegistry()
