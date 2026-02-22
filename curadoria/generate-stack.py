#!/usr/bin/env python3
"""Generate stack JSON file from directory listings."""

from __future__ import annotations

import json
import re
from pathlib import Path


# Configuration: Repository root directory
# Calculated as one level above the script's directory (parent of 'curadoria/')
# Script location: <repo_root>/curadoria/generate-stack.py
# REPO_ROOT = <repo_root>/ (one level above)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Configuration: directories to include in the stack (relative to REPO_ROOT)
STACK_DIRS = ["agents", "instructions", "prompts"]

# Output file (relative to script directory)
OUTPUT_FILE = "stack.json"

# Regex to extract YAML frontmatter description field
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_DESCRIPTION_RE = re.compile(r"""^description:\s*['"]?(.*?)['"]?\s*$""", re.MULTILINE)


def extract_description(file_path: Path) -> str:
    """Extract the description field from YAML frontmatter of a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    fm_match = _FRONTMATTER_RE.match(content)
    if not fm_match:
        return ""

    frontmatter = fm_match.group(1)
    desc_match = _DESCRIPTION_RE.search(frontmatter)
    if not desc_match:
        return ""

    return desc_match.group(1).strip()


def list_directory(directory: Path, repo_root: Path) -> list[dict[str, str]]:
    """List all files in a directory recursively.

    Args:
        directory: Directory to scan for files
        repo_root: Repository root path (for calculating relative paths)

    Returns:
        List of file dictionaries with type, path, and description
    """
    files = []
    dir_type = directory.name

    for file_path in sorted(directory.rglob("*")):
        if file_path.is_file():
            # Get relative path from repo root
            try:
                rel_path = file_path.relative_to(repo_root)
                # Normalize path separators to backslash (Windows style)
                rel_path_str = str(rel_path).replace("/", "\\")
                description = extract_description(file_path)
                files.append({
                    "type": dir_type,
                    "path": rel_path_str,
                    "description": description,
                })
            except ValueError:
                # File is outside repo root, skip it
                continue

    return files


def main() -> int:
    """Main entry point for the script.

    Scans configured directories from REPO_ROOT and generates stack.json.

    Repository structure:
        REPO_ROOT/
        ├── agents/
        ├── instructions/
        ├── prompts/
        └── curadoria/
            ├── generate-stack.py (this script)
            └── stack.json (output)

    Returns:
        0 on success, 1 on error
    """
    repo_root = REPO_ROOT
    script_dir = Path(__file__).resolve().parent

    # Verify repo root exists
    if not repo_root.is_dir():
        print(f"Error: Repository root not found: {repo_root}")
        return 1

    print(f"Using repository root: {repo_root}")
    print(f"Output directory: {script_dir}\n")

    all_files = []

    # Scan each configured directory relative to repo root
    for dir_name in STACK_DIRS:
        input_dir = repo_root / dir_name
        if not input_dir.is_dir():
            print(f"Warning: Directory not found: {input_dir}")
            continue

        files = list_directory(input_dir, repo_root)
        if files:
            all_files.extend(files)
            print(f"Added {len(files)} files from {dir_name}/")

    if not all_files:
        print("Error: No files found in any directory")
        return 1

    # Generate stack JSON
    output = {"files": all_files}

    output_path = script_dir / OUTPUT_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print(f"\nGenerated {output_path.name} with {len(all_files)} total files")
    print(f"Output file: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
