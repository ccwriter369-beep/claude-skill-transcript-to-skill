#!/usr/bin/env python3
"""
transcript-to-skill — entry point

Convert a transcript, article, or workflow document into a reusable Claude Code skill.

Usage:
    python3 transcript_to_skill.py <file> [options]
"""
import sys
from pathlib import Path

# Allow running from the skill directory directly
sys.path.insert(0, str(Path(__file__).parent))

from transcript_to_skill.cli import main

if __name__ == "__main__":
    main()
