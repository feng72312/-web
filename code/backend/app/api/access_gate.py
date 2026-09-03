from __future__ import annotations

import json
import re
import secrets
from pathlib import Path

PROTECTED_PATTERNS = (
    re.compile(r"^/api/v1/(?:.+/)?interpret(?:/stream)?$"),
    re.compile(r"^/api/v1/chat/"),
    re.compile(r"^/api/v1/rag/search$"),
)


class AccessGateMiddleware:
    def __init__(self, app, code_file: Path) -> None:
        self.app = app
        self.code_file = Path(code_file)
        self._cached = ""
        self._mtime: float | None = None

    def read_code(self) -> str:
        try:
            stat = self.code_file.stat()
        except FileNotFoundError:
            self._cached = ""
            self._mtime = None
            return ""
        if self._mtime == stat.st_mtime:
            return self._cached
        text = self.code_file.read_text(encoding="utf-8").strip()
        self._cached = text
        self._mtime = stat.st_mtime
        return text

    def _is_protected(self, path: str) -> bool:
        return any(pattern.search(path) for pattern in PROTECTED_PATTERNS)

    async def __call__(self, scope, receive, send):  # noqa: ANN001
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        path = scope.get("path", "")
        code = self.read_code()
        if "cf-connecting-ip" in headers and code and self._is_protected(path):
            provided = headers.get("x-access-code", "")
            ok = bool(provided) and secrets.compare_digest(provided, code)
            if not ok:
                body = json.dumps(
                    {
                        "detail": {
                            "code": "access_code_required",
                            "message": "请输入访问口令",
                        }
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [
                            (b"content-type", b"application/json; charset=utf-8"),
                            (b"content-length", str(len(body)).encode("ascii")),
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": body})
                return

        await self.app(scope, receive, send)
