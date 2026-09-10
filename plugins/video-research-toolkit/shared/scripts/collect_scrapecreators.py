from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _common import (
    append_log,
    atomic_write_json,
    build_url,
    cache_key,
    ensure_project_dirs,
    get_secret,
    http_get_json,
    read_json,
    register_collection,
    save_raw,
    utc_now,
)


BASE = "https://api.scrapecreators.com"
BALANCE_ENDPOINT = "/v1/account/credit-balance"
TOKEN_TO_PARAM = {
    "cursor": "cursor",
    "max_cursor": "max_cursor",
    "continuationToken": "continuationToken",
    "continuation_token": "continuationToken",
    "next_max_id": "max_id",
    "max_id": "max_id",
    "paginationToken": "paginationToken",
}


def batch_name() -> str:
    return datetime.now(timezone.utc).strftime("sc_%Y%m%dT%H%M%S%fZ")


def read_balance(project_dir: Path, key: str) -> dict[str, Any]:
    data = http_get_json(f"{BASE}{BALANCE_ENDPOINT}", headers={"x-api-key": key}, secrets=[key])
    remaining = data.get("credits_remaining", data.get("creditCount"))
    state_path = project_dir / ".video-research" / "state.json"
    state = read_json(state_path, {}) or {}
    usage = state.setdefault("api_usage", {}).setdefault("scrapecreators", {})
    if isinstance(remaining, (int, float)) and not isinstance(usage.get("initial_credits"), (int, float)):
        usage["initial_credits"] = remaining
    usage["last_known_credits"] = remaining
    usage["checked_at"] = utc_now()
    atomic_write_json(state_path, state)
    return {"remaining": remaining, "initial": usage.get("initial_credits"), "raw": data}


def find_next_token(value: Any) -> tuple[str, Any] | None:
    if isinstance(value, dict):
        for key in TOKEN_TO_PARAM:
            token = value.get(key)
            if token not in (None, "", False, 0):
                return TOKEN_TO_PARAM[key], token
        for nested in value.values():
            found = find_next_token(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value[:5]:
            found = find_next_token(nested)
            if found:
                return found
    return None


def call_or_cache(project_dir: Path, endpoint: str, params: dict[str, Any], key: str, refresh: bool) -> tuple[dict[str, Any], bool]:
    digest = cache_key("scrapecreators", endpoint, params)
    cache_path = project_dir / ".video-research" / "cache" / "scrapecreators" / f"{digest}.json"
    if cache_path.exists() and not refresh:
        return read_json(cache_path, {}), True
    data = http_get_json(build_url(f"{BASE}{endpoint}", params), headers={"x-api-key": key}, secrets=[key])
    atomic_write_json(cache_path, data)
    return data, False


def parse_params(values: list[str]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Invalid parameter '{item}'. Use name=value.")
        name, value = item.split("=", 1)
        params[name] = value
    return params


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect public social data through ScrapeCreators with cache and balance protection.")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--batch-id")
    parser.add_argument("--refresh", action="store_true")
    sub = parser.add_subparsers(dest="mode", required=True)

    sub.add_parser("balance")

    request_parser = sub.add_parser("request")
    request_parser.add_argument("--endpoint", required=True)
    request_parser.add_argument("--param", action="append", default=[])
    request_parser.add_argument("--max-pages", type=int, default=1)
    request_parser.add_argument("--skip-balance-check", action="store_true")

    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()
    ensure_project_dirs(project_dir)
    key = get_secret(project_dir, "SCRAPECREATORS_API_KEY")
    if not key:
        print(json.dumps({"status": "missing_api_key", "required": "SCRAPECREATORS_API_KEY", "instruction": "Configure the key in the project .env file. Do not paste it into chat."}, ensure_ascii=False, indent=2))
        return 2

    if args.mode == "balance":
        try:
            balance = read_balance(project_dir, key)
            print(json.dumps({"status": "ok", "credits_remaining": balance["remaining"], "initial_project_credits": balance["initial"], "note": "The balance request may consume one credit."}, ensure_ascii=False, indent=2))
            return 0
        except Exception as exc:
            print(json.dumps({"status": "collection_failed", "endpoint": BALANCE_ENDPOINT, "error": str(exc), "retry_requires_review": True}, ensure_ascii=False, indent=2))
            return 1

    endpoint = args.endpoint.strip()
    if not re.fullmatch(r"/v[123]/[A-Za-z0-9_./-]+", endpoint):
        print(json.dumps({"status": "invalid_endpoint", "endpoint": endpoint}, ensure_ascii=False, indent=2))
        return 2

    params = parse_params(args.param)
    batch_id = args.batch_id or batch_name()
    paths: list[str] = []
    balance_checked = False
    current_params = dict(params)
    next_token: tuple[str, Any] | None = None
    try:
        for page_number in range(1, args.max_pages + 1):
            digest = cache_key("scrapecreators", endpoint, current_params)
            cache_path = project_dir / ".video-research" / "cache" / "scrapecreators" / f"{digest}.json"
            cached_before_call = cache_path.exists() and not args.refresh
            if not cached_before_call and not args.skip_balance_check and not balance_checked:
                balance = read_balance(project_dir, key)
                balance_checked = True
                remaining, initial = balance["remaining"], balance["initial"]
                if isinstance(remaining, (int, float)) and isinstance(initial, (int, float)) and initial > 0 and remaining <= initial * 0.25:
                    print(json.dumps({"status": "confirmation_required", "reason": "scrapecreators_balance_at_or_below_25_percent", "credits_remaining": remaining, "initial_project_credits": initial, "planned_endpoint": endpoint}, ensure_ascii=False, indent=2))
                    return 25

            data, cached = call_or_cache(project_dir, endpoint, current_params, key, args.refresh)
            raw_path = save_raw(project_dir, "scrapecreators", batch_id, f"response_page_{page_number:04d}", data)
            paths.append(str(raw_path))
            next_token = find_next_token(data)
            append_log(project_dir, "scrapecreators.request", "cached" if cached else "ok", {"batch_id": batch_id, "endpoint": endpoint, "page": page_number, "has_next": bool(next_token)})
            if not next_token:
                break
            param_name, token = next_token
            if current_params.get(param_name) == token:
                break
            current_params[param_name] = token

        result = {
            "status": "ok",
            "endpoint": endpoint,
            "batch_id": batch_id,
            "pages": len(paths),
            "raw_files": paths,
            "next": {"parameter": next_token[0], "value": next_token[1]} if next_token else None,
            "collected_at": utc_now(),
        }
        index_path = project_dir / "raw" / "scrapecreators" / batch_id / "collection-index.json"
        atomic_write_json(index_path, result)
        result["index_file"] = str(index_path)
        register_collection(project_dir, "scrapecreators", batch_id, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        append_log(project_dir, "scrapecreators.request", "failed", {"batch_id": batch_id, "endpoint": endpoint, "error": str(exc)})
        print(json.dumps({"status": "collection_failed", "endpoint": endpoint, "batch_id": batch_id, "error": str(exc), "retry_requires_review": True}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
