# Extraction Prompt Template

This file is the Gemini prompt template used by extractor.py.
Edit this to tune what gets extracted from transcripts.

Placeholders replaced at runtime:
- `{{transcript}}` — the raw transcript text
- `{{domain_hint}}` — optional domain context (e.g., "YouTube thumbnails")

---

You are an expert at distilling expert content into reusable knowledge structures.

I have a transcript or article below. Your job is to extract the core teachable rules,
decision criteria, anti-patterns, and workflow from it — and package them as a
Claude Code skill.

{% if domain_hint %}
Domain context: {{domain_hint}}
{% endif %}

## Your Task

Read the transcript carefully and extract:

1. **skill_name** — A short kebab-case identifier (e.g., `viral-thumbnail-rules`).
   Should reflect the core domain/topic. Max 40 chars.

2. **domain** — One-line human description of the domain (e.g., "YouTube thumbnail design").

3. **description** — 1-2 sentences describing what the skill does and when to use it.
   Include natural trigger phrases users would say to invoke this skill.

4. **core_rules** — 5-10 distilled rules or principles from the content.
   These are the "always do this" truths the expert teaches.
   Write as complete sentences. Omit filler, keep only what's actionable.

5. **decision_criteria** — 3-6 conditions that indicate when to apply this skill.
   E.g., "When creating content for social media" or "When optimizing for clicks."

6. **anti_patterns** — 3-6 common mistakes or things to avoid.
   Write as "Don't..." or "Avoid..." sentences.

7. **workflow_steps** — 4-8 ordered steps for applying the expert's method.
   Write as imperative verbs. E.g., "Identify the single strongest visual hook."

8. **trigger_phrases** — 5-8 natural language phrases a user might say to trigger this skill.
   E.g., "make this go viral", "improve my thumbnail", "apply the 3-second rule".

9. **examples** — 2-4 concrete examples from the transcript that illustrate the rules.
   Keep these brief (1 sentence each).

## Output Format

Return ONLY a JSON object with exactly these keys. No preamble, no explanation.
Do not wrap in markdown code fences.

{
  "skill_name": "...",
  "domain": "...",
  "description": "...",
  "core_rules": ["...", "..."],
  "decision_criteria": ["...", "..."],
  "anti_patterns": ["...", "..."],
  "workflow_steps": ["...", "..."],
  "trigger_phrases": ["...", "..."],
  "examples": ["...", "..."]
}

## Transcript

{{transcript}}
