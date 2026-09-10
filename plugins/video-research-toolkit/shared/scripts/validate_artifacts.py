from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]{25,}"),
    re.compile(r"(?i)(?:x-api-key|youtube_api_key|scrapecreators_api_key)\s*[=:]\s*[^\s\"'<>]{8,}"),
]


def scan_text(text: str) -> list[str]:
    findings: list[str] = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            token = match.group(0)
            if token.endswith("=") or token.endswith(":"):
                continue
            if "你的Key" in token or token.endswith("***REDACTED***"):
                continue
            findings.append(token[:20] + "…")
    return findings


def validate_xlsx(path: Path, expected_sheets: list[str]) -> dict:
    result = {"file": str(path), "type": "xlsx", "valid_zip": False, "sheets": [], "missing_sheets": [], "secret_findings": []}
    with zipfile.ZipFile(path) as archive:
        result["valid_zip"] = True
        workbook_xml = archive.read("xl/workbook.xml").decode("utf-8", errors="replace")
        result["sheets"] = re.findall(r'<(?:[A-Za-z_][\w.-]*:)?sheet\b[^>]+name="([^"]+)"', workbook_xml)
        result["missing_sheets"] = [name for name in expected_sheets if name not in result["sheets"]]
        for member in archive.namelist():
            if member.endswith((".xml", ".rels")):
                text = archive.read(member).decode("utf-8", errors="replace")
                result["secret_findings"].extend(scan_text(text))
    result["ok"] = result["valid_zip"] and not result["missing_sheets"] and not result["secret_findings"]
    return result


def validate_text(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    findings = scan_text(text)
    return {"file": str(path), "type": path.suffix.lower().lstrip("."), "secret_findings": findings, "ok": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate workbook structure and scan delivered artifacts for exposed API keys.")
    parser.add_argument("--file", action="append", required=True)
    parser.add_argument("--expect-sheet", action="append", default=[])
    args = parser.parse_args()
    results = []
    for value in args.file:
        path = Path(value).resolve()
        if not path.exists():
            results.append({"file": str(path), "ok": False, "error": "file_not_found"})
        elif path.suffix.lower() == ".xlsx":
            results.append(validate_xlsx(path, args.expect_sheet))
        else:
            results.append(validate_text(path))
    summary = {"ok": all(item.get("ok") for item in results), "results": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
