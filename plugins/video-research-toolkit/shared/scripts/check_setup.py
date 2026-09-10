from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import build_url, get_secret, http_get_json, redact


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local API setup without exposing API keys.")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--provider", action="append", choices=["youtube", "scrapecreators"], help="Check only the provider needed for this task. Repeat to check both; default checks both.")
    parser.add_argument("--live", action="store_true", help="Make real API requests. ScrapeCreators balance check may consume one credit.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    youtube_key = get_secret(project_dir, "YOUTUBE_API_KEY")
    scrape_key = get_secret(project_dir, "SCRAPECREATORS_API_KEY")
    requested = set(args.provider or ["youtube", "scrapecreators"])
    result = {
        "project_dir": str(project_dir),
        "requested_providers": sorted(requested),
    }
    if "youtube" in requested:
        result["youtube"] = {"configured": bool(youtube_key), "connection": "not_tested"}
    if "scrapecreators" in requested:
        result["scrapecreators"] = {"configured": bool(scrape_key), "connection": "not_tested"}

    if "youtube" in requested and args.live and youtube_key:
        try:
            url = build_url(
                "https://www.googleapis.com/youtube/v3/videos",
                {"part": "id", "id": "dQw4w9WgXcQ", "key": youtube_key},
            )
            http_get_json(url, secrets=[youtube_key])
            result["youtube"]["connection"] = "ok"
        except Exception as exc:
            result["youtube"]["connection"] = "failed"
            result["youtube"]["error"] = redact(str(exc), [youtube_key])

    if "scrapecreators" in requested and args.live and scrape_key:
        try:
            data = http_get_json(
                "https://api.scrapecreators.com/v1/account/credit-balance",
                headers={"x-api-key": scrape_key},
                secrets=[scrape_key],
            )
            result["scrapecreators"]["connection"] = "ok"
            result["scrapecreators"]["credits_remaining"] = data.get("credits_remaining", data.get("creditCount"))
            result["scrapecreators"]["note"] = "This live balance request may consume one credit."
        except Exception as exc:
            result["scrapecreators"]["connection"] = "failed"
            result["scrapecreators"]["error"] = redact(str(exc), [scrape_key])

    print(json.dumps(result, ensure_ascii=False, indent=2))
    checks = [result[name] for name in requested]
    return 0 if all(item["configured"] for item in checks) else 2


if __name__ == "__main__":
    raise SystemExit(main())
