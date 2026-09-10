from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from _common import atomic_write_json, ensure_project_dirs, read_json, utc_now


STATE_VERSION = "1.0"


def project_paths(project_dir: Path) -> tuple[Path, Path]:
    return project_dir / "project-config.json", project_dir / ".video-research" / "state.json"


def init_project(args: argparse.Namespace) -> dict:
    project_dir = Path(args.project_dir).resolve()
    ensure_project_dirs(project_dir)
    config_path, state_path = project_paths(project_dir)
    now = utc_now()
    config = read_json(config_path, {}) or {}
    config.update(
        {
            "project_id": config.get("project_id") or f"vr_{uuid.uuid4().hex[:12]}",
            "project_name": args.name or config.get("project_name") or project_dir.name,
            "research_object": args.research_object or config.get("research_object") or "",
            "market": args.market or config.get("market") or "",
            "languages": args.languages or config.get("languages") or [],
            "platforms": args.platforms or config.get("platforms") or [],
            "date_range": config.get("date_range") or {"start": args.date_from, "end": args.date_to},
            "research_goal": args.goal or config.get("research_goal") or "",
            "requested_deliverables": args.deliverables or config.get("requested_deliverables") or [],
            "include_rules": config.get("include_rules") or [],
            "exclude_rules": config.get("exclude_rules") or [],
            "journey_hypothesis": config.get("journey_hypothesis") or [],
            "created_at": config.get("created_at") or now,
            "updated_at": now,
            "schema_version": "1.0",
        }
    )
    state = read_json(state_path, {}) or {}
    state.update(
        {
            "state_version": STATE_VERSION,
            "project_id": config["project_id"],
            "config_updated_at": now,
            "skills": state.get("skills") or {},
            "artifacts": state.get("artifacts") or [],
            "collections": state.get("collections") or [],
            "search_queries": state.get("search_queries") or [],
            "journey_revisions": state.get("journey_revisions") or [],
            "api_usage": state.get("api_usage") or {},
            "last_successful_step": state.get("last_successful_step"),
            "pending_decisions": state.get("pending_decisions") or [],
            "updated_at": now,
        }
    )
    atomic_write_json(config_path, config)
    atomic_write_json(state_path, state)
    return {"project_dir": str(project_dir), "config": str(config_path), "state": str(state_path), "project_id": config["project_id"]}


def update_skill(args: argparse.Namespace) -> dict:
    project_dir = Path(args.project_dir).resolve()
    _, state_path = project_paths(project_dir)
    state = read_json(state_path, {}) or {}
    skills = state.setdefault("skills", {})
    entry = skills.setdefault(args.skill, {})
    entry.update({"status": args.status, "updated_at": utc_now()})
    if args.note:
        entry["note"] = args.note
    if args.last_step:
        state["last_successful_step"] = args.last_step
    state["updated_at"] = utc_now()
    atomic_write_json(state_path, state)
    return {"skill": args.skill, "status": args.status, "state": str(state_path)}


def register_artifact(args: argparse.Namespace) -> dict:
    project_dir = Path(args.project_dir).resolve()
    _, state_path = project_paths(project_dir)
    state = read_json(state_path, {}) or {}
    artifact_path = str(Path(args.path).resolve())
    artifacts = state.setdefault("artifacts", [])
    artifacts[:] = [item for item in artifacts if not (item.get("type") == args.type and item.get("path") == artifact_path)]
    artifacts.append(
        {
            "type": args.type,
            "path": artifact_path,
            "status": args.status,
            "skill": args.skill,
            "version": args.version,
            "created_at": utc_now(),
        }
    )
    state["updated_at"] = utc_now()
    atomic_write_json(state_path, state)
    return artifacts[-1]


def show_status(args: argparse.Namespace) -> dict:
    project_dir = Path(args.project_dir).resolve()
    config_path, state_path = project_paths(project_dir)
    return {"config": read_json(config_path, {}), "state": read_json(state_path, {})}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Create and maintain video research project state.")
    sub = root.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--project-dir", required=True)
    init.add_argument("--name")
    init.add_argument("--research-object")
    init.add_argument("--market")
    init.add_argument("--languages", nargs="*")
    init.add_argument("--platforms", nargs="*")
    init.add_argument("--date-from")
    init.add_argument("--date-to")
    init.add_argument("--goal")
    init.add_argument("--deliverables", nargs="*")
    init.set_defaults(handler=init_project)

    skill = sub.add_parser("skill")
    skill.add_argument("--project-dir", required=True)
    skill.add_argument("--skill", required=True)
    skill.add_argument("--status", required=True, choices=["not_started", "in_progress", "partial", "complete", "failed"])
    skill.add_argument("--note")
    skill.add_argument("--last-step")
    skill.set_defaults(handler=update_skill)

    artifact = sub.add_parser("artifact")
    artifact.add_argument("--project-dir", required=True)
    artifact.add_argument("--type", required=True)
    artifact.add_argument("--path", required=True)
    artifact.add_argument("--skill", required=True)
    artifact.add_argument("--status", default="complete")
    artifact.add_argument("--version", default="1")
    artifact.set_defaults(handler=register_artifact)

    status = sub.add_parser("status")
    status.add_argument("--project-dir", required=True)
    status.set_defaults(handler=show_status)
    return root


if __name__ == "__main__":
    args = parser().parse_args()
    print(json.dumps(args.handler(args), ensure_ascii=False, indent=2))
