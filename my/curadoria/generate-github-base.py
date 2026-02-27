#!/usr/bin/env python3
"""Copy files listed in a stack JSON into github-base, preserving paths.

This script provides a functional approach to copying files based on stack JSON
configurations, with comprehensive error handling and flexible path resolution.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import dataclass
from enum import Enum
from functools import reduce
from pathlib import Path
from typing import Callable, Iterable, List, TypeAlias

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Type aliases for clarity
JsonData: TypeAlias = dict | list | str | None
PathList: TypeAlias = list[str]


class Status(Enum):
    """File copy operation status."""
    COPIED = "copied"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class CopyResult:
    """Result of a single file copy operation."""
    source: Path
    destination: Path | None
    status: Status
    error: str | None = None


@dataclass(frozen=True)
class CopyStats:
    """Statistics from a batch copy operation."""
    copied: list[Path]
    skipped: int

    @property
    def total(self) -> int:
        """Total files processed."""
        return len(self.copied) + self.skipped

    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        return (len(self.copied) / self.total * 100) if self.total > 0 else 0.0


@dataclass(frozen=True)
class Config:
    """Application configuration with precedence: CLI > ENV > Defaults."""
    repo_root: Path
    stack_dir: Path
    dest_dir: Path
    source: str

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Config:
        """Create configuration from CLI arguments and environment.

        Args:
            args: Parsed command line arguments

        Returns:
            Immutable Config object
        """
        script_dir = Path(__file__).resolve().parent

        # Resolve repo root: CLI > ENV > Default (parent of script)
        repo_root = (
            Path(args.repo_root).resolve() if args.repo_root
            else Path(os.getenv("REPO_ROOT", script_dir.parent)).resolve()
        )

        # Resolve stack directory: CLI > ENV > Default (script dir)
        stack_dir = (
            Path(args.stack_dir).resolve() if args.stack_dir
            else Path(os.getenv("STACK_DIR", script_dir)).resolve()
        )

        # Resolve destination: CLI > ENV > Default
        dest_default = os.getenv("DEST_DIR", f"agents/{args.source}")
        dest_dir = Path(args.dest if args.dest else dest_default)

        return cls(
            repo_root=repo_root,
            stack_dir=stack_dir,
            dest_dir=dest_dir,
            source=args.source
        )




# ============================================================================
# Pure Functions - No side effects
# ============================================================================

def extract_paths(data: JsonData) -> PathList:
    """Extract file paths from stack JSON data structure (pure function).

    Uses recursive pattern matching to traverse nested structures.

    Args:
        data: Stack JSON object (can be dict, list, or string)

    Returns:
        List of file path strings
    """
    match data:
        case str():
            return [data]
        case dict():
            # Prefer 'files' key, fall back to 'path' key
            if "files" in data:
                return extract_paths(data["files"])
            if path := data.get("path"):
                return [path] if isinstance(path, str) else []
            return []
        case list():
            # Flatten nested lists using reduce
            return reduce(
                lambda acc, item: acc + extract_paths(item),
                data,
                []
            )
        case _:
            return []


def resolve_destination(dest: Path, repo_root: Path) -> Path:
    """Resolve destination path: absolute paths stay, relative become relative to repo_root.

    Args:
        dest: Destination path (relative or absolute)
        repo_root: Repository root directory

    Returns:
        Resolved absolute destination path
    """
    return dest if dest.is_absolute() else repo_root / dest


def copy_single_file(src: Path, dest: Path) -> CopyResult:
    """Copy a single file, returning result status (pure-ish, has I/O side effects).

    Args:
        src: Source file path
        dest: Destination file path

    Returns:
        CopyResult with operation status
    """
    if not src.exists():
        return CopyResult(
            source=src,
            destination=None,
            status=Status.SKIPPED,
            error="File not found"
        )

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return CopyResult(
            source=src,
            destination=dest,
            status=Status.COPIED,
            error=None
        )
    except (FileNotFoundError, IOError, PermissionError) as e:
        return CopyResult(
            source=src,
            destination=None,
            status=Status.FAILED,
            error=str(e)
        )


def copy_files_batch(
    repo_root: Path,
    dest_root: Path,
    paths: Iterable[str]
) -> list[CopyResult]:
    """Copy multiple files from repo_root to dest_root, preserving paths.

    Args:
        repo_root: Repository root directory (source base)
        dest_root: Destination directory (resolved to absolute)
        paths: Iterable of relative file paths to copy

    Returns:
        List of CopyResult objects
    """
    final_dest = resolve_destination(dest_root, repo_root)

    # Use list comprehension for functional-style batch processing
    return [
        copy_single_file(repo_root / rel_path, final_dest / rel_path)
        for rel_path in (Path(p) for p in paths)
    ]


def aggregate_results(results: list[CopyResult]) -> CopyStats:
    """Aggregate copy results into statistics (pure function).

    Args:
        results: List of CopyResult objects

    Returns:
        CopyStats with aggregated information
    """
    copied = [r.destination for r in results if r.status == Status.COPIED and r.destination]
    skipped = sum(1 for r in results if r.status in (Status.SKIPPED, Status.FAILED))

    return CopyStats(copied=copied, skipped=skipped)


# ============================================================================
# Impure Functions - Side effects (I/O, printing)
# ============================================================================

def log_warning(message: str) -> None:
    """Log a warning message to stdout."""
    print(f"⚠️  Warning: {message}")


def log_results(results: list[CopyResult]) -> None:
    """Log individual copy results, showing only warnings."""
    for result in results:
        if result.status in (Status.SKIPPED, Status.FAILED):
            log_warning(f"{result.error}: {result.source}")


def log_stats(stats: CopyStats) -> None:
    """Log aggregated statistics."""
    print(f"\n✅ Copy completed: {len(stats.copied)} files copied, {stats.skipped} files skipped")
    if stats.total > 0:
        print(f"   Success rate: {stats.success_rate:.1f}%")


def log_copied_files(copied: list[Path], repo_root: Path, dest_root: Path) -> None:
    """Log list of successfully copied files with intelligent path resolution."""
    if not copied:
        return

    print("\nCopied files:")
    for item in copied:
        # Try to show relative paths for better readability
        try:
            rel_path = item.relative_to(repo_root)
            print(f"  {rel_path}")
        except ValueError:
            try:
                rel_path = item.relative_to(dest_root)
                print(f"  {rel_path}")
            except ValueError:
                print(f"  {item}")


def load_stack_json(stack_path: Path) -> JsonData:
    """Load and parse stack JSON file.

    Args:
        stack_path: Path to stack JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If stack file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    with stack_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_config(config: Config) -> tuple[bool, str | None]:
    """Validate configuration directories exist.

    Args:
        config: Application configuration

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not config.repo_root.is_dir():
        return False, f"Repository root not found: {config.repo_root}\nSet REPO_ROOT environment variable."

    stack_file = config.stack_dir / f"stack-{config.source}.json"
    if not stack_file.exists():
        return False, f"Stack file not found: {stack_file}"

    return True, None


# ============================================================================
# CLI and Main Entry Point
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Copy files referenced by a stack JSON into a destination folder, preserving relative paths.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --source java
  %(prog)s --source python --dest build/output
  %(prog)s --source java --repo-root /custom/path

Environment Variables:
  REPO_ROOT   Repository root directory
  STACK_DIR   Stack files directory
  DEST_DIR    Default destination directory
        """
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Stack identifier (e.g., 'java', 'python') to load stack-<source>.json"
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination folder. Default: DEST_DIR env var or 'agents/<source>'"
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root directory. Default: REPO_ROOT env var or script parent"
    )
    parser.add_argument(
        "--stack-dir",
        default=None,
        help="Stack files directory. Default: STACK_DIR env var or script directory"
    )

    return parser




