#!/usr/bin/env python3
"""Generate stack JSON file from directory listings.

This script provides a functional approach to scanning directories and extracting
metadata from markdown files with YAML frontmatter, generating a structured JSON output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from functools import reduce
from pathlib import Path
from typing import Callable, Iterable, TypeAlias

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Type aliases for clarity
FileList: TypeAlias = list["FileEntry"]
DirectoryScan: TypeAlias = tuple[str, FileList]

# Regex patterns (compiled once for performance)
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_DESCRIPTION_RE = re.compile(r"""^description:\s*['"]?(.*?)['"]?\s*$""", re.MULTILINE)


@dataclass(frozen=True)
class FileEntry:
    """Represents a file with metadata extracted from frontmatter."""
    type: str
    path: str
    description: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass(frozen=True)
class Config:
    """Application configuration with precedence: CLI > ENV > Defaults."""
    repo_root: Path
    stack_dirs: list[str]
    output_file: str
    output_dir: Path

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

        # Stack directories: CLI > ENV > Default
        stack_dirs = (
            args.dirs if args.dirs
            else os.getenv("STACK_DIRS", "agents,instructions,prompts,skills,plugins,hooks").split(",")
        )

        # Output file: CLI > ENV > Default
        output_file = args.output or os.getenv("STACK_OUTPUT", "stack.json")

        # Output directory: CLI > ENV > Default (script dir)
        output_dir = (
            Path(args.output_dir).resolve() if args.output_dir
            else Path(os.getenv("OUTPUT_DIR", script_dir)).resolve()
        )

        return cls(
            repo_root=repo_root,
            stack_dirs=stack_dirs,
            output_file=output_file,
            output_dir=output_dir
        )


@dataclass(frozen=True)
class ScanStats:
    """Statistics from directory scanning operation."""
    total_files: int
    directories_scanned: int
    files_with_descriptions: int

    @property
    def files_without_descriptions(self) -> int:
        """Files without description metadata."""
        return self.total_files - self.files_with_descriptions

    @property
    def description_rate(self) -> float:
        """Percentage of files with descriptions."""
        return (self.files_with_descriptions / self.total_files * 100) if self.total_files > 0 else 0.0




# ============================================================================
# Pure Functions - No side effects
# ============================================================================

def extract_frontmatter(content: str) -> str | None:
    """Extract YAML frontmatter from markdown content (pure function).

    Args:
        content: Markdown file content

    Returns:
        Frontmatter content or None if not found
    """
    match = _FRONTMATTER_RE.match(content)
    return match.group(1) if match else None


def extract_description_from_frontmatter(frontmatter: str) -> str:
    """Extract description field from YAML frontmatter (pure function).

    Args:
        frontmatter: YAML frontmatter content

    Returns:
        Description text or empty string if not found
    """
    match = _DESCRIPTION_RE.search(frontmatter)
    return match.group(1).strip() if match else ""


def read_file_safe(file_path: Path) -> str | None:
    """Safely read file content, returning None on error.

    Args:
        file_path: Path to file to read

    Returns:
        File content or None if read fails
    """
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def extract_description(file_path: Path) -> str:
    """Extract description from markdown file frontmatter.

    Functional composition of: read -> extract frontmatter -> extract description

    Args:
        file_path: Path to markdown file

    Returns:
        Description text or empty string
    """
    content = read_file_safe(file_path)
    if not content:
        return ""

    frontmatter = extract_frontmatter(content)
    if not frontmatter:
        return ""

    return extract_description_from_frontmatter(frontmatter)


def normalize_path(file_path: Path, repo_root: Path) -> str | None:
    """Normalize file path relative to repo root (pure function).

    Args:
        file_path: Absolute file path
        repo_root: Repository root path

    Returns:
        Normalized path string with backslashes, or None if file is outside repo
    """
    try:
        rel_path = file_path.relative_to(repo_root)
        return str(rel_path).replace("/", "\\")
    except ValueError:
        return None


