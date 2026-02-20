"""
publisher.py — Write SKILL.md to ~/.claude/skills/{name}/ and push to GitHub

Convention (from MEMORY.md):
  - Repo name: claude-skill-{name} on ccwriter369-beep
  - Public, MIT license
  - Conventional commits
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SKILLS_DIR = Path("~/.claude/skills").expanduser()
GITHUB_USER = "ccwriter369-beep"


def publish(
    skill_name: str,
    skill_md_content: str,
    no_push: bool = False,
) -> Path:
    """
    Write SKILL.md to ~/.claude/skills/{skill_name}/, init git,
    create GitHub repo, commit and push.

    Returns the path to the skill directory.
    """
    skill_dir = SKILLS_DIR / skill_name

    if skill_dir.exists():
        print(f"  [warn] Skill directory already exists: {skill_dir}")
        print("  Writing SKILL.md and continuing...")
    else:
        skill_dir.mkdir(parents=True)
        print(f"  Created: {skill_dir}")

    # Write SKILL.md
    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(skill_md_content, encoding="utf-8")
    print(f"  Wrote: {skill_md_path}")

    if no_push:
        print("  [--no-push] Skipping GitHub.")
        return skill_dir

    # Git init (idempotent)
    _run(["git", "init"], cwd=skill_dir)

    # Write .gitignore and LICENSE
    _write_gitignore(skill_dir)
    _write_license(skill_dir)

    # Stage + commit
    _run(["git", "add", "."], cwd=skill_dir)
    _run(
        ["git", "commit", "-m", f"feat: initial skill — {skill_name}"],
        cwd=skill_dir,
    )

    # Create GitHub repo
    repo_name = f"claude-skill-{skill_name}"
    print(f"  Creating GitHub repo: {GITHUB_USER}/{repo_name}")
    result = subprocess.run(
        [
            "gh", "repo", "create",
            f"{GITHUB_USER}/{repo_name}",
            "--public",
            "--description", f"Claude Code skill: {skill_name}",
            "--source", str(skill_dir),
            "--push",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # Repo might already exist — try pushing to existing remote
        stderr = result.stderr.strip()
        if "already exists" in stderr or "Name already exists" in stderr:
            print(f"  [warn] Repo already exists. Pushing to existing remote.")
            _ensure_remote(skill_dir, repo_name)
            _run(["git", "push", "-u", "origin", "main"], cwd=skill_dir)
        else:
            print(f"  [error] gh repo create failed: {stderr}", file=sys.stderr)
            print(f"  Skill written locally at {skill_dir}. Push manually.")
            return skill_dir
    else:
        repo_url = result.stdout.strip().split("\n")[-1]
        print(f"  Pushed: {repo_url}")

    return skill_dir


def _ensure_remote(skill_dir: Path, repo_name: str) -> None:
    """Add or update origin remote."""
    remote_url = f"git@github.com:{GITHUB_USER}/{repo_name}.git"
    # Check if origin exists
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=skill_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        _run(["git", "remote", "set-url", "origin", remote_url], cwd=skill_dir)
    else:
        _run(["git", "remote", "add", "origin", remote_url], cwd=skill_dir)


def _write_gitignore(skill_dir: Path) -> None:
    (skill_dir / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n*.pyo\n.DS_Store\n*.egg-info/\n",
        encoding="utf-8",
    )


def _write_license(skill_dir: Path) -> None:
    (skill_dir / "LICENSE").write_text(
        'MIT License\n\nCopyright (c) 2026 ccwriter369-beep\n\n'
        'Permission is hereby granted, free of charge, to any person obtaining a copy '
        'of this software and associated documentation files (the "Software"), to deal '
        'in the Software without restriction, including without limitation the rights '
        'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell '
        'copies of the Software, and to permit persons to whom the Software is '
        'furnished to do so, subject to the following conditions:\n\n'
        'The above copyright notice and this permission notice shall be included in all '
        'copies or substantial portions of the Software.\n\n'
        'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR '
        'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, '
        'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE '
        'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER '
        'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, '
        'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE '
        'SOFTWARE.\n',
        encoding="utf-8",
    )


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [warn] {' '.join(cmd)} exited {result.returncode}: {result.stderr.strip()}")
    return result
