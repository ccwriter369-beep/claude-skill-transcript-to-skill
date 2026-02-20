---
name: transcript-to-skill
description: |
  Convert a transcript, article, or workflow document into a reusable Claude Code skill.
  Use when user says: "convert this transcript to a skill", "make a skill from this",
  "extract a skill from [file/URL/content]", "turn this into a reusable skill",
  "encode this workflow as a skill", "make this reusable", "skill-ify this",
  or provides a video transcript or expert content and wants to package it.
  Dispatches extraction to Gemini, outputs a properly formatted SKILL.md, and
  publishes to ~/.claude/skills/ with a GitHub repo (ccwriter369-beep/claude-skill-{name}).
---

# Transcript to Skill

Convert expert content (transcripts, articles, how-to guides) into reusable Claude Code skills.

## Quick Start

```bash
# From a file
python3 ~/.claude/skills/transcript-to-skill/transcript_to_skill.py input.txt

# With explicit name and domain hint
python3 ~/.claude/skills/transcript-to-skill/transcript_to_skill.py input.md \
  --name viral-thumbnail-rules --domain "YouTube thumbnails"

# Dry run — see extracted SKILL.md without saving
python3 ~/.claude/skills/transcript-to-skill/transcript_to_skill.py input.txt --dry-run

# Skip GitHub push (local only)
python3 ~/.claude/skills/transcript-to-skill/transcript_to_skill.py input.txt --no-push
```

## Pipeline

```
file → input_loader → TranscriptFragment
                             ↓
                       extractor (Gemini)
                             ↓
                       ExtractionResult (JSON)
                             ↓
                       skill_builder → SKILL.md
                             ↓
                       publisher → ~/.claude/skills/{name}/ + GitHub
```

## Flags

| Flag | Description |
|------|-------------|
| `--name NAME` | Kebab-case skill name (auto-derived from content if omitted) |
| `--domain HINT` | Domain hint injected into extraction prompt |
| `--dry-run` | Print SKILL.md to stdout, don't write or push |
| `--no-push` | Write locally but skip GitHub repo creation and push |

## Extraction Prompt

The Gemini extraction prompt is at `references/extraction-prompt.md` — edit it to
tune what Gemini extracts from transcripts. The prompt is a Jinja2-style template
with `{{transcript}}` and `{{domain_hint}}` placeholders.

## Output Structure

Generated SKILL.md follows the standard frontmatter format with:
- `name`, `description` (with embedded trigger phrases)
- `source`, `extracted` date metadata
- Sections: Core Rules, When to Apply, Anti-Patterns, Workflow, Examples
