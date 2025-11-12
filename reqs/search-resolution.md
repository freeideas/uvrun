# Search Location Resolution Flow

**Source:** ./README.md

The tool searches for both uv.exe and the matching Python script across multiple locations in a specific order.

## $REQ_SEARCH_001: Search Current Working Directory

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe and the Python script in the current working directory (`.`).

## $REQ_SEARCH_002: Search ./bin Subdirectory of CWD

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe and the Python script in the `./bin` subdirectory of the current working directory.

## $REQ_SEARCH_003: Search ./scripts Subdirectory of CWD

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe and the Python script in the `./scripts` subdirectory of the current working directory.

## $REQ_SEARCH_004: Search Binary Location Directory

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe and the Python script in the directory where the binary itself is located.

## $REQ_SEARCH_005: Search Binary's ./bin Subdirectory

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe and the Python script in the `./bin` subdirectory of the directory where the binary is located.

## $REQ_SEARCH_006: Search Binary's ./scripts Subdirectory

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe and the Python script in the `./scripts` subdirectory of the directory where the binary is located.

## $REQ_SEARCH_007: Search PATH Directories

**Source:** ./README.md (Section: "Search locations")

The tool searches for uv.exe and the Python script in all directories listed in the PATH environment variable.

## $REQ_SEARCH_008: Search Order Priority

**Source:** ./README.md (Section: "Search locations")

The search locations are checked in this order: (1) current working directory, (2) ./bin of CWD, (3) ./scripts of CWD, (4) binary's directory, (5) binary's ./bin, (6) binary's ./scripts, (7) PATH directories.

## $REQ_SEARCH_009: Use First Found Match

**Source:** ./README.md (Section: "Search locations")

The first matching file found in the search order is used for execution.

## $REQ_SEARCH_010: Find Both uv.exe and Script

**Source:** ./README.md (Section: "Search locations")

The tool must successfully locate both uv.exe and the matching Python script file to execute.
