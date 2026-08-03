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


def validate_json(errors: list[str]) -> int:
    checked = 0
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        checked += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
    return checked


def validate_markdown_links(errors: list[str]) -> int:
    checked = 0
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith("#") or target.startswith(REMOTE_PREFIXES):
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
        if "\t" in text:
            errors.append(f"{path.relative_to(ROOT)}: YAML contains tab indentation")
        for marker in STATIC_CREDENTIAL_MARKERS:
            if marker in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: static AWS credential marker found: {marker}"
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
