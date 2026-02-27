#!/usr/bin/env python3
"""Copy files listed in a stack JSON into github-base, preserving paths."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Iterable, List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_repo_root() -> Path:
    """Get repository root path with fallback hierarchy.

    Precedence:
    1. REPO_ROOT environment variable
    2. REPO_ROOT from .env file (loaded above)
    3. Script's parent directory (one level above curadoria/)

    Returns:
        Path to repository root
    """
    if repo_root_env := os.getenv("REPO_ROOT"):
        return Path(repo_root_env).resolve()
    return Path(__file__).resolve().parent.parent


REPO_ROOT = _get_repo_root()


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


def copy_files(source_dir, dest_dir, file_list):
    """Copy files from source to destination directory."""
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    skipped = 0
    copied = 0

    for file_entry in file_list:
        source_file = source_dir / file_entry
        dest_file = dest_path / file_entry

        try:
            if not source_file.exists():
                print(f"⚠️  Warning: File not found: {source_file}")
                skipped += 1
                continue

            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
            copied += 1
        except (FileNotFoundError, IOError) as e:
            print(f"⚠️  Warning: Could not copy {source_file}: {e}")
            skipped += 1
            continue

    print(f"\n✅ Copy completed: {copied} files copied, {skipped} files skipped")
    return copied, skipped


def _copy_paths(repo_root: Path, dest_root: Path, paths: Iterable[str]) -> tuple[List[Path], int]:
    """Copy files from repo_root to dest_root, preserving relative paths.

    Args:
        repo_root: Repository root directory (source base)
        dest_root: Destination directory (can be relative to repo_root or absolute)
        paths: Iterable of relative file paths to copy

    Returns:
        Tuple of (list of copied destination file paths, count of skipped files)
    """
    copied: List[Path] = []
    skipped = 0

    # Resolve destination: if relative, make it relative to repo_root; if absolute, use as-is
    if dest_root.is_absolute():
        final_dest = dest_root
    else:
        final_dest = repo_root / dest_root

    for rel_path in paths:
        rel = Path(rel_path)
        src = repo_root / rel

        try:
            if not src.exists():
                print(f"⚠️  Warning: File not found: {src}")
                skipped += 1
                continue

            dest = final_dest / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied.append(dest)
        except (FileNotFoundError, IOError) as e:
            print(f"⚠️  Warning: Could not copy {src}: {e}")
            skipped += 1
            continue

    return copied, skipped


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
        help="Source type (e.g., java, python) to load stack-<source>.json",
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination directory for generated files. Default: DEST_DIR env var or 'github-base'.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root directory. Default: REPO_ROOT env var or one level above script.",
    )
    parser.add_argument(
        "--stack-dir",
        default=None,
        help="Stack files directory. Default: STACK_DIR env var or script directory.",
    )
    args = parser.parse_args()

    # Set default destination from .env if not provided via command line
    if args.dest is None:
        args.dest = os.getenv("DEST_DIR", f"agents/{args.source}")

    dest_path = Path(args.dest)

    # Resolve paths with precedence: CLI args > env vars > defaults
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        repo_root = REPO_ROOT

    if args.stack_dir:
        stack_dir = Path(args.stack_dir).resolve()
    else:
        stack_dir = Path(__file__).resolve().parent

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
        copied, skipped = _copy_paths(repo_root, dest_path, paths)

        print(f"\n✅ Copy completed: {len(copied)} files copied, {skipped} files skipped")

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

    except Exception as e:
        print(f"Error: {e}")
        return 1

    print(f"\nAll files copied to: {final_dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
