from __future__ import annotations

import argparse
import json
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


BASE = "https://www.googleapis.com/youtube/v3"


def batch_name() -> str:
    return datetime.now(timezone.utc).strftime("yt_%Y%m%dT%H%M%S%fZ")


def call_api(project_dir: Path, endpoint: str, params: dict[str, Any], key: str, refresh: bool) -> tuple[dict[str, Any], bool]:
    safe_params = {k: v for k, v in params.items() if k != "key"}
    digest = cache_key("youtube", endpoint, safe_params)
    cache_path = project_dir / ".video-research" / "cache" / "youtube" / f"{digest}.json"
    if cache_path.exists() and not refresh:
        return read_json(cache_path, {}), True
    request_params = dict(params)
    request_params["key"] = key
    data = http_get_json(build_url(f"{BASE}/{endpoint}", request_params), secrets=[key])
    atomic_write_json(cache_path, data)
    return data, False


def collect_pages(
    project_dir: Path,
    endpoint: str,
    base_params: dict[str, Any],
    key: str,
    batch_id: str,
    max_pages: int,
    refresh: bool,
    name_prefix: str,
) -> dict[str, Any]:
    page_token = None
    paths: list[str] = []
    item_count = 0
    cached_pages = 0
    for page_number in range(1, max_pages + 1):
        params = dict(base_params)
        if page_token:
            params["pageToken"] = page_token
        data, cached = call_api(project_dir, endpoint, params, key, refresh)
        cached_pages += int(cached)
        raw_path = save_raw(project_dir, "youtube", batch_id, f"{name_prefix}_page_{page_number:04d}", data)
        paths.append(str(raw_path))
        item_count += len(data.get("items", []))
        page_token = data.get("nextPageToken")
        append_log(
            project_dir,
            f"youtube.{endpoint}",
            "cached" if cached else "ok",
            {"batch_id": batch_id, "page": page_number, "items": len(data.get("items", [])), "has_next": bool(page_token)},
        )
        if not page_token:
            break
    return {
        "endpoint": endpoint,
        "pages": len(paths),
        "items": item_count,
        "cached_pages": cached_pages,
        "next_page_token": page_token,
        "raw_files": paths,
    }


def search(args: argparse.Namespace, project_dir: Path, key: str, batch_id: str) -> dict[str, Any]:
    params: dict[str, Any] = {
        "part": "snippet",
        "type": "video",
        "q": args.query,
        "maxResults": min(args.page_size, 50),
        "order": args.order,
        "publishedAfter": args.published_after,
        "publishedBefore": args.published_before,
        "regionCode": args.region,
        "relevanceLanguage": args.language,
        "safeSearch": args.safe_search,
    }
    result = collect_pages(project_dir, "search", params, key, batch_id, args.max_pages, args.refresh, "search")
    result.update({"mode": "search", "query": args.query, "batch_id": batch_id, "collected_at": utc_now()})
    return result


def videos(args: argparse.Namespace, project_dir: Path, key: str, batch_id: str) -> dict[str, Any]:
    ids = []
    for value in args.video_id:
        ids.extend(item.strip() for item in value.split(",") if item.strip())
    paths: list[str] = []
    items = 0
    cached_calls = 0
    for chunk_number, start in enumerate(range(0, len(ids), 50), 1):
        chunk = ids[start : start + 50]
        params = {"part": "snippet,statistics,contentDetails,status", "id": ",".join(chunk), "maxResults": 50}
        data, cached = call_api(project_dir, "videos", params, key, args.refresh)
        cached_calls += int(cached)
        raw_path = save_raw(project_dir, "youtube", batch_id, f"videos_chunk_{chunk_number:04d}", data)
        paths.append(str(raw_path))
        items += len(data.get("items", []))
        append_log(project_dir, "youtube.videos", "cached" if cached else "ok", {"batch_id": batch_id, "chunk": chunk_number, "items": len(data.get("items", []))})
    return {"mode": "videos", "batch_id": batch_id, "requested_ids": len(ids), "items": items, "cached_calls": cached_calls, "raw_files": paths, "collected_at": utc_now()}