def main() -> int:
    """Main entry point for the script.

    Orchestrates the file copying pipeline:
    1. Parse arguments and build configuration
    2. Validate configuration
    3. Load and parse stack JSON
    4. Extract file paths
    5. Copy files (functional batch operation)
    6. Aggregate and report results

    Returns:
        0 on success, 1 on error
    """
    # Parse arguments and create configuration
    parser = create_parser()
    args = parser.parse_args()
    config = Config.from_args(args)

    # Display configuration
    print(f"Configuration:")
    print(f"  Repository root: {config.repo_root}")
    print(f"  Stack directory: {config.stack_dir}")
    print(f"  Destination: {config.dest_dir}")
    print(f"  Source: {config.source}\n")

    # Validate configuration
    is_valid, error = validate_config(config)
    if not is_valid:
        print(f"Error: {error}")
        return 1

    # Load stack JSON
    stack_file = config.stack_dir / f"stack-{config.source}.json"
    print(f"Reading stack file: {stack_file.name}")

    try:
        data = load_stack_json(stack_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading stack file: {e}")
        return 1

    # Extract paths using pure function
    paths = extract_paths(data)
    if not paths:
        print("Error: No paths found in the stack JSON.")
        return 1

    print(f"Found {len(paths)} files to copy\n")

    # Copy files (functional batch operation)
    results = copy_files_batch(config.repo_root, config.dest_dir, paths)

    # Log warnings for failed operations
    log_results(results)

    # Aggregate results and log statistics
    stats = aggregate_results(results)
    log_stats(stats)

    # Show successfully copied files
    final_dest = resolve_destination(config.dest_dir, config.repo_root)
    log_copied_files(stats.copied, config.repo_root, final_dest)

    print(f"\nAll files copied to: {final_dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
