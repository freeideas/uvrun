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

import os
import shutil
import subprocess
from pathlib import Path
import tempfile

def main():
    """Test search location resolution for uv.exe and Python scripts."""

    original_cwd = os.getcwd()
    temp_test_dir = None

    try:
        # Create a temporary directory structure for testing
        temp_test_dir = tempfile.mkdtemp(prefix='uvrun_test_')
        print(f"Created test directory: {temp_test_dir}")

        # Paths we'll need
        release_dir = Path(original_cwd) / 'release'
        uvrun_exe = release_dir / 'uvrun.exe'

        # Verify uvrun.exe exists
        assert uvrun_exe.exists(), f"uvrun.exe not found at {uvrun_exe}"
        print(f"✓ Found uvrun.exe at {uvrun_exe}")

        # Create a simple test Python script
        test_script_content = """#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

print("TEST_SCRIPT_SUCCESS")
sys.exit(0)
"""

        # Find uv.exe in PATH (we need it for the tests)
        uv_in_path = shutil.which('uv')
        if not uv_in_path:
            print("⚠ WARNING: uv.exe not found in PATH, trying to find it...")
            # Try to find uv.exe in common locations
            possible_uv_locations = [
                Path(original_cwd) / 'uv.exe',
                Path.home() / '.cargo' / 'bin' / 'uv.exe',
            ]
            for loc in possible_uv_locations:
                if loc.exists():
                    uv_in_path = str(loc)
                    print(f"✓ Found uv.exe at {uv_in_path}")
                    break

            if not uv_in_path:
                print("✗ ERROR: Could not find uv.exe anywhere")
                return 1
        else:
            print(f"✓ Found uv.exe in PATH: {uv_in_path}")

        # Test $REQ_SEARCH_001: Search current working directory
        print("\n--- Testing $REQ_SEARCH_001: Current working directory ---")
        test_cwd = Path(temp_test_dir) / 'test_cwd'
        test_cwd.mkdir(parents=True)

        # Copy uv.exe and create testscript.py in current working directory
        shutil.copy(uv_in_path, test_cwd / 'uv.exe')
        (test_cwd / 'testscript.py').write_text(test_script_content, encoding='utf-8')

        # Copy and rename uvrun.exe to testscript.exe
        shutil.copy(uvrun_exe, test_cwd / 'testscript.exe')

        # Change to test directory and run
        os.chdir(test_cwd)
        print(f"Changed to directory: {test_cwd}")
        print(f"Running: ./testscript.exe")

        result = subprocess.run(
            ['./testscript.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"testscript.exe failed with code {result.returncode}"  # $REQ_SEARCH_001
        assert "TEST_SCRIPT_SUCCESS" in result.stdout, "Expected output not found"  # $REQ_SEARCH_001
        print("✓ $REQ_SEARCH_001: Current working directory search works")

        # Test $REQ_SEARCH_002: Search ./bin subdirectory of CWD
        print("\n--- Testing $REQ_SEARCH_002: ./bin subdirectory of CWD ---")
        test_bin = Path(temp_test_dir) / 'test_bin'
        test_bin.mkdir(parents=True)
        bin_dir = test_bin / 'bin'
        bin_dir.mkdir()

        # Put uv.exe and script in ./bin subdirectory
        shutil.copy(uv_in_path, bin_dir / 'uv.exe')
        (bin_dir / 'binscript.py').write_text(test_script_content, encoding='utf-8')

        # Put renamed uvrun.exe in current directory
        shutil.copy(uvrun_exe, test_bin / 'binscript.exe')

        os.chdir(test_bin)
        print(f"Changed to directory: {test_bin}")
        print(f"Running: ./binscript.exe (should find ./bin/binscript.py)")

        result = subprocess.run(
            ['./binscript.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"binscript.exe failed with code {result.returncode}"  # $REQ_SEARCH_002
        assert "TEST_SCRIPT_SUCCESS" in result.stdout, "Expected output not found"  # $REQ_SEARCH_002
        print("✓ $REQ_SEARCH_002: ./bin subdirectory search works")

        # Test $REQ_SEARCH_003: Search ./scripts subdirectory of CWD
        print("\n--- Testing $REQ_SEARCH_003: ./scripts subdirectory of CWD ---")
        test_scripts = Path(temp_test_dir) / 'test_scripts'
        test_scripts.mkdir(parents=True)
        scripts_dir = test_scripts / 'scripts'
        scripts_dir.mkdir()

        # Put uv.exe and script in ./scripts subdirectory
        shutil.copy(uv_in_path, scripts_dir / 'uv.exe')
        (scripts_dir / 'scriptscript.py').write_text(test_script_content, encoding='utf-8')

        # Put renamed uvrun.exe in current directory
        shutil.copy(uvrun_exe, test_scripts / 'scriptscript.exe')

        os.chdir(test_scripts)
        print(f"Changed to directory: {test_scripts}")
        print(f"Running: ./scriptscript.exe (should find ./scripts/scriptscript.py)")

        result = subprocess.run(
            ['./scriptscript.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"scriptscript.exe failed with code {result.returncode}"  # $REQ_SEARCH_003
        assert "TEST_SCRIPT_SUCCESS" in result.stdout, "Expected output not found"  # $REQ_SEARCH_003
        print("✓ $REQ_SEARCH_003: ./scripts subdirectory search works")

        # Test $REQ_SEARCH_004: Search binary location directory
        print("\n--- Testing $REQ_SEARCH_004: Binary location directory ---")
        test_binary_dir = Path(temp_test_dir) / 'test_binary_dir'
        test_binary_dir.mkdir(parents=True)

        # Put uv.exe, script, AND the binary in the same directory
        shutil.copy(uv_in_path, test_binary_dir / 'uv.exe')
        (test_binary_dir / 'binloc.py').write_text(test_script_content, encoding='utf-8')
        shutil.copy(uvrun_exe, test_binary_dir / 'binloc.exe')

        # Run from a DIFFERENT directory (so CWD searches fail)
        os.chdir(temp_test_dir)
        print(f"Changed to directory: {temp_test_dir}")
        print(f"Running: {test_binary_dir}/binloc.exe (should find files next to binary)")

        result = subprocess.run(
            [str(test_binary_dir / 'binloc.exe')],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"binloc.exe failed with code {result.returncode}"  # $REQ_SEARCH_004
        assert "TEST_SCRIPT_SUCCESS" in result.stdout, "Expected output not found"  # $REQ_SEARCH_004
        print("✓ $REQ_SEARCH_004: Binary location directory search works")

        # Test $REQ_SEARCH_005: Search binary's ./bin subdirectory
        print("\n--- Testing $REQ_SEARCH_005: Binary's ./bin subdirectory ---")
        test_binary_bin = Path(temp_test_dir) / 'test_binary_bin'
        test_binary_bin.mkdir(parents=True)
        binary_bin_dir = test_binary_bin / 'bin'
        binary_bin_dir.mkdir()

        # Put uv.exe and script in binary's ./bin subdirectory
        shutil.copy(uv_in_path, binary_bin_dir / 'uv.exe')
        (binary_bin_dir / 'binbin.py').write_text(test_script_content, encoding='utf-8')

        # Put binary in parent directory
        shutil.copy(uvrun_exe, test_binary_bin / 'binbin.exe')

        # Run from a different directory
        os.chdir(temp_test_dir)
        print(f"Changed to directory: {temp_test_dir}")
        print(f"Running: {test_binary_bin}/binbin.exe (should find ./bin/binbin.py relative to binary)")

        result = subprocess.run(
            [str(test_binary_bin / 'binbin.exe')],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"binbin.exe failed with code {result.returncode}"  # $REQ_SEARCH_005
        assert "TEST_SCRIPT_SUCCESS" in result.stdout, "Expected output not found"  # $REQ_SEARCH_005
        print("✓ $REQ_SEARCH_005: Binary's ./bin subdirectory search works")

        # Test $REQ_SEARCH_006: Search binary's ./scripts subdirectory
        print("\n--- Testing $REQ_SEARCH_006: Binary's ./scripts subdirectory ---")
        test_binary_scripts = Path(temp_test_dir) / 'test_binary_scripts'
        test_binary_scripts.mkdir(parents=True)
        binary_scripts_dir = test_binary_scripts / 'scripts'
        binary_scripts_dir.mkdir()

        # Put uv.exe and script in binary's ./scripts subdirectory
        shutil.copy(uv_in_path, binary_scripts_dir / 'uv.exe')
        (binary_scripts_dir / 'binscripts.py').write_text(test_script_content, encoding='utf-8')

        # Put binary in parent directory
        shutil.copy(uvrun_exe, test_binary_scripts / 'binscripts.exe')

        # Run from a different directory
        os.chdir(temp_test_dir)
        print(f"Changed to directory: {temp_test_dir}")
        print(f"Running: {test_binary_scripts}/binscripts.exe (should find ./scripts/binscripts.py relative to binary)")

        result = subprocess.run(
            [str(test_binary_scripts / 'binscripts.exe')],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"binscripts.exe failed with code {result.returncode}"  # $REQ_SEARCH_006
        assert "TEST_SCRIPT_SUCCESS" in result.stdout, "Expected output not found"  # $REQ_SEARCH_006
        print("✓ $REQ_SEARCH_006: Binary's ./scripts subdirectory search works")

        # Test $REQ_SEARCH_007: Search PATH directories
        print("\n--- Testing $REQ_SEARCH_007: PATH directories ---")
        # This is already implicitly tested -- uv.exe is in PATH
        # We'll create a more explicit test by putting a script in PATH
        test_path = Path(temp_test_dir) / 'test_path'
        test_path.mkdir(parents=True)

        # Create a directory to add to PATH
        path_dir = Path(temp_test_dir) / 'path_test_dir'
        path_dir.mkdir(parents=True)

        # Put script in PATH directory (uv.exe is already in PATH)
        (path_dir / 'pathscript.py').write_text(test_script_content, encoding='utf-8')

        # Put binary somewhere else
        shutil.copy(uvrun_exe, test_path / 'pathscript.exe')

        # Modify PATH to include our test directory
        original_path = os.environ.get('PATH', '')
        os.environ['PATH'] = str(path_dir) + os.pathsep + original_path

        os.chdir(test_path)
        print(f"Changed to directory: {test_path}")
        print(f"Added {path_dir} to PATH")
        print(f"Running: ./pathscript.exe (should find pathscript.py in PATH)")

        result = subprocess.run(
            ['./pathscript.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Restore PATH
        os.environ['PATH'] = original_path

        assert result.returncode == 0, f"pathscript.exe failed with code {result.returncode}"  # $REQ_SEARCH_007
        assert "TEST_SCRIPT_SUCCESS" in result.stdout, "Expected output not found"  # $REQ_SEARCH_007
        print("✓ $REQ_SEARCH_007: PATH directory search works")

        # Test $REQ_SEARCH_008: Search order priority
        print("\n--- Testing $REQ_SEARCH_008: Search order priority ---")
        test_priority = Path(temp_test_dir) / 'test_priority'
        test_priority.mkdir(parents=True)

        # Create multiple locations with scripts
        # CWD should win over ./bin
        priority_bin = test_priority / 'bin'
        priority_bin.mkdir()

        # Different script content for each location
        cwd_script = """#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
print("CWD_SCRIPT")
"""

        bin_script = """#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
print("BIN_SCRIPT")
"""

        # Put uv.exe in both locations
        shutil.copy(uv_in_path, test_priority / 'uv.exe')
        shutil.copy(uv_in_path, priority_bin / 'uv.exe')

        # Put different scripts in CWD and ./bin
        (test_priority / 'priority.py').write_text(cwd_script, encoding='utf-8')
        (priority_bin / 'priority.py').write_text(bin_script, encoding='utf-8')

        # Put binary in CWD
        shutil.copy(uvrun_exe, test_priority / 'priority.exe')

        os.chdir(test_priority)
        print(f"Changed to directory: {test_priority}")
        print(f"Running: ./priority.exe (should use CWD script, not ./bin script)")

        result = subprocess.run(
            ['./priority.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        assert result.returncode == 0, f"priority.exe failed with code {result.returncode}"  # $REQ_SEARCH_008
        assert "CWD_SCRIPT" in result.stdout, "Expected CWD script to be used (priority order)"  # $REQ_SEARCH_008
        assert "BIN_SCRIPT" not in result.stdout, "Unexpected ./bin script used (wrong priority)"  # $REQ_SEARCH_008
        print("✓ $REQ_SEARCH_008: Search order priority is correct (CWD before ./bin)")

        # Test $REQ_SEARCH_009: Use first found match
        print("\n--- Testing $REQ_SEARCH_009: Use first found match ---")
        # Already implicitly tested by $REQ_SEARCH_008
        # The priority test proves first match is used
        print("✓ $REQ_SEARCH_009: First found match is used (validated by priority test)")

        # Test $REQ_SEARCH_010: Find both uv.exe and script
        print("\n--- Testing $REQ_SEARCH_010: Find both uv.exe and script ---")
        test_both = Path(temp_test_dir) / 'test_both'
        test_both.mkdir(parents=True)

        # Only put the script, no uv.exe (should fail)
        (test_both / 'bothtest.py').write_text(test_script_content, encoding='utf-8')
        shutil.copy(uvrun_exe, test_both / 'bothtest.exe')

        # Remove uv from PATH temporarily to ensure failure
        os.environ['PATH'] = ''

        os.chdir(test_both)
        print(f"Changed to directory: {test_both}")
        print(f"Running: ./bothtest.exe (should fail -- no uv.exe available)")

        result = subprocess.run(
            ['./bothtest.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Restore PATH
        os.environ['PATH'] = original_path

        assert result.returncode != 0, "Should have failed without uv.exe"  # $REQ_SEARCH_010
        print("✓ $REQ_SEARCH_010: Both uv.exe and script are required")

        print("\n✓ All tests passed")
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1

    finally:
        # Cleanup
        os.chdir(original_cwd)
        if temp_test_dir and Path(temp_test_dir).exists():
            print(f"\nCleaning up test directory: {temp_test_dir}")
            shutil.rmtree(temp_test_dir, ignore_errors=True)

if __name__ == '__main__':
    sys.exit(main())