def comments(args: argparse.Namespace, project_dir: Path, key: str, batch_id: str) -> dict[str, Any]:
    all_results: list[dict[str, Any]] = []
    for video_id in args.video_id:
        params = {
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": min(args.page_size, 100),
            "order": args.comment_order,
            "textFormat": "plainText",
        }
        result = collect_pages(project_dir, "commentThreads", params, key, batch_id, args.max_pages, args.refresh, f"comments_{video_id}")
        result["video_id"] = video_id
        all_results.append(result)
    return {
        "mode": "comments",
        "batch_id": batch_id,
        "videos": len(all_results),
        "items": sum(item["items"] for item in all_results),
        "results": all_results,
        "collected_at": utc_now(),
        "note": "commentThreads may not include every reply. Use comments.list for full replies when required.",
    }


def replies(args: argparse.Namespace, project_dir: Path, key: str, batch_id: str) -> dict[str, Any]:
    all_results: list[dict[str, Any]] = []
    for parent_id in args.parent_id:
        params = {"part": "snippet", "parentId": parent_id, "maxResults": min(args.page_size, 100), "textFormat": "plainText"}
        result = collect_pages(project_dir, "comments", params, key, batch_id, args.max_pages, args.refresh, f"replies_{parent_id}")
        result["parent_id"] = parent_id
        all_results.append(result)
    return {"mode": "replies", "batch_id": batch_id, "parents": len(all_results), "items": sum(item["items"] for item in all_results), "results": all_results, "collected_at": utc_now()}


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Collect traceable YouTube Data API records.")
    root.add_argument("--project-dir", required=True)
    root.add_argument("--batch-id")
    root.add_argument("--refresh", action="store_true")
    root.add_argument("--max-pages", type=int, default=1)
    root.add_argument("--page-size", type=int, default=50)
    sub = root.add_subparsers(dest="mode", required=True)

    search_parser = sub.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--order", default="relevance", choices=["date", "rating", "relevance", "title", "videoCount", "viewCount"])
    search_parser.add_argument("--published-after")
    search_parser.add_argument("--published-before")
    search_parser.add_argument("--region")
    search_parser.add_argument("--language")
    search_parser.add_argument("--safe-search", default="none", choices=["moderate", "none", "strict"])
    search_parser.set_defaults(handler=search)

    video_parser = sub.add_parser("videos")
    video_parser.add_argument("--video-id", action="append", required=True)
    video_parser.set_defaults(handler=videos)

    comment_parser = sub.add_parser("comments")
    comment_parser.add_argument("--video-id", action="append", required=True)
    comment_parser.add_argument("--comment-order", default="relevance", choices=["relevance", "time"])
    comment_parser.set_defaults(handler=comments)

    reply_parser = sub.add_parser("replies")
    reply_parser.add_argument("--parent-id", action="append", required=True)
    reply_parser.set_defaults(handler=replies)
    return root


def main() -> int:
    args = build_parser().parse_args()
    project_dir = Path(args.project_dir).resolve()
    ensure_project_dirs(project_dir)
    key = get_secret(project_dir, "YOUTUBE_API_KEY")
    if not key:
        print(json.dumps({"status": "missing_api_key", "required": "YOUTUBE_API_KEY", "instruction": "Configure the key in the project .env file. Do not paste it into chat."}, ensure_ascii=False, indent=2))
        return 2
    batch_id = args.batch_id or batch_name()
    try:
        result = args.handler(args, project_dir, key, batch_id)
        index_path = project_dir / "raw" / "youtube" / batch_id / "collection-index.json"
        atomic_write_json(index_path, result)
        result["index_file"] = str(index_path)
        register_collection(project_dir, "youtube", batch_id, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        append_log(project_dir, f"youtube.{args.mode}", "failed", {"batch_id": batch_id, "error": str(exc)})
        print(json.dumps({"status": "collection_failed", "mode": args.mode, "batch_id": batch_id, "error": str(exc), "retry_requires_review": True}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
