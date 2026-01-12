#!/usr/bin/env python3
"""
Helper script to reorganize flat CTF repos into categorized structure.
Usage: python cleanup_old_repo.py /path/to/old_repo

This script:
1. Scans for *writeup.md files
2. Tries to detect category from content
3. Generates commands to reorganize
4. Creates a new README
"""

import os
import re
import sys
from pathlib import Path

CATEGORIES = {
    "crypto": ["rsa", "aes", "cipher", "encrypt", "decrypt", "xor", "hash", "prime", "modular"],
    "pwn": ["buffer", "overflow", "shellcode", "rop", "bof", "exploit", "canary", "libc", "got", "plt"],
    "rev": ["reverse", "disassembl", "decompil", "binary", "assembly", "ida", "ghidra", "obfuscate"],
    "web": ["sql", "xss", "csrf", "cookie", "session", "http", "php", "javascript", "html", "api", "jwt"],
    "forensics": ["pcap", "wireshark", "memory", "disk", "volatility", "autopsy", "image", "steganography"],
    "osint": ["osint", "google", "social", "geolocation", "metadata"],
    "misc": []  # default fallback
}


def detect_category(content: str, filename: str) -> str:
    """Try to detect category from writeup content."""
    content_lower = content.lower()
    filename_lower = filename.lower()

    # Check explicit category mentions
    if match := re.search(r'\*\*category[:\*]*\s*(\w+)', content_lower):
        cat = match.group(1).strip()
        if cat in CATEGORIES:
            return cat

    # Keyword matching
    for cat, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in content_lower or keyword in filename_lower:
                return cat

    return "misc"


def analyze_repo(repo_path: Path) -> list:
    """Analyze a flat repo structure."""
    challenges = []

    for f in repo_path.iterdir():
        if not f.is_file():
            continue
        if not f.suffix == ".md":
            continue
        if f.name.lower() == "readme.md":
            continue

        content = f.read_text(errors='ignore')
        category = detect_category(content, f.name)

        # Extract challenge name
        name = f.stem.replace("writeup", "").replace("Writeup", "").replace("_", "").replace("-", "_")
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()  # camelCase to snake_case
        name = name.strip("_")

        if not name:
            name = f.stem.lower()

        challenges.append({
            "original_file": f.name,
            "name": name,
            "category": category,
            "content": content
        })

    return challenges


def generate_migration_script(repo_path: Path, challenges: list) -> str:
    """Generate bash commands to reorganize."""
    lines = ["#!/bin/bash", f"# Migration script for {repo_path.name}", "set -e", ""]

    # Create directories
    categories_used = set(c["category"] for c in challenges)
    for cat in sorted(categories_used):
        lines.append(f"mkdir -p {cat}")

    lines.append("")

    # Move files
    for c in challenges:
        src = c["original_file"]
        dst = f"{c['category']}/{c['name']}/{c['name']}_writeup.md"
        lines.append(f"mkdir -p {c['category']}/{c['name']}")
        lines.append(f"mv \"{src}\" \"{dst}\"")

    lines.append("")
    lines.append("echo 'Migration complete! Now run generate_readme.py'")

    return "\n".join(lines)


def generate_readme_template(repo_name: str, challenges: list) -> str:
    """Generate a README for the reorganized repo."""
    lines = [f"# {repo_name} Write-ups", ""]

    # Summary
    by_cat = {}
    for c in challenges:
        by_cat.setdefault(c["category"], []).append(c)

    lines.append("## Challenges")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat in sorted(by_cat.keys()):
        lines.append(f"| {cat.title()} | {len(by_cat[cat])} |")
    lines.append("")

    # Details
    for cat in sorted(by_cat.keys()):
        lines.append(f"### {cat.title()}")
        lines.append("")
        for c in by_cat[cat]:
            link = f"{cat}/{c['name']}/{c['name']}_writeup.md"
            lines.append(f"- [{c['name'].replace('_', ' ').title()}]({link})")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python cleanup_old_repo.py /path/to/repo")
        print("\nThis script analyzes a flat CTF repo and generates migration commands.")
        sys.exit(1)

    repo_path = Path(sys.argv[1]).resolve()

    if not repo_path.exists():
        print(f"Error: {repo_path} does not exist")
        sys.exit(1)

    print(f"Analyzing: {repo_path}")
    challenges = analyze_repo(repo_path)

    if not challenges:
        print("No writeup files found!")
        sys.exit(1)

    print(f"Found {len(challenges)} challenges:")
    for c in challenges:
        print(f"  [{c['category']}] {c['name']} <- {c['original_file']}")

    # Generate migration script
    migration_script = generate_migration_script(repo_path, challenges)
    script_path = repo_path / "migrate.sh"
    script_path.write_text(migration_script)
    print(f"\nGenerated: {script_path}")

    # Generate new README
    readme = generate_readme_template(repo_path.name, challenges)
    readme_path = repo_path / "NEW_README.md"
    readme_path.write_text(readme)
    print(f"Generated: {readme_path}")

    print("\nNext steps:")
    print(f"  1. cd {repo_path}")
    print("  2. Review migrate.sh and NEW_README.md")
    print("  3. chmod +x migrate.sh && ./migrate.sh")
    print("  4. mv NEW_README.md README.md")
    print("  5. Copy scripts/generate_readme.py for future automation")


if __name__ == "__main__":
    main()
