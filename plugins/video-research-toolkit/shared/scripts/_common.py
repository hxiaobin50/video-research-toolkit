from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_dotenv(project_dir: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = project_dir / ".env"
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_secret(project_dir: Path, name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value.strip()
    return load_dotenv(project_dir).get(name) or None


def redact(value: Any, secrets: list[str] | None = None) -> Any:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    for secret in secrets or []:
        if secret:
            text = text.replace(secret, "***REDACTED***")
    text = re.sub(r"(?i)(x-api-key|api[_-]?key|key)([=: ]+)[^&\s\"']+", r"\1\2***REDACTED***", text)
    if isinstance(value, str):
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_log(project_dir: Path, action: str, status: str, details: dict[str, Any] | None = None) -> None:
    safe = redact(details or {})
    append_jsonl(
        project_dir / ".video-research" / "logs" / "run-log.jsonl",
        {"time": utc_now(), "action": action, "status": status, "details": safe},
    )


def cache_key(provider: str, endpoint: str, params: dict[str, Any]) -> str:
    payload = json.dumps(
        {"provider": provider, "endpoint": endpoint, "params": params},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stable_id(prefix: str, *parts: Any) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def http_get_json(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 45,
    secrets: list[str] | None = None,
) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {redact(body, secrets)}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {redact(str(exc.reason), secrets)}") from exc


def build_url(base: str, params: dict[str, Any]) -> str:
    clean = {key: value for key, value in params.items() if value is not None and value != ""}
    return f"{base}?{urllib.parse.urlencode(clean, doseq=True)}"


def ensure_project_dirs(project_dir: Path) -> None:
    for relative in [
        ".video-research/cache",
        ".video-research/logs",
        "raw",
        "processed",
        "outputs",
    ]:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)


def save_raw(project_dir: Path, provider: str, batch_id: str, name: str, data: Any) -> Path:
    target = project_dir / "raw" / provider / batch_id / f"{name}.json"
    atomic_write_json(target, data)
    return target


def register_collection(project_dir: Path, provider: str, batch_id: str, result: dict[str, Any]) -> None:
    state_path = project_dir / ".video-research" / "state.json"
    state = read_json(state_path, {}) or {}
    collections = state.setdefault("collections", [])
    collections[:] = [
        item
        for item in collections
        if not (item.get("provider") == provider and item.get("batch_id") == batch_id)
    ]
    collections.append(
        {
            "provider": provider,
            "batch_id": batch_id,
            "mode": result.get("mode") or result.get("endpoint"),
            "status": result.get("status", "complete"),
            "items": result.get("items"),
            "pages": result.get("pages"),
            "index_file": result.get("index_file"),
            "updated_at": utc_now(),
        }
    )
    state["last_successful_step"] = f"collection:{provider}:{batch_id}"
    state["updated_at"] = utc_now()
    atomic_write_json(state_path, state)
