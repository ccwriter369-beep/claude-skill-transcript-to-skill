"""
input_loader.py — Load transcript files into TranscriptFragment

Supports .txt and .md files. For .md files, parses YAML frontmatter
to extract title and domain_hint if present.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TranscriptFragment:
    raw_text: str
    source_path: str
    source_title: Optional[str] = None
    domain_hint: Optional[str] = None


def load_file(path: str, domain_hint: Optional[str] = None) -> TranscriptFragment:
    """Load a .txt or .md file into a TranscriptFragment."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")

    raw = p.read_text(encoding="utf-8")

    title: Optional[str] = None
    fm_domain: Optional[str] = None

    if p.suffix == ".md":
        raw, title, fm_domain = _parse_frontmatter(raw)

    return TranscriptFragment(
        raw_text=raw.strip(),
        source_path=str(p),
        source_title=title,
        domain_hint=domain_hint or fm_domain,
    )


def _parse_frontmatter(text: str) -> tuple[str, Optional[str], Optional[str]]:
    """
    Extract YAML frontmatter from markdown text.

    Returns (body_text, title, domain_hint).
    Looks for `title:` and `domain:` keys in frontmatter.
    """
    match = re.match(r"^---\n(.*?)\n---\n?(.*)", text, re.DOTALL)
    if not match:
        return text, None, None

    fm_raw, body = match.group(1), match.group(2)

    title = _fm_value(fm_raw, "title")
    domain = _fm_value(fm_raw, "domain")

    return body, title, domain


def _fm_value(fm_text: str, key: str) -> Optional[str]:
    """Extract a simple key: value from raw frontmatter text."""
    match = re.search(rf"^{key}:\s*(.+)$", fm_text, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return None
