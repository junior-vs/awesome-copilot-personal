#!/usr/bin/env python3
"""Copy files listed in a stack JSON into github-base, preserving paths."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Iterable, List


# Configuration: Repository root directory
# Default: one level above the script's directory (parent of 'curadoria/')
# Script location: <repo_root>/curadoria/generate-github-base.py
# REPO_ROOT = <repo_root>/ (one level above)
# You can override this by setting the REPO_ROOT environment variable
REPO_ROOT = Path(os.getenv("REPO_ROOT", Path(__file__).resolve().parent.parent))


def _extract_paths(data: object) -> List[str]:
    """Extract file paths from stack JSON data structure.

    Args:
        data: Stack JSON object (can be dict, list, or string)

    Returns:
        List of file path strings
    """
    if isinstance(data, str):
        return [data]
    if isinstance(data, dict):
        if "files" in data:
            return _extract_paths(data.get("files"))
        path = data.get("path")
        return [path] if isinstance(path, str) else []
    if isinstance(data, list):
        paths: List[str] = []
        for item in data:
            paths.extend(_extract_paths(item))
        return paths
    return []


def _copy_paths(repo_root: Path, dest_root: Path, paths: Iterable[str]) -> List[Path]:
    """Copy files from repo_root to dest_root, preserving relative paths.

    Args:
        repo_root: Repository root directory (source base)
        dest_root: Destination directory (can be relative to repo_root or absolute)
        paths: Iterable of relative file paths to copy

    Returns:
        List of copied destination file paths

    Raises:
        FileNotFoundError: If a source file doesn't exist
    """
    copied: List[Path] = []

    # Resolve destination: if relative, make it relative to repo_root; if absolute, use as-is
    if dest_root.is_absolute():
        final_dest = dest_root
    else:
        final_dest = repo_root / dest_root

    for rel_path in paths:
        rel = Path(rel_path)
        src = repo_root / rel
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src}")

        dest = final_dest / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(dest)

    return copied


def main() -> int:
    """Main entry point for the script.

    Reads a stack-<source>.json file and copies all referenced files
    to the destination directory, preserving relative paths.

    Repository structure:
        REPO_ROOT/
        ├── agents/
        ├── instructions/
        ├── prompts/
        └── curadoria/
            ├── generate-github-base.py (this script)
            ├── stack-<source>.json (input)
            └── github-base/ (output, default)

    Returns:
        0 on success, 1 on error
    """
    repo_root = REPO_ROOT
    script_dir = Path(__file__).resolve().parent

    # Verify repo root exists
    if not repo_root.is_dir():
        print(f"Error: Repository root not found: {repo_root}")
        print("Set REPO_ROOT environment variable to override.")
        return 1

    parser = argparse.ArgumentParser(
        description=(
            "Copy files referenced by a stack JSON into a destination folder, "
            "preserving relative paths."
        )
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Stack identifier (e.g., 'java', 'python') to load stack-<source>.json",
    )
    parser.add_argument(
        "--dest",
        default="github-base",
        help="Destination folder (relative to repo root or absolute path). Created if it doesn't exist.",
    )
    args = parser.parse_args()

    print(f"Using repository root: {repo_root}")
    print(f"Script directory: {script_dir}\n")

    source_file = f"stack-{args.source}.json"
    source_path = (script_dir / source_file).resolve()

    if not source_path.exists():
        print(f"Error: Stack file not found: {source_path}")
        return 1

    print(f"Reading stack file: {source_path.name}")

    with source_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    paths = _extract_paths(data)
    if not paths:
        print("Error: No paths found in the stack JSON.")
        return 1

    # Resolve destination path
    dest_path = Path(args.dest)
    if dest_path.is_absolute():
        final_dest = dest_path
    else:
        final_dest = repo_root / dest_path

    print(f"Found {len(paths)} files to copy")
    print(f"Destination: {final_dest}\n")

    try:
        copied = _copy_paths(repo_root, dest_path, paths)

        print(f"\nSuccessfully copied {len(copied)} files:")

        # Try to show relative paths intelligently
        for item in copied:
            try:
                # If destination is within repo_root, show path relative to repo_root
                rel_path = item.relative_to(repo_root)
                print(f"  {rel_path}")
            except ValueError:
                # If destination is outside repo_root, show path relative to destination
                try:
                    rel_path = item.relative_to(final_dest)
                    print(f"  {rel_path}")
                except ValueError:
                    # Fallback: show absolute path
                    print(f"  {item}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    print(f"\nAll files copied to: {final_dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
