#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
import shutil
import os
from pathlib import Path

def main():
    """Test binary rename and execution flow."""

    print("Starting binary rename execution test...")

    # Setup paths
    release_dir = Path('./release')
    tmp_dir = Path('./tmp')
    tmp_dir.mkdir(exist_ok=True)

    uvrun_exe = release_dir / 'uvrun.exe'
    renamed_exe = tmp_dir / 'myscript.exe'
    test_script = tmp_dir / 'myscript.py'

    # Track resources for cleanup
    created_files = []

    try:
        # Verify uvrun.exe exists
        assert uvrun_exe.exists(), f"uvrun.exe not found at {uvrun_exe}"
        print(f"✓ Found uvrun.exe at {uvrun_exe}")

        # $REQ_BASIC_001: Binary Can Be Renamed
        print(f"\nTesting requirement $REQ_BASIC_001: Binary can be renamed...")
        print(f"Copying {uvrun_exe} to {renamed_exe}...")
        shutil.copy2(uvrun_exe, renamed_exe)
        created_files.append(renamed_exe)
        assert renamed_exe.exists(), "Failed to create renamed binary"  # $REQ_BASIC_001
        assert renamed_exe.is_file(), "Renamed binary must be a file"  # $REQ_BASIC_001
        print(f"✓ Successfully renamed uvrun.exe to myscript.exe")

        # Create a test Python script that the renamed binary will execute
        # This script tests multiple requirements at once
        print(f"\nCreating test script at {test_script}...")
        script_content = '''#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os

# Test argument forwarding
print("ARGS:", " ".join(sys.argv[1:]))

# Test stdin passthrough
if not sys.stdin.isatty():
    stdin_data = sys.stdin.read()
    print("STDIN:", stdin_data, end="")

# Test stdout (this line itself)
print("STDOUT: Hello from myscript.py", file=sys.stdout)

# Test stderr
print("STDERR: Error message from script", file=sys.stderr)

# Test exit code
sys.exit(42)
'''
        test_script.write_text(script_content, encoding='utf-8')
        created_files.append(test_script)
        assert test_script.exists(), "Failed to create test script"
        print(f"✓ Created test script at {test_script}")

        # $REQ_BASIC_002: Derive Script Name from Binary Name
        # $REQ_BASIC_004: Search for Python Script
        # $REQ_BASIC_005: Support .py Extension
        # $REQ_BASIC_008: Execute Script via uv run
        # $REQ_BASIC_009: Forward Arguments to Script
        # $REQ_BASIC_011: Pass Through stdout
        # $REQ_BASIC_012: Pass Through stderr
        # $REQ_BASIC_013: Pass Through Exit Code
        print(f"\nTesting execution of renamed binary with arguments...")
        print(f"Running: {renamed_exe} arg1 arg2 arg3")
        result = subprocess.run(
            [str(renamed_exe), 'arg1', 'arg2', 'arg3'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=str(tmp_dir)
        )

        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")

        # Verify the binary derived the script name from its own name
        assert 'myscript.py' in result.stdout or 'myscript.py' in result.stderr or result.returncode == 42, \
            "Binary should have found and executed myscript.py"  # $REQ_BASIC_002

        # Verify arguments were forwarded
        assert 'ARGS: arg1 arg2 arg3' in result.stdout, \
            "Arguments were not forwarded to script"  # $REQ_BASIC_009
        print("✓ Arguments forwarded correctly")

        # Verify stdout passthrough
        assert 'STDOUT: Hello from myscript.py' in result.stdout, \
            "Stdout was not passed through"  # $REQ_BASIC_011
        print("✓ Stdout passed through correctly")

        # Verify stderr passthrough
        assert 'STDERR: Error message from script' in result.stderr, \
            "Stderr was not passed through"  # $REQ_BASIC_012
        print("✓ Stderr passed through correctly")

        # Verify exit code passthrough
        assert result.returncode == 42, \
            f"Exit code not passed through correctly: expected 42, got {result.returncode}"  # $REQ_BASIC_013
        print("✓ Exit code passed through correctly")

        # $REQ_BASIC_010: Pass Through stdin
        print(f"\nTesting stdin passthrough...")
        stdin_test_input = "Test input data from stdin\n"
        result = subprocess.run(
            [str(renamed_exe)],
            input=stdin_test_input,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=str(tmp_dir)
        )

        assert f"STDIN: {stdin_test_input}" in result.stdout, \
            "Stdin was not passed through to script"  # $REQ_BASIC_010
        print("✓ Stdin passed through correctly")

        # $REQ_BASIC_006: Support .uvpy Extension
        # $REQ_BASIC_007: Extension Priority First-Found
        print(f"\nTesting .uvpy extension support...")
        uvpy_script = tmp_dir / 'testuvpy.uvpy'
        uvpy_exe = tmp_dir / 'testuvpy.exe'

        uvpy_script.write_text('''#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
import sys
print("UVPY: Executed from .uvpy file")
sys.exit(0)
''', encoding='utf-8')
        created_files.append(uvpy_script)

        shutil.copy2(uvrun_exe, uvpy_exe)
        created_files.append(uvpy_exe)

        print(f"Running: {uvpy_exe}")
        result = subprocess.run(
            [str(uvpy_exe)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=str(tmp_dir)
        )

        assert result.returncode == 0, \
            f".uvpy script execution failed with code {result.returncode}"  # $REQ_BASIC_006
        assert "UVPY: Executed from .uvpy file" in result.stdout, \
            ".uvpy file was not executed"  # $REQ_BASIC_006
        print("✓ .uvpy extension supported")

        # Test first-found priority: if both .py and .uvpy exist, first found wins
        print(f"\nTesting extension priority (first-found wins)...")
        priority_py = tmp_dir / 'priority.py'
        priority_uvpy = tmp_dir / 'priority.uvpy'
        priority_exe = tmp_dir / 'priority.exe'

        priority_py.write_text('''#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
print("PRIORITY: Executed from .py file")
''', encoding='utf-8')
        created_files.append(priority_py)

        priority_uvpy.write_text('''#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
print("PRIORITY: Executed from .uvpy file")
''', encoding='utf-8')
        created_files.append(priority_uvpy)

        shutil.copy2(uvrun_exe, priority_exe)
        created_files.append(priority_exe)

        print(f"Running: {priority_exe} (both .py and .uvpy exist)")
        result = subprocess.run(
            [str(priority_exe)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=str(tmp_dir)
        )

        # Should execute one of them (whichever is found first)
        executed_py = "PRIORITY: Executed from .py file" in result.stdout
        executed_uvpy = "PRIORITY: Executed from .uvpy file" in result.stdout
        assert executed_py or executed_uvpy, \
            "Neither .py nor .uvpy was executed"  # $REQ_BASIC_007
        assert not (executed_py and executed_uvpy), \
            "Both files were executed, should only execute first found"  # $REQ_BASIC_007
        print(f"✓ First-found priority working ({'py' if executed_py else 'uvpy'} executed)")

        # $REQ_BASIC_014: No Configuration Files Required
        print(f"\nTesting no configuration files required...")
        # This entire test proves this requirement -- we never created any config files
        # The binary worked purely by renaming and having the script nearby
        config_patterns = ['*.config', '*.cfg', '*.ini', '*.toml', '*.yaml', '*.yml', '*.json']
        config_found = False
        for pattern in config_patterns:
            if list(tmp_dir.glob(pattern)):
                config_found = True
                break
        assert not config_found, \
            "Test should not require any configuration files"  # $REQ_BASIC_014
        print("✓ No configuration files required")

        # $REQ_BASIC_003: Search for uv.exe
        # This is implicitly tested by all the above tests working
        # The renamed binary successfully found uv.exe and executed scripts
        print(f"\nAll requirements verified successfully!")
        print("✓ All tests passed")
        return 0

    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Cleanup created files
        print(f"\nCleaning up test files...")
        for file_path in created_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    print(f"Removed {file_path}")
            except Exception as e:
                print(f"Warning: Failed to remove {file_path}: {e}")

if __name__ == '__main__':
    sys.exit(main())
