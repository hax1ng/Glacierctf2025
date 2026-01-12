#!/usr/bin/env python3
"""
Auto-generates README.md for CTF write-up repositories.
Scans category directories for challenges and write-ups.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# Configuration - edit these for each CTF
CTF_CONFIG = {
    "name": "UofTCTF 2026",
    "url": "https://ctf.uoftctf.org/",
    "date": "January 2026",
    "team": "Solo",
    "placement": "",  # e.g., "15th / 500 teams"
    "categories": ["crypto", "forensics", "misc", "osint", "pwn", "rev", "web"],
}

# Category display names and emojis
CATEGORY_META = {
    "crypto": {"emoji": "🔐", "name": "Cryptography"},
    "forensics": {"emoji": "🔍", "name": "Forensics"},
    "misc": {"emoji": "🎲", "name": "Miscellaneous"},
    "osint": {"emoji": "🌐", "name": "OSINT"},
    "pwn": {"emoji": "💥", "name": "Binary Exploitation"},
    "rev": {"emoji": "⚙️", "name": "Reverse Engineering"},
    "web": {"emoji": "🌍", "name": "Web"},
    "hardware": {"emoji": "🔌", "name": "Hardware"},
    "mobile": {"emoji": "📱", "name": "Mobile"},
    "blockchain": {"emoji": "⛓️", "name": "Blockchain"},
}


def find_writeup(challenge_path: Path) -> Path | None:
    """Find write-up file in challenge directory."""
    for pattern in ["*_writeup.md", "*writeup.md", "writeup.md", "WRITEUP.md", "solution.md"]:
        matches = list(challenge_path.glob(pattern))
        if matches:
            return matches[0]
    return None


def extract_metadata(writeup_path: Path) -> dict:
    """Extract metadata from write-up file."""
    metadata = {"points": "", "difficulty": "", "solved": True, "flag": ""}

    try:
        content = writeup_path.read_text()

        # Extract points
        if match := re.search(r'\*\*Points:\*\*\s*(\d+)', content):
            metadata["points"] = match.group(1)

        # Extract flag (to confirm solved)
        if match := re.search(r'`(uoftctf\{[^}]+\})`|Flag:\*\*\s*`([^`]+)`', content):
            metadata["flag"] = match.group(1) or match.group(2)
            metadata["solved"] = True

    except Exception:
        pass

    return metadata


def scan_challenges(repo_root: Path) -> dict:
    """Scan repository for all challenges and write-ups."""
    challenges = {}

    for category in CTF_CONFIG["categories"]:
        cat_path = repo_root / category
        if not cat_path.exists():
            continue

        challenges[category] = []

        for challenge_dir in sorted(cat_path.iterdir()):
            if not challenge_dir.is_dir():
                continue
            if challenge_dir.name.startswith(('.', '_')):
                continue

            writeup = find_writeup(challenge_dir)
            metadata = extract_metadata(writeup) if writeup else {}

            challenges[category].append({
                "name": challenge_dir.name.replace("_", " ").title(),
                "dir": challenge_dir.name,
                "writeup": writeup.name if writeup else None,
                "solved": writeup is not None,
                **metadata
            })

    return challenges


def generate_badge(solved: int, total: int) -> str:
    """Generate shields.io badge URL."""
    pct = int((solved / total) * 100) if total > 0 else 0
    color = "brightgreen" if pct >= 80 else "green" if pct >= 60 else "yellow" if pct >= 40 else "orange"
    return f"![Solved](https://img.shields.io/badge/Solved-{solved}%2F{total}-{color})"


def generate_readme(repo_root: Path) -> str:
    """Generate the complete README content."""
    challenges = scan_challenges(repo_root)

    total_challenges = sum(len(c) for c in challenges.values())
    total_solved = sum(1 for cats in challenges.values() for c in cats if c["solved"])

    lines = []

    # Header
    lines.append(f"# {CTF_CONFIG['name']} Write-ups")
    lines.append("")
    lines.append(f"{generate_badge(total_solved, total_challenges)}")
    lines.append("")

    # CTF Info
    lines.append("## CTF Information")
    lines.append("")
    lines.append(f"- **Event:** [{CTF_CONFIG['name']}]({CTF_CONFIG['url']})")
    lines.append(f"- **Date:** {CTF_CONFIG['date']}")
    lines.append(f"- **Team:** {CTF_CONFIG['team']}")
    if CTF_CONFIG['placement']:
        lines.append(f"- **Placement:** {CTF_CONFIG['placement']}")
    lines.append("")

    # Quick Stats
    lines.append("## Challenges")
    lines.append("")

    # Summary table
    lines.append("| Category | Solved | Total |")
    lines.append("|----------|--------|-------|")
    for cat in CTF_CONFIG["categories"]:
        if cat not in challenges:
            continue
        cat_meta = CATEGORY_META.get(cat, {"emoji": "📁", "name": cat.title()})
        solved = sum(1 for c in challenges[cat] if c["solved"])
        total = len(challenges[cat])
        lines.append(f"| {cat_meta['emoji']} {cat_meta['name']} | {solved} | {total} |")
    lines.append("")

    # Detailed challenge tables per category
    for cat in CTF_CONFIG["categories"]:
        if cat not in challenges or not challenges[cat]:
            continue

        cat_meta = CATEGORY_META.get(cat, {"emoji": "📁", "name": cat.title()})
        lines.append(f"### {cat_meta['emoji']} {cat_meta['name']}")
        lines.append("")
        lines.append("| Challenge | Points | Write-up |")
        lines.append("|-----------|--------|----------|")

        for chall in challenges[cat]:
            name = chall["name"]
            points = chall.get("points", "-")

            if chall["solved"] and chall["writeup"]:
                writeup_link = f"[Write-up]({cat}/{chall['dir']}/{chall['writeup']})"
            else:
                writeup_link = "❌"

            lines.append(f"| {name} | {points} | {writeup_link} |")

        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    return "\n".join(lines)


def main():
    repo_root = Path(__file__).parent.parent
    readme_content = generate_readme(repo_root)

    readme_path = repo_root / "README.md"
    readme_path.write_text(readme_content)
    print(f"Generated {readme_path}")

    # Also output stats
    challenges = scan_challenges(repo_root)
    total = sum(len(c) for c in challenges.values())
    solved = sum(1 for cats in challenges.values() for c in cats if c["solved"])
    print(f"Stats: {solved}/{total} challenges solved")


if __name__ == "__main__":
    main()
