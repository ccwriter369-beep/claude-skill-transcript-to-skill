"""
cli.py — Argument parsing and pipeline orchestration for transcript-to-skill
"""
from __future__ import annotations

import argparse
import sys

from .input_loader import load_file
from .extractor import extract
from .skill_builder import build_skill_md
from .publisher import publish


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="transcript-to-skill",
        description="Convert a transcript or article into a reusable Claude Code skill.",
    )
    parser.add_argument("input", help="Path to the transcript file (.txt or .md)")
    parser.add_argument(
        "--name",
        metavar="NAME",
        help="Kebab-case skill name (auto-derived from content if omitted)",
    )
    parser.add_argument(
        "--domain",
        metavar="HINT",
        help="Domain hint injected into extraction prompt (e.g. 'YouTube thumbnails')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print extracted SKILL.md to stdout; don't save or push",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Write SKILL.md locally but skip GitHub repo creation and push",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=18000,
        metavar="N",
        help="Truncate transcript to N chars before sending to Gemini (default: 18000)",
    )
    args = parser.parse_args()

    print(f"Loading: {args.input}")
    fragment = load_file(args.input, domain_hint=args.domain)
    print(f"  Source title: {fragment.source_title or '(none)'}")
    print(f"  Domain hint:  {fragment.domain_hint or '(none)'}")
    print(f"  Length:       {len(fragment.raw_text):,} chars")

    print("\nExtracting via Gemini...")
    try:
        result = extract(fragment, skill_name_override=args.name, max_chars=args.max_chars)
    except Exception as e:
        print(f"\n[error] Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  Skill name:   {result.skill_name}")
    print(f"  Domain:       {result.domain}")
    print(f"  Rules:        {len(result.core_rules)}")
    print(f"  Steps:        {len(result.workflow_steps)}")

    skill_md = build_skill_md(result, source_path=fragment.source_path)

    if args.dry_run:
        print("\n" + "=" * 60)
        print(skill_md)
        print("=" * 60)
        print("\n[dry-run] Not saved.")
        return

    print(f"\nPublishing to ~/.claude/skills/{result.skill_name}/")
    skill_dir = publish(
        skill_name=result.skill_name,
        skill_md_content=skill_md,
        no_push=args.no_push,
    )

    print(f"\nDone. Skill at: {skill_dir}")
    if not args.no_push:
        print(f"GitHub: https://github.com/ccwriter369-beep/claude-skill-{result.skill_name}")
