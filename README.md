# transcript-to-skill

Claude Code skill that converts transcripts, articles, and how-to guides into reusable Claude Code skills — extracts rules, workflows, trigger phrases, and anti-patterns into a structured SKILL.md.

## Install

```bash
cp -r . ~/.claude/skills/transcript-to-skill/
```

## Usage

```bash
# From a file
python3 ~/.claude/skills/transcript-to-skill/transcript_to_skill.py input.txt

# With explicit name and domain hint
python3 ~/.claude/skills/transcript-to-skill/transcript_to_skill.py input.md \
  --name my-skill --domain "topic area"

# Dry run — preview without saving
python3 ~/.claude/skills/transcript-to-skill/transcript_to_skill.py input.txt --dry-run
```

## Trigger Phrases

- "convert this transcript to a skill"
- "make a skill from this"
- "extract a skill from this content"
- "turn this into a reusable skill"
- "skill-ify this"

## What's Included

- `SKILL.md` — full extraction workflow and skill design guidelines
- `transcript_to_skill.py` — CLI pipeline: load → extract (Gemini) → build → publish
- `references/` — extraction prompt templates

## License

MIT
