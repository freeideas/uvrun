#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Build Artifacts Validation Test

IMPORTANT: Before modifying this test, read:
- ./README.md
- ./tests/build.py

This test validates that ./tests/build.py produces exactly
the artifacts specified in the documentation.

If this test fails, the problem is likely in ./tests/build.py
-- it's not building what the documentation specifies.
The documentation is the source of truth.

To regenerate this test (if documentation changes):
  Run: ./the-system/scripts/software-construction.py
  (This will regenerate the test based on current documentation)
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
from pathlib import Path

def main():
    release_dir = Path('./release')

    # List what's actually in ./release/
    actual_files = set()
    if release_dir.exists():
        for item in release_dir.iterdir():
            if item.is_file():
                actual_files.add(item.name)

    # Define expected files based on documentation
    # From README.md: "uvrun is a tiny Rust binary"
    # From tests/build.py: Creates only uvrun.exe in ./release/
    expected_files = {
        'uvrun.exe',
    }

    # Check for missing files
    missing = expected_files - actual_files
    if missing:
        print(f"ERROR: Missing files in ./release/:")
        for f in sorted(missing):
            print(f"  - {f}")
        print()
        print("Expected files are documented in:")
        print("  - ./README.md (describes uvrun as 'a tiny Rust binary')")
        print("  - ./tests/build.py (shows what the build creates)")
        return 1

    # Check for unexpected files
    unexpected = actual_files - expected_files
    if unexpected:
        print(f"ERROR: Unexpected files in ./release/:")
        for f in sorted(unexpected):
            print(f"  - {f}")
        print()
        print("Only uvrun.exe should be in ./release/ according to:")
        print("  - ./README.md (single binary design)")
        print("  - ./tests/build.py (only copies uvrun.exe)")
        return 1

    print("✓ Build artifacts validation: PASS")
    print(f"  Found expected file: uvrun.exe")
    return 0

if __name__ == '__main__':
    sys.exit(main())
