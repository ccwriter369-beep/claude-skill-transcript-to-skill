"""
extractor.py — Dispatch transcript to Gemini, return ExtractionResult

Uses the GeminiClient pattern from content-compiler (stdin redirect).
Prompt loaded from references/extraction-prompt.md (editable).
One repair pass on JSON parse failure.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .input_loader import TranscriptFragment


PROMPT_TEMPLATE_PATH = (
    Path(__file__).parent.parent / "references" / "extraction-prompt.md"
)

REQUIRED_KEYS = {
    "skill_name",
    "domain",
    "description",
    "core_rules",
    "decision_criteria",
    "anti_patterns",
    "workflow_steps",
    "trigger_phrases",
    "examples",
}


@dataclass
class ExtractionResult:
    skill_name: str
    domain: str
    description: str
    core_rules: list[str] = field(default_factory=list)
    decision_criteria: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    workflow_steps: list[str] = field(default_factory=list)
    trigger_phrases: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


def extract(fragment: TranscriptFragment, skill_name_override: Optional[str] = None, max_chars: int = 18000) -> ExtractionResult:
    """
    Dispatch to Gemini for extraction. Returns ExtractionResult.
    Tries once; on JSON failure, sends one repair pass.
    """
    if max_chars and len(fragment.raw_text) > max_chars:
        print(f"  [truncate] {len(fragment.raw_text):,} → {max_chars:,} chars")
        fragment = TranscriptFragment(
            raw_text=fragment.raw_text[:max_chars],
            source_path=fragment.source_path,
            source_title=fragment.source_title,
            domain_hint=fragment.domain_hint,
        )

    prompt = _build_prompt(fragment)

    raw = _invoke_gemini(prompt)

    try:
        result = _parse_json(raw)
    except (ValueError, KeyError) as e:
        print(f"  [warn] First pass JSON parse failed ({e}). Sending repair pass...")
        repair_prompt = _repair_prompt(raw, str(e))
        raw2 = _invoke_gemini(repair_prompt)
        result = _parse_json(raw2)  # Hard fail if still broken

    if skill_name_override:
        result.skill_name = skill_name_override

    return result


def _build_prompt(fragment: TranscriptFragment) -> str:
    """Load template and substitute placeholders."""
    template = PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")

    # Handle the domain_hint conditional block manually
    if fragment.domain_hint:
        domain_block = f"Domain context: {fragment.domain_hint}"
        template = re.sub(
            r"\{%\s*if domain_hint\s*%\}.*?\{%\s*endif\s*%\}",
            domain_block,
            template,
            flags=re.DOTALL,
        )
    else:
        # Remove the whole block
        template = re.sub(
            r"\{%\s*if domain_hint\s*%\}.*?\{%\s*endif\s*%\}\n?",
            "",
            template,
            flags=re.DOTALL,
        )

    template = template.replace("{{transcript}}", fragment.raw_text)
    template = template.replace("{{domain_hint}}", fragment.domain_hint or "")

    return template


def _invoke_gemini(prompt: str) -> str:
    """Write prompt to tempfile and invoke Gemini via stdin redirect."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(prompt)
        f.flush()
        tmppath = f.name

    try:
        result = subprocess.run(
            ["gemini", "--approval-mode", "yolo"],
            stdin=open(tmppath, "r"),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Gemini failed (exit {result.returncode}): {result.stderr[:500]}"
            )
        return result.stdout
    finally:
        os.unlink(tmppath)


def _parse_json(raw: str) -> ExtractionResult:
    """
    Extract the JSON object from Gemini's output.
    Gemini may wrap JSON in prose or code fences — strip them.
    """
    # Try to find a JSON block (code fence or bare)
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Find first { to last }
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in Gemini output")
        json_str = raw[start : end + 1]

    data = json.loads(json_str)

    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        raise KeyError(f"Missing required fields: {missing}")

    return ExtractionResult(
        skill_name=_kebab(data["skill_name"]),
        domain=data["domain"],
        description=data["description"],
        core_rules=_ensure_list(data.get("core_rules", [])),
        decision_criteria=_ensure_list(data.get("decision_criteria", [])),
        anti_patterns=_ensure_list(data.get("anti_patterns", [])),
        workflow_steps=_ensure_list(data.get("workflow_steps", [])),
        trigger_phrases=_ensure_list(data.get("trigger_phrases", [])),
        examples=_ensure_list(data.get("examples", [])),
    )


def _repair_prompt(bad_output: str, error: str) -> str:
    return f"""The following output was supposed to be a valid JSON object but failed to parse.
Error: {error}

Fix it and return ONLY the corrected JSON object with no additional text or code fences.

Original output:
{bad_output}
"""


def _kebab(name: str) -> str:
    """Normalize a skill name to kebab-case."""
    name = re.sub(r"[^a-z0-9-]", "-", name.lower())
    name = re.sub(r"-+", "-", name).strip("-")
    return name[:40]


def _ensure_list(val) -> list:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [val]
    return []