def create_file_entry(file_path: Path, repo_root: Path, dir_type: str) -> FileEntry | None:
    """Create FileEntry from a file or directory path (pure-ish, reads file if needed).

    For regular files: extracts description from frontmatter
    For directories (skills/plugins): uses empty description

    Args:
        file_path: Path to file or directory
        repo_root: Repository root path
        dir_type: Type/category of the file (e.g., 'agents', 'instructions', 'skills', 'plugins')

    Returns:
        FileEntry or None if path is outside repo root
    """
    normalized_path = normalize_path(file_path, repo_root)
    if not normalized_path:
        return None

    # For directories (skills, plugins), don't extract description
    # For files, extract description from frontmatter
    description = "" if file_path.is_dir() else extract_description(file_path)

    return FileEntry(
        type=dir_type,
        path=normalized_path,
        description=description
    )


def scan_directory_files(directory: Path, recursive: bool = True) -> list[Path]:
    """Scan directory recursively for files or just immediate subdirs.

    For skills and plugins: returns immediate subdirectories (shallow)
    For other types: returns all files recursively (deep)

    Args:
        directory: Directory to scan
        recursive: If True, scan recursively for files; if False, return immediate subdirs

    Returns:
        Sorted list of file or directory paths
    """
    if recursive:
        # Deep scan: find all files recursively
        return sorted(p for p in directory.rglob("*") if p.is_file())
    else:
        # Shallow scan: return only immediate subdirectories
        return sorted(p for p in directory.iterdir() if p.is_dir())


def should_scan_recursively(dir_type: str) -> bool:
    """Determine if directory type should be scanned recursively.

    Skills and plugins: shallow scan (immediate subdirs only)
    Others: recursive scan (all files)

    Args:
        dir_type: Directory type name

    Returns:
        True for recursive scan, False for shallow scan
    """
    return dir_type not in ("skills", "plugins")


def process_directory(
    directory: Path,
    repo_root: Path
) -> tuple[str, FileList]:
    """Process a directory and extract file/directory entries.

    For skills and plugins: lists only immediate subdirectories
    For other types: lists all files recursively

    Args:
        directory: Directory to process
        repo_root: Repository root path

    Returns:
        Tuple of (directory_name, list_of_entries)
    """
    dir_type = directory.name

    # Determine scan depth based on directory type
    recursive = should_scan_recursively(dir_type)
    items = scan_directory_files(directory, recursive=recursive)

    # Functional pipeline: map items to FileEntry objects, filter out None
    entries = [
        entry for item_path in items
        if (entry := create_file_entry(item_path, repo_root, dir_type)) is not None
    ]

    return dir_type, entries


def merge_file_lists(scans: Iterable[DirectoryScan]) -> FileList:
    """Merge multiple directory scans into a single file list (pure function).

    Uses reduce for functional aggregation.

    Args:
        scans: Iterable of (directory_name, file_list) tuples

    Returns:
        Merged list of all file entries
    """
    return reduce(
        lambda acc, scan: acc + scan[1],
        scans,
        []
    )


def calculate_stats(files: FileList) -> ScanStats:
    """Calculate statistics from file list (pure function).

    Args:
        files: List of file entries

    Returns:
        ScanStats with aggregated information
    """
    files_with_desc = sum(1 for f in files if f.description)

    # Count unique directory types
    dir_types = len(set(f.type for f in files))

    return ScanStats(
        total_files=len(files),
        directories_scanned=dir_types,
        files_with_descriptions=files_with_desc
    )


def files_to_dict(files: FileList) -> dict[str, list[dict[str, str]]]:
    """Convert file list to dictionary for JSON serialization (pure function).

    Args:
        files: List of FileEntry objects

    Returns:
        Dictionary with 'files' key containing list of file dictionaries
    """
    return {"files": [f.to_dict() for f in files]}


# ============================================================================
# Impure Functions - Side effects (I/O, printing)
# ============================================================================

def log_info(message: str) -> None:
    """Log an info message to stdout."""
    print(message)


def log_warning(message: str) -> None:
    """Log a warning message to stdout."""
    print(f"⚠️  Warning: {message}")


def log_scan_result(dir_name: str, count: int) -> None:
    """Log directory scan result."""
    log_info(f"✓ Added {count} files from {dir_name}/")


