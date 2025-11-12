#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import subprocess
import shutil
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    # Get project root (parent of tests directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    code_dir = project_root / "code"
    release_dir = project_root / "release"

    print(f"Building uvrun from {code_dir}")

    # Create release directory if it doesn't exist
    release_dir.mkdir(exist_ok=True)

    # Delete any existing artifacts that we will recreate
    uvrun_exe = release_dir / "uvrun.exe"
    if uvrun_exe.exists():
        print(f"Removing existing artifact: {uvrun_exe}")
        uvrun_exe.unlink()

    # Build the Rust project using cargo
    print("Running cargo build --release...")
    try:
        result = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=code_dir,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code {e.returncode}", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("Error: cargo not found. Please install Rust toolchain.", file=sys.stderr)
        return 1

    # Copy the built binary to release directory
    built_exe = code_dir / "target" / "release" / "uvrun.exe"
    if not built_exe.exists():
        print(f"Error: Built binary not found at {built_exe}", file=sys.stderr)
        return 1

    print(f"Copying {built_exe} to {uvrun_exe}")
    shutil.copy2(built_exe, uvrun_exe)

    # Verify the artifact exists
    if not uvrun_exe.exists():
        print(f"Error: Failed to copy binary to {uvrun_exe}", file=sys.stderr)
        return 1

    file_size = uvrun_exe.stat().st_size
    print(f"\nBuild successful!")
    print(f"Artifact created: {uvrun_exe} ({file_size:,} bytes)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
