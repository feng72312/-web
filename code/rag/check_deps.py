"""Return 0 when RAG runtime dependencies are ready."""

from __future__ import annotations

import sys


def _import_check() -> str | None:
    try:
        import chromadb  # noqa: F401
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except ImportError as exc:
        return f"missing base package: {exc}"

    version = getattr(chromadb, "__version__", "")
    if not version.startswith("0.5."):
        return f"chromadb version must be 0.5.x, got {version or 'unknown'}"

    try:
        import sentence_transformers  # noqa: F401
    except ImportError as exc:
        return f"sentence_transformers import failed: {exc}"

    return None


def main() -> int:
    reason = _import_check()
    if reason:
        if "--verbose" in sys.argv:
            print(reason, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
