from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.api.access_gate import AccessGateMiddleware


async def interpret(request):  # noqa: ANN001, ARG001
    return JSONResponse({"ok": True})


async def paipan(request):  # noqa: ANN001, ARG001
    return JSONResponse({"ok": True})


async def quota(request):  # noqa: ANN001, ARG001
    return JSONResponse({"ok": True})


async def chat_send(request):  # noqa: ANN001, ARG001
    return JSONResponse({"ok": True})


def _client(code_file: Path) -> TestClient:
    app = Starlette(
        routes=[
            Route("/api/v1/interpret", interpret, methods=["POST"]),
            Route("/api/v1/interpret/stream", interpret, methods=["POST"]),
            Route("/api/v1/chat/send", chat_send, methods=["POST"]),
            Route("/api/v1/rag/search", interpret, methods=["POST"]),
            Route("/api/v1/paipan", paipan, methods=["POST"]),
            Route("/api/v1/quota/status", quota, methods=["GET"]),
        ]
    )
    app.add_middleware(AccessGateMiddleware, code_file=code_file)
    return TestClient(app)


def test_lan_request_untouched(tmp_path: Path) -> None:
    code_file = tmp_path / "code.txt"
    code_file.write_text("a1b2c3", encoding="utf-8")
    client = _client(code_file)
    response = client.post("/api/v1/interpret")
    assert response.status_code == 200


def test_tunnel_without_file_passes(tmp_path: Path) -> None:
    client = _client(tmp_path / "missing.txt")
    response = client.post("/api/v1/interpret", headers={"CF-Connecting-IP": "1.2.3.4"})
    assert response.status_code == 200


def test_tunnel_without_code_rejected(tmp_path: Path) -> None:
    code_file = tmp_path / "code.txt"
    code_file.write_text("a1b2c3", encoding="utf-8")
    client = _client(code_file)
    response = client.post("/api/v1/interpret", headers={"CF-Connecting-IP": "1.2.3.4"})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "access_code_required"


def test_tunnel_correct_code(tmp_path: Path) -> None:
    code_file = tmp_path / "code.txt"
    code_file.write_text("a1b2c3", encoding="utf-8")
    client = _client(code_file)
    response = client.post(
        "/api/v1/interpret",
        headers={"CF-Connecting-IP": "1.2.3.4", "X-Access-Code": "a1b2c3"},
    )
    assert response.status_code == 200


def test_tunnel_wrong_code(tmp_path: Path) -> None:
    code_file = tmp_path / "code.txt"
    code_file.write_text("a1b2c3", encoding="utf-8")
    client = _client(code_file)
    response = client.post(
        "/api/v1/interpret",
        headers={"CF-Connecting-IP": "1.2.3.4", "X-Access-Code": "zzzzzz"},
    )
    assert response.status_code == 401


def test_unprotected_paths_pass(tmp_path: Path) -> None:
    code_file = tmp_path / "code.txt"
    code_file.write_text("a1b2c3", encoding="utf-8")
    client = _client(code_file)
    assert client.post("/api/v1/paipan", headers={"CF-Connecting-IP": "1.2.3.4"}).status_code == 200
    assert client.get("/api/v1/quota/status", headers={"CF-Connecting-IP": "1.2.3.4"}).status_code == 200


def test_file_removed_releases_gate(tmp_path: Path) -> None:
    code_file = tmp_path / "code.txt"
    code_file.write_text("a1b2c3", encoding="utf-8")
    client = _client(code_file)
    blocked = client.post("/api/v1/interpret", headers={"CF-Connecting-IP": "1.2.3.4"})
    assert blocked.status_code == 401
    code_file.unlink()
    opened = client.post("/api/v1/interpret", headers={"CF-Connecting-IP": "1.2.3.4"})
    assert opened.status_code == 200
