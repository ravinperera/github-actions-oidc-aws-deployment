#!/usr/bin/env python3
"""Dependency-free checks for this public OIDC reference repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REMOTE_PREFIXES = ("http://", "https://", "mailto:", "tel:")
STATIC_CREDENTIAL_MARKERS = (
    "aws-access-key-id:",
    "aws-secret-access-key:",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
)
TOP_LEVEL_PERMISSIONS = re.compile(r"(?m)^permissions\s*:")
WRITE_ALL_PERMISSIONS = re.compile(r"(?mi)^\s*permissions\s*:\s*write-all\s*(?:#.*)?$")


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build a JSON object while rejecting duplicate keys."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def validate_json(errors: list[str]) -> int:
    checked = 0
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        checked += 1
        try:
            json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=reject_duplicate_json_keys,
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
    return checked


def validate_markdown_links(errors: list[str]) -> int:
    checked = 0
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        active_fence: str | None = None

        for line in text.splitlines():
            stripped = line.lstrip()
            marker = None
            if stripped.startswith("```"):
                marker = "```"
            elif stripped.startswith("~~~"):
                marker = "~~~"

            if marker is not None:
                if active_fence is None:
                    active_fence = marker
                elif active_fence == marker:
                    active_fence = None
                continue

            if active_fence is not None:
                continue

            for raw_target in MARKDOWN_LINK.findall(line):
                target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
                if (
                    not target
                    or target.startswith("#")
                    or target.startswith(REMOTE_PREFIXES)
                ):
                    continue
                target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not target:
                    continue
                resolved = (path.parent / target).resolve()
                try:
                    resolved.relative_to(ROOT)
                except ValueError:
                    errors.append(
                        f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}"
                    )
                    continue
                if not resolved.exists():
                    errors.append(
                        f"{path.relative_to(ROOT)}: missing local link target: {raw_target}"
                    )
    return checked


def validate_workflows(errors: list[str]) -> int:
    workflow_dir = ROOT / ".github" / "workflows"
    checked = 0
    if not workflow_dir.exists():
        errors.append(".github/workflows: directory is missing")
        return checked

    for path in sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml"))):
        checked += 1
        text = path.read_text(encoding="utf-8")
        relative_path = path.relative_to(ROOT)

        if "\t" in text:
            errors.append(f"{relative_path}: YAML contains tab indentation")

        if not TOP_LEVEL_PERMISSIONS.search(text):
            errors.append(
                f"{relative_path}: workflow is missing an explicit top-level permissions declaration"
            )

        if WRITE_ALL_PERMISSIONS.search(text):
            errors.append(
                f"{relative_path}: workflow uses broad permissions: write-all"
            )

        for marker in STATIC_CREDENTIAL_MARKERS:
            if marker in text:
                errors.append(
                    f"{relative_path}: static AWS credential marker found: {marker}"
                )
    return checked


def main() -> int:
    errors: list[str] = []
    json_count = validate_json(errors)
    markdown_count = validate_markdown_links(errors)
    workflow_count = validate_workflows(errors)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Validation passed: "
        f"{json_count} JSON file(s), "
        f"{markdown_count} Markdown file(s), "
        f"{workflow_count} workflow file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
