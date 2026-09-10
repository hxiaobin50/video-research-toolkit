from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any, Iterable

from _common import stable_id, utc_now


MISSING = "not_available"


def load_any(path: Path) -> Any:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from walk_dicts(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk_dicts(nested)


def comment_candidates(value: Any) -> Iterable[dict[str, Any]]:
    for item in walk_dicts(value):
        top_level = item.get("snippet", {}).get("topLevelComment") if isinstance(item.get("snippet"), dict) else None
        if isinstance(top_level, dict):
            enriched = copy.deepcopy(top_level)
            snippet = enriched.setdefault("snippet", {})
            if isinstance(snippet, dict):
                thread_snippet = item.get("snippet", {})
                snippet.setdefault("videoId", thread_snippet.get("videoId"))
                snippet.setdefault("totalReplyCount", thread_snippet.get("totalReplyCount"))
                expected = parse_number(thread_snippet.get("totalReplyCount"))
                inline_replies = item.get("replies", {}).get("comments", []) if isinstance(item.get("replies"), dict) else []
                if expected is not None:
                    snippet.setdefault("repliesComplete", len(inline_replies) >= expected)
            yield enriched
        yield item


def dig(value: Any, *paths: str) -> Any:
    for path in paths:
        current = value
        found = True
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                found = False
                break
        if found and current not in (None, "") and not isinstance(current, (dict, list)):
            return current
    return None


def parse_number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        try:
            return float(cleaned) if "." in cleaned else int(cleaned)
        except ValueError:
            return None
    return None


def parse_duration(value: Any) -> int | None:
    number = parse_number(value)
    if number is not None:
        return int(number)
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value)
    if not match:
        return None
    days, hours, minutes, seconds = [int(part or 0) for part in match.groups()]
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def duration_band(seconds: int | None) -> str:
    if seconds is None:
        return MISSING
    if seconds <= 30:
        return "0–30秒"
    if seconds <= 60:
        return "31–60秒"
    if seconds <= 120:
        return "61–120秒"
    return ">120秒"


def rate(numerator: Any, denominator: Any) -> float | str:
    top = parse_number(numerator)
    bottom = parse_number(denominator)
    if top is None or bottom is None or bottom <= 0:
        return MISSING
    return top / bottom


def normalize_video(item: dict[str, Any], platform: str, source_file: str) -> dict[str, Any] | None:
    explicit_content_id = dig(item, "id.videoId", "videoId", "video_id", "aweme_id", "media_id", "code", "shortcode")
    fallback_content_id = dig(item, "pk", "id")
    content_id = explicit_content_id or fallback_content_id
    title = dig(item, "snippet.title", "title", "desc", "caption")
    url = dig(item, "url", "webVideoUrl", "share_url", "permalink", "link", "video_url")
    if not content_id and not url:
        return None
    if isinstance(content_id, (dict, list)):
        content_id = None
    duration = parse_duration(dig(item, "contentDetails.duration", "duration", "duration_seconds", "video.duration"))
    views = parse_number(dig(item, "statistics.viewCount", "viewCount", "view_count", "playCount", "play_count", "views", "video_view_count"))
    likes = parse_number(dig(item, "statistics.likeCount", "likeCount", "like_count", "diggCount", "likes"))
    comments = parse_number(dig(item, "statistics.commentCount", "commentCount", "comment_count", "comments"))
    shares = parse_number(dig(item, "shareCount", "share_count", "shares"))
    saves = parse_number(dig(item, "collectCount", "saveCount", "save_count", "bookmark_count", "saves"))
    has_video_shape = any(
        value is not None
        for value in (title, url, duration, views, likes, comments, shares, saves)
    )
    if not explicit_content_id and not has_video_shape:
        return None
    if platform.lower() == "youtube" and content_id and not url:
        url = f"https://www.youtube.com/watch?v={content_id}"
    key_value = content_id or url
    return {
        "record_id": stable_id("vid", platform.lower(), key_value),
        "platform": platform,
        "platform_content_id": str(content_id) if content_id else MISSING,
        "video_url": url or MISSING,
        "platform_content_type": dig(item, "type", "content_type", "media_type") or MISSING,
        "same_content_group_id": MISSING,
        "discovery_method": MISSING,
        "source_query_id": MISSING,
        "collection_batch_id": MISSING,
        "collected_at": utc_now(),
        "raw_data_reference": source_file,
        "video_title": title or MISSING,
        "publisher_name": dig(item, "snippet.channelTitle", "author.uniqueId", "author.username", "ownerUsername", "username", "channelTitle") or MISSING,
        "publisher_id": dig(item, "snippet.channelId", "author.id", "authorId", "ownerId", "channelId") or MISSING,
        "published_at": dig(item, "snippet.publishedAt", "createTimeISO", "created_at", "taken_at", "published_at") or MISSING,
        "duration_seconds": duration if duration is not None else MISSING,
        "duration_band": duration_band(duration),
        "description": dig(item, "snippet.description", "description", "desc", "caption") or MISSING,
        "available_text_summary": MISSING,
        "view_or_play_count": views if views is not None else MISSING,
        "like_count": likes if likes is not None else MISSING,
        "comment_count": comments if comments is not None else MISSING,
        "share_count": shares if shares is not None else MISSING,
        "save_count": saves if saves is not None else MISSING,
        "like_rate": rate(likes, views),
        "comment_rate": rate(comments, views),
        "share_rate": rate(shares, views),
        "save_rate": rate(saves, views),
        "relevance": "not_reviewed",
        "exclusion_reason": "",
        "primary_journey_stage": "not_reviewed",
        "main_consumer_task": "not_reviewed",
        "secondary_journey_stage": "not_reviewed",
        "primary_content_theme": "not_reviewed",
        "secondary_content_theme": "not_reviewed",
        "target_audience_type": "not_reviewed",
        "manual_review_needed": "not_reviewed",
        "manual_review_reason": "not_reviewed",
        "source_files": [source_file],
    }


