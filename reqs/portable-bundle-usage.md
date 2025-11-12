# Portable Bundle Usage Flow

**Source:** ./README.md

User creates a self-contained directory with uv.exe, renamed binary, and Python script, executes it with arguments, and receives the script's output and exit code.

## $REQ_BUNDLE_001: Self-Contained Directory Structure

**Source:** ./README.md (Section: "Portable bundle example")

User can create a directory containing uv.exe, a renamed copy of uvrun.exe, and a matching Python script.

## $REQ_BUNDLE_002: Execute from Bundle Directory

**Source:** ./README.md (Section: "Portable bundle example")

When the renamed binary is executed from within the bundle directory, it finds uv.exe and the matching Python script in the same directory and executes the script.

## $REQ_BUNDLE_003: Pass Arguments to Script

**Source:** ./README.md (Section: "Basic example")

Arguments passed to the renamed binary are forwarded to the Python script being executed.

## $REQ_BUNDLE_004: Pass Through stdin

**Source:** ./README.md (Section: "How it works")

Standard input (stdin) is passed through to the Python script.

## $REQ_BUNDLE_005: Pass Through stdout

**Source:** ./README.md (Section: "How it works")

Standard output (stdout) from the Python script is passed through to the caller.

## $REQ_BUNDLE_006: Pass Through stderr

**Source:** ./README.md (Section: "How it works")

Standard error (stderr) from the Python script is passed through to the caller.

## $REQ_BUNDLE_007: Pass Through Exit Code

**Source:** ./README.md (Section: "How it works")

The exit code from the Python script execution is returned as the exit code of the renamed binary.

## $REQ_BUNDLE_008: Execute Bundle from External Location

**Source:** ./README.md (Section: "Portable bundle example")

The portable bundle directory works from any location without requiring installation or PATH configuration.
