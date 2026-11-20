"""Optional local-only AI assistant.

The assistant talks only to a model listening on localhost (Ollama-compatible API).
If no local model is available, the application remains fully usable and the UI
reports that the assistant is unavailable.
"""
from __future__ import annotations

import json
import os
from urllib.parse import urlparse
from typing import Any
from urllib import error, request

OLLAMA_BASE_URL = os.getenv("LOCAL_AI_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("LOCAL_AI_MODEL", "llama3.2")


def _is_loopback(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        return host in {"127.0.0.1", "localhost", "::1"}
    except Exception:
        return False


def local_model_status() -> dict[str, Any]:
    if not _is_loopback(OLLAMA_BASE_URL):
        return {
            "available": False,
            "message": "المساعد المحلي متاح فقط على عنوان محلي (localhost).",
        }
    try:
        req = request.Request(f"{OLLAMA_BASE_URL}/api/tags", method="GET")
        with request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = [m.get("name", "") for m in data.get("models", [])]
        if not any(OLLAMA_MODEL in m for m in models):
            return {
                "available": False,
                "message": f"النموذج {OLLAMA_MODEL} غير موجود محليًا. قم بتثبيته عبر Ollama.",
            }
        return {"available": True, "message": "المساعد المحلي جاهز.", "model": OLLAMA_MODEL}
    except Exception as exc:
        return {
            "available": False,
            "message": f"المساعد المحلي غير متاح حالياً: {exc}",
        }


def _post_json(path: str, payload: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    if not _is_loopback(OLLAMA_BASE_URL):
        raise RuntimeError("Local AI endpoint must be loopback only.")
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{OLLAMA_BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.URLError as exc:
        raise RuntimeError(f"فشل الاتصال بالنموذج المحلي: {exc}") from exc


def ask_local_model(prompt: str, system: str | None = None) -> str:
    status = local_model_status()
    if not status["available"]:
        raise RuntimeError(status["message"])
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    data = _post_json(
        "/api/chat",
        {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1},
        },
    )
    content = data.get("message", {}).get("content") or data.get("response") or ""
    if not content:
        raise RuntimeError("النموذج المحلي لم يُرجع محتوى.")
    return content.strip()


def ask_local_model_json(prompt: str, system: str | None = None) -> dict[str, Any]:
    raw = ask_local_model(prompt, system=system)
    # Strip markdown fences if the model adds them
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError("النموذج المحلي لم يُرجع JSON صالحًا.") from exc