def normalize_comment(item: dict[str, Any], platform: str, source_file: str) -> dict[str, Any] | None:
    text = dig(item, "snippet.textOriginal", "snippet.textDisplay", "text", "comment", "content", "body")
    comment_id = dig(item, "commentId", "comment_id", "cid", "pk", "id")
    if not text or not comment_id or isinstance(comment_id, (dict, list)):
        return None
    video_id = dig(item, "snippet.videoId", "videoId", "video_id", "aweme_id", "media_id")
    parent_id = dig(item, "snippet.parentId", "parentId", "parent_id")
    likes = parse_number(dig(item, "snippet.likeCount", "likeCount", "like_count", "diggCount", "likes"))
    replies = parse_number(dig(item, "snippet.totalReplyCount", "replyCount", "reply_count", "child_comment_count"))
    return {
        "comment_record_id": stable_id("com", platform.lower(), comment_id),
        "video_record_id": stable_id("vid", platform.lower(), video_id) if video_id else MISSING,
        "platform": platform,
        "video_url": MISSING,
        "collection_batch_id": MISSING,
        "collected_at": utc_now(),
        "raw_data_reference": source_file,
        "platform_comment_id": str(comment_id),
        "parent_comment_id": str(parent_id) if parent_id else "not_applicable",
        "comment_level": "reply" if parent_id else "top_level",
        "public_author_id": dig(item, "snippet.authorChannelId.value", "author.uniqueId", "author.username", "username", "user_id") or MISSING,
        "comment_published_at": dig(item, "snippet.publishedAt", "createTimeISO", "created_at", "published_at") or MISSING,
        "original_comment": str(text),
        "comment_like_count": likes if likes is not None else MISSING,
        "reply_count": replies if replies is not None else MISSING,
        "replies_complete": dig(item, "snippet.repliesComplete", "repliesComplete") if dig(item, "snippet.repliesComplete", "repliesComplete") is not None else MISSING,
        "included": "not_reviewed",
        "exclusion_reason": "",
        "duplicate_group_id": MISSING,
        "source_files": [source_file],
    }


def merge_record(existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    for key, value in new.items():
        if key == "source_files":
            existing[key] = sorted(set(existing.get(key, []) + value))
        elif existing.get(key) in (None, "", MISSING, "not_reviewed") and value not in (None, "", MISSING):
            existing[key] = value
    if existing.get("raw_data_reference") != new.get("raw_data_reference"):
        existing["raw_data_reference"] = "; ".join(existing.get("source_files", []))
    return existing


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize and deduplicate collected video or comment records.")
    parser.add_argument("--kind", required=True, choices=["video", "comment"])
    parser.add_argument("--platform", required=True)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    normalized: dict[str, dict[str, Any]] = {}
    for input_name in args.input:
        path = Path(input_name).resolve()
        data = load_any(path)
        candidates = walk_dicts(data) if args.kind == "video" else comment_candidates(data)
        for item in candidates:
            record = normalize_video(item, args.platform, str(path)) if args.kind == "video" else normalize_comment(item, args.platform, str(path))
            if not record:
                continue
            record_key = record["record_id"] if args.kind == "video" else record["comment_record_id"]
            normalized[record_key] = merge_record(normalized[record_key], record) if record_key in normalized else record

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in normalized.values():
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"status": "ok", "kind": args.kind, "platform": args.platform, "records": len(normalized), "output": str(output_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
