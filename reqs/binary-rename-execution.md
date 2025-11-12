# Basic Usage Flow

**Source:** ./README.md

User renames uvrun.exe to match a Python script name, places the script nearby, executes the renamed binary with arguments, and receives the script's output and exit code.

## $REQ_BASIC_001: Binary Can Be Renamed

**Source:** ./README.md (Section: "How it works")

The uvrun.exe binary can be renamed to any name (e.g., myscript.exe).

## $REQ_BASIC_002: Derive Script Name from Binary Name

**Source:** ./README.md (Section: "How it works")

When the renamed binary executes, it derives the Python script name from its own executable name by replacing the .exe extension with .py or .uvpy.

## $REQ_BASIC_003: Search for uv.exe

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe across multiple locations: current working directory, ./bin subdirectory, ./scripts subdirectory, binary's directory, binary's ./bin subdirectory, binary's ./scripts subdirectory, and PATH directories.

## $REQ_BASIC_004: Search for Python Script

**Source:** ./README.md (Section: "Search locations")

The tool searches for the matching Python script (.py or .uvpy) across the same locations as uv.exe.

## $REQ_BASIC_005: Support .py Extension

**Source:** ./README.md (Section: "Search locations")

The tool searches for Python scripts with the .py extension.

## $REQ_BASIC_006: Support .uvpy Extension

**Source:** ./README.md (Section: "Search locations")

The tool searches for Python scripts with the .uvpy extension.

## $REQ_BASIC_007: Extension Priority First-Found

**Source:** ./README.md (Section: "Search locations")

When both .uvpy and .py extensions exist, whichever is found first in the search order is used.

## $REQ_BASIC_008: Execute Script via uv run

**Source:** ./README.md (Section: "How it works")

The renamed binary executes the matched Python script using the command format: `uv run --script scriptname.py [args]`.

## $REQ_BASIC_009: Forward Arguments to Script

**Source:** ./README.md (Section: "How it works")

Arguments passed to the renamed binary are forwarded to the Python script.

## $REQ_BASIC_010: Pass Through stdin

**Source:** ./README.md (Section: "How it works")

Standard input (stdin) is passed through to the Python script.

## $REQ_BASIC_011: Pass Through stdout

**Source:** ./README.md (Section: "How it works")

Standard output (stdout) from the Python script is passed through to the caller.

## $REQ_BASIC_012: Pass Through stderr

**Source:** ./README.md (Section: "How it works")

Standard error (stderr) from the Python script is passed through to the caller.

## $REQ_BASIC_013: Pass Through Exit Code

**Source:** ./README.md (Section: "How it works")

The exit code from the Python script execution is returned as the exit code of the renamed binary.

## $REQ_BASIC_014: No Configuration Files Required

**Source:** ./README.md (Section: "Why?")

The tool operates without requiring any configuration files -- renaming the binary is sufficient.
