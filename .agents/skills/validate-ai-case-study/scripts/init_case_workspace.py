#!/usr/bin/env python3
"""Initialize an ignored workspace for an AI case-study validation run."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


TEMPLATE_MAP = {
    "00-run-state.template.md": "00-run-state.private.md",
    "01-source-ledger.template.md": "01-source-ledger.internal.md",
    "10-case-analysis.template.md": "10-case-analysis.internal.md",
    "20-implementation-log.template.md": "20-implementation-log.internal.md",
    "90-final-brief.template.md": "90-final-brief.internal.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an ignored, template-based case-study workspace."
    )
    parser.add_argument("url", help="Primary public case-study URL (HTTP or HTTPS)")
    parser.add_argument("--slug", help="Lowercase case slug; derived from the URL if omitted")
    parser.add_argument(
        "--date",
        dest="run_date",
        help="Run date in YYYY-MM-DD format (defaults to the local date)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root (defaults to the current Git repository)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Add missing templates to an existing run without overwriting files",
    )
    return parser.parse_args()


def fail(message: str, exit_code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(exit_code)


def validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        fail("URL must be an absolute HTTP or HTTPS URL")
    return value


def slugify(value: str) -> str:
    normalized = unquote(value).lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    normalized = re.sub(r"-+", "-", normalized)[:72].rstrip("-")
    if not normalized:
        fail("could not derive a non-empty ASCII slug; pass --slug explicitly")
    return normalized


def derive_slug(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname or "case"
    host = re.sub(r"^www\.", "", host)
    host_part = host.split(".")[0]
    path_parts = [part for part in parsed.path.split("/") if part]
    path_part = path_parts[-1] if path_parts else "case-study"
    return slugify(f"{host_part}-{path_part}")


def validate_slug(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        fail("--slug must contain only lowercase ASCII letters, digits, and hyphens")
    if len(value) > 72:
        fail("--slug must not exceed 72 characters")
    return value


def resolve_repo_root(explicit_root: Path | None) -> Path:
    if explicit_root is not None:
        root = explicit_root.expanduser().resolve()
    else:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            fail("current directory is not inside a Git repository")
        root = Path(result.stdout.strip()).resolve()

    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or Path(result.stdout.strip()).resolve() != root:
        fail(f"not a Git repository root: {root}")
    return root


def validate_run_date(value: str | None) -> str:
    if value is None:
        return dt.date.today().isoformat()
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError:
        fail("--date must use YYYY-MM-DD format")
    raise AssertionError("unreachable")


def verify_ignored(repo_root: Path, destination: Path) -> None:
    probe = destination / "00-run-state.private.md"
    relative_probe = probe.relative_to(repo_root)
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "check-ignore",
            "-q",
            "--no-index",
            str(relative_probe),
        ],
        check=False,
    )
    if result.returncode != 0:
        fail(
            f"destination is not ignored: {destination}. "
            "Add the required internal-briefs/ rule before continuing."
        )


def initialize_file(target: Path, source: Path, url: str, timestamp: str) -> None:
    shutil.copyfile(source, target)
    text = target.read_text(encoding="utf-8")

    if target.name == "00-run-state.private.md":
        text = text.replace("- Primary URL:\n", f"- Primary URL: {url}\n", 1)
        text = text.replace("- Started:\n", f"- Started: {timestamp}\n", 1)
        text = text.replace("- Last updated:\n", f"- Last updated: {timestamp}\n", 1)
    elif target.name == "01-source-ledger.internal.md":
        text = text.replace("- Access date:\n", f"- Access date: {timestamp[:10]}\n", 1)
        text = text.replace("- URL:\n", f"- URL: {url}\n", 1)

    target.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    url = validate_url(args.url)
    slug = validate_slug(args.slug) if args.slug else derive_slug(url)
    run_date = validate_run_date(args.run_date)
    repo_root = resolve_repo_root(args.repo_root)
    destination = repo_root / "internal-briefs" / "case-studies" / f"{run_date}-{slug}"

    verify_ignored(repo_root, destination)

    if destination.exists() and any(destination.iterdir()) and not args.resume:
        fail(f"run already exists: {destination}; pass --resume to add missing templates")

    template_root = Path(__file__).resolve().parent.parent / "assets" / "case-workspace"
    missing_templates = [name for name in TEMPLATE_MAP if not (template_root / name).is_file()]
    if missing_templates:
        fail(f"missing bundled templates: {', '.join(missing_templates)}")

    destination.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    created: list[Path] = []
    skipped: list[Path] = []

    for template_name, output_name in TEMPLATE_MAP.items():
        target = destination / output_name
        if target.exists():
            skipped.append(target)
            continue
        initialize_file(target, template_root / template_name, url, timestamp)
        created.append(target)

    print(f"workspace: {destination}")
    print("ignore-check: passed")
    for path in created:
        print(f"created: {path.relative_to(repo_root)}")
    for path in skipped:
        print(f"preserved: {path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