def log_stats(stats: ScanStats) -> None:
    """Log aggregated statistics."""
    log_info(f"\n📊 Statistics:")
    log_info(f"   Total files: {stats.total_files}")
    log_info(f"   Directories scanned: {stats.directories_scanned}")
    log_info(f"   Files with descriptions: {stats.files_with_descriptions}")
    log_info(f"   Files without descriptions: {stats.files_without_descriptions}")
    log_info(f"   Description rate: {stats.description_rate:.1f}%")


def write_json_file(output_path: Path, data: dict) -> None:
    """Write data to JSON file.

    Args:
        output_path: Path to output file
        data: Data to serialize to JSON
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def validate_config(config: Config) -> tuple[bool, str | None]:
    """Validate configuration directories exist.

    Args:
        config: Application configuration

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not config.repo_root.is_dir():
        return False, f"Repository root not found: {config.repo_root}"

    if not config.output_dir.is_dir():
        # Try to create output directory
        try:
            config.output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return False, f"Cannot create output directory: {config.output_dir} - {e}"

    return True, None


# ============================================================================
# CLI and Main Entry Point
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate stack JSON file from directory listings with metadata extraction.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --dirs agents,instructions,prompts
  %(prog)s --output stack-custom.json
  %(prog)s --repo-root /custom/path --output-dir /custom/output

Environment Variables:
  REPO_ROOT      Repository root directory
  STACK_DIRS     Comma-separated list of directories to scan (default: agents,instructions,prompts)
  STACK_OUTPUT   Output filename (default: stack.json)
  OUTPUT_DIR     Output directory path (default: script directory)
        """
    )

    parser.add_argument(
        "--dirs",
        nargs="*",
        default=None,
        help="Directories to scan (space-separated). Default: STACK_DIRS env var or 'agents instructions prompts'"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output filename. Default: STACK_OUTPUT env var or 'stack.json'"
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root directory. Default: REPO_ROOT env var or script parent"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Default: OUTPUT_DIR env var or script directory"
    )

    return parser




def main() -> int:
    """Main entry point for the script.

    Orchestrates the stack generation pipeline:
    1. Parse arguments and build configuration
    2. Validate configuration
    3. Scan directories and extract file metadata
    4. Merge results and calculate statistics
    5. Write JSON output

    Returns:
        0 on success, 1 on error
    """
    # Parse arguments and create configuration
    parser = create_parser()
    args = parser.parse_args()
    config = Config.from_args(args)

    # Display configuration
    log_info("Configuration:")
    log_info(f"  Repository root: {config.repo_root}")
    log_info(f"  Stack directories: {', '.join(config.stack_dirs)}")
    log_info(f"  Output file: {config.output_file}")
    log_info(f"  Output directory: {config.output_dir}\n")

    # Validate configuration
    is_valid, error = validate_config(config)
    if not is_valid:
        log_info(f"❌ Error: {error}")
        return 1

    # Scan directories (functional pipeline)
    scans: list[DirectoryScan] = []

    for dir_name in config.stack_dirs:
        input_dir = config.repo_root / dir_name

        if not input_dir.is_dir():
            log_warning(f"Directory not found: {input_dir}")
            continue

        # Process directory functionally
        dir_type, entries = process_directory(input_dir, config.repo_root)

        if entries:
            scans.append((dir_type, entries))
            log_scan_result(dir_name, len(entries))

    # Merge all scans into a single file list (functional reduce)
    all_files = merge_file_lists(scans)

    if not all_files:
        log_info("❌ Error: No files found in any directory")
        return 1

    # Calculate statistics
    stats = calculate_stats(all_files)
    log_stats(stats)

    # Convert to dictionary for JSON serialization
    output_data = files_to_dict(all_files)

    # Write output file
    output_path = config.output_dir / config.output_file

    try:
        write_json_file(output_path, output_data)
        log_info(f"\n✅ Successfully generated: {output_path}")
        log_info(f"   {stats.total_files} total files included")
    except OSError as e:
        log_info(f"❌ Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
