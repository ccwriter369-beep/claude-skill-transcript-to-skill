"""
skill_builder.py — Convert ExtractionResult into a SKILL.md string
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .extractor import ExtractionResult


def build_skill_md(result: "ExtractionResult", source_path: str) -> str:
    """Render an ExtractionResult into a complete SKILL.md string."""

    trigger_phrases = result.trigger_phrases
    # Embed trigger phrases into description so Claude can discover the skill
    trigger_list = ", ".join(f'"{t}"' for t in trigger_phrases[:4])
    description_body = result.description
    if trigger_phrases:
        description_body += f" Use when user says: {trigger_list}."

    today = date.today().isoformat()

    lines = [
        "---",
        f"name: {result.skill_name}",
        "description: |",
        f"  {description_body}",
        f"source: \"{source_path}\"",
        f"extracted: \"{today}\"",
        "---",
        "",
        f"# {_title(result.skill_name, result.domain)}",
        "",
    ]

    if result.core_rules:
        lines += ["## Core Rules", ""]
        for rule in result.core_rules:
            lines.append(f"- {rule}")
        lines.append("")

    if result.decision_criteria:
        lines += ["## When to Apply", ""]
        for criterion in result.decision_criteria:
            lines.append(f"- {criterion}")
        lines.append("")

    if result.anti_patterns:
        lines += ["## Anti-Patterns", ""]
        for ap in result.anti_patterns:
            lines.append(f"- {ap}")
        lines.append("")

    if result.workflow_steps:
        lines += ["## Workflow", ""]
        for i, step in enumerate(result.workflow_steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    if result.examples:
        lines += ["## Examples", ""]
        for ex in result.examples:
            lines.append(f"- {ex}")
        lines.append("")

    return "\n".join(lines)


def _title(skill_name: str, domain: str) -> str:
    """Produce a display title: prefer domain if rich, else title-case the skill name."""
    if domain and len(domain) > 3:
        return domain.title()
    return " ".join(w.capitalize() for w in skill_name.split("-"))
