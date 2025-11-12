# uvrun

A smart Rust-based Python script runner that automatically finds and executes your Python scripts.

## What is this?

`uvrun` is a tiny Rust binary that acts as a launcher for Python scripts. It stands on the shoulders of the fantastic [uv project](https://github.com/astral-sh/uv).

**I DON'T THINK YOU UNDERSTAND HOW LIFE-CHANGING THIS IS** Let me explain: You just download the very small `uv.exe` file, put it in your PATH, and now you can run ANY PYTHON SCRIPT with ANY DEPENDENCY without installing ANYTHING! 🤯

How to download uv.exe:
```bash
wget -O uv.zip https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip && unzip uv.zip
```


And this project takes it a step further: Now you can make an .exe file that runs any python script on your path, simply by RENAMING the script!

## Why?

- **Zero configuration** -- rename the binary and you're done
- **No installation required** -- not even Python! No conda, poetry, venv, virtualenv, pipenv, or pip install needed
- **Portable bundles** -- drop `uv.exe`, `myscript.exe` (renamed uvrun), and `myscript.py` in a folder
- **No PATH pollution needed** -- everything can be self-contained
- **Windows-friendly** -- no shebang issues or file associations needed
- **Works anywhere** -- searches multiple locations automatically

## How it works

1. You rename `uvrun.exe` to match your script (e.g., `myscript.exe`)
2. When you run `myscript.exe`, it:
   - Searches for `uv.exe` in multiple locations
   - Searches for `myscript.py` or `myscript.uvpy` in the same locations
   - Executes `uv run --script myscript.py [your args]`
   - Passes through stdin, stdout, stderr, and exit codes

## Search locations

The tool searches for both `uv.exe` and the matching `.py`/`.uvpy` file in this order:

1. Current working directory (`.`)
2. `./bin` subdirectory
3. `./scripts` subdirectory
4. The directory where the binary itself is located
5. The binary's directory's `./bin` subdirectory
6. The binary's directory's `./scripts` subdirectory
7. All directories in the `PATH` environment variable

**Note:** `.uvpy` and `.py` extensions are treated equally -- whichever is found first wins.

## Usage

### Basic example

```bash
# Rename uvrun.exe to match your script
cp uvrun.exe myscript.exe

# Run it -- it finds uv.exe and myscript.py automatically
./myscript.exe arg1 arg2
```

### Portable bundle example

Create a self-contained directory:

```
myproject/
├── uv.exe
├── process_data.exe    # renamed uvrun.exe
└── process_data.py
```

Now `./process_data.exe` works anywhere without installation!

### With uv in PATH

If `uv` is in your PATH, you can place just the renamed binary and script anywhere:

```
scripts/
├── backup.exe          # renamed uvrun.exe
└── backup.py
```

## Building

```bash
cargo build --release
```

The binary will be at `target/release/uvrun.exe`.

## Requirements

- `uv` must be accessible (either nearby or in PATH)
  - Get it from the amazing [uv project](https://github.com/astral-sh/uv)
- Python scripts should use the standard `uv` inline script metadata format:

```python
#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests",
# ]
# ///

import requests
print("Hello from uv!")
```

## Use cases

- **Portable tools** -- distribute scripts with all dependencies self-contained
- **Project-specific scripts** -- keep `uv.exe` and scripts in project directories
- **Quick utilities** -- rename once, run anywhere
- **Windows scripting** -- avoid batch file wrappers and PATH issues
