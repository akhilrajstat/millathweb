"""
scripts/package_project.py
==========================
Deployment packaging script for Millath College ERP.
Creates a clean, production-ready release ZIP archive strictly excluding
temporary data, dev SQLite databases, virtual environments, .env secrets,
compiled pyc files, collected staticfiles, and local media uploads.

Usage:
    python scripts/package_project.py [output_filename.zip]
"""

import os
import sys
import zipfile
from pathlib import Path

# Directories and file patterns that MUST NEVER be packaged for deployment
EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "ENV",
    "staticfiles",
    "media",
    ".git",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".mypy_cache",
    "htmlcov",
    "dist",
    "build",
}

EXCLUDED_FILE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".sqlite3",
    ".db",
    ".swp",
    ".swo",
    ".zip",
    ".tar.gz",
}

EXCLUDED_EXACT_FILENAMES = {
    ".env",
    "db.sqlite3",
    "db.sqlite3-journal",
    ".DS_Store",
    "Thumbs.db",
}


def should_exclude(rel_path: Path) -> bool:
    """Check if a given relative path should be excluded from the package."""
    # Check directory components
    for part in rel_path.parts[:-1]:
        if part in EXCLUDED_DIR_NAMES:
            return True

    filename = rel_path.name
    # Check exact excluded filenames
    if filename in EXCLUDED_EXACT_FILENAMES:
        return True

    # Check directory name if it's a folder
    if filename in EXCLUDED_DIR_NAMES:
        return True

    # Check file extensions
    ext = os.path.splitext(filename)[1].lower()
    if ext in EXCLUDED_FILE_EXTENSIONS:
        return True

    # Check hidden .env variants (allow .env.example)
    if filename.startswith(".env") and filename != ".env.example":
        return True

    return False


def build_package(output_zip: str = "millath_erp_release.zip") -> None:
    root_dir = Path(__file__).resolve().parent.parent
    output_path = root_dir / output_zip

    print(f"[INFO] Packaging project from: {root_dir}")
    print(f"[INFO] Output archive: {output_path}")

    included_count = 0
    excluded_count = 0

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for foldername, subfolders, filenames in os.walk(root_dir):
            current_folder = Path(foldername)
            # Prune excluded directories in-place so os.walk doesn't traverse them
            subfolders[:] = [d for d in subfolders if d not in EXCLUDED_DIR_NAMES]

            for filename in filenames:
                full_path = current_folder / filename
                rel_path = full_path.relative_to(root_dir)

                # Skip the output zip itself
                if full_path == output_path:
                    continue

                if should_exclude(rel_path):
                    excluded_count += 1
                    continue

                zip_file.write(full_path, arcname=str(rel_path))
                included_count += 1

    print(f"[OK] Build archive created successfully!")
    print(f"     Files included: {included_count}")
    print(f"     Files excluded (hygiene enforcement): {excluded_count}")
    print(f"     Archive size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    output_name = sys.argv[1] if len(sys.argv) > 1 else "millath_erp_release.zip"
    build_package(output_name)
