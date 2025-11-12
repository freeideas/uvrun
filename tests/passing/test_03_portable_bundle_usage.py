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
    """Test portable bundle usage flow."""

    bundle_dir = None

    try:
        print("Setting up test environment...", flush=True)

        # Create a temporary bundle directory with timestamp to avoid Windows file locks
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        bundle_dir = Path(f'./tmp/test_bundle_{timestamp}')
        bundle_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created bundle directory: {bundle_dir}", flush=True)

        # Step 1: Create self-contained directory structure
        print("\n[Step 1] Creating self-contained directory structure...", flush=True)
        print("Step 1 started...", flush=True)

        # Copy uv.exe to bundle directory
        uv_source = Path('./release/uvrun.exe')
        assert uv_source.exists(), f"uvrun.exe not found at {uv_source}"

        # For testing, we need actual uv.exe
        # First check if uv is available in PATH
        uv_in_path = shutil.which('uv')
        if uv_in_path:
            uv_exe_source = Path(uv_in_path)
            print(f"Found uv.exe in PATH at: {uv_exe_source}", flush=True)
        else:
            # If not in PATH, check release directory
            uv_exe_source = Path('./release/uv.exe')
            assert uv_exe_source.exists(), f"uv.exe not found in PATH or at {uv_exe_source}"
            print(f"Found uv.exe at: {uv_exe_source}", flush=True)

        uv_exe_dest = bundle_dir / 'uv.exe'
        print(f"Copying from {uv_exe_source} to {uv_exe_dest}", flush=True)
        shutil.copy2(uv_exe_source, uv_exe_dest)
        assert uv_exe_dest.exists(), "Failed to copy uv.exe to bundle"  # $REQ_BUNDLE_001
        print(f"Copied uv.exe to bundle: {uv_exe_dest}", flush=True)

        # Copy and rename uvrun.exe to match script name
        renamed_binary = bundle_dir / 'process_data.exe'
        shutil.copy2(uv_source, renamed_binary)
        assert renamed_binary.exists(), "Failed to copy renamed binary"  # $REQ_BUNDLE_001
        print(f"Created renamed binary: {renamed_binary}", flush=True)

        # Create a matching Python script
        script_path = bundle_dir / 'process_data.py'
        script_content = '''#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os

# Print arguments received
print("Script received args:", sys.argv[1:])

# Read from stdin if available
stdin_data = sys.stdin.read().strip()
if stdin_data:
    print(f"Script received stdin: {stdin_data}")

# Write to stderr
print("Script stderr output", file=sys.stderr)

# Exit with code based on first argument
if len(sys.argv) > 1 and sys.argv[1] == "fail":
    sys.exit(42)
else:
    sys.exit(0)
'''
        script_path.write_text(script_content, encoding='utf-8')
        assert script_path.exists(), "Failed to create Python script"  # $REQ_BUNDLE_001
        print(f"Created Python script: {script_path}", flush=True)

        print("✓ Self-contained directory structure created", flush=True)  # $REQ_BUNDLE_001

        # Verify directory structure
        print("Verifying directory structure...", flush=True)
        assert (bundle_dir / 'uv.exe').exists()  # $REQ_BUNDLE_001
        assert (bundle_dir / 'process_data.exe').exists()  # $REQ_BUNDLE_001
        assert (bundle_dir / 'process_data.py').exists()  # $REQ_BUNDLE_001
        print("Directory structure verified", flush=True)

        # Step 2: Execute from bundle directory
        print("\n[Step 2] Executing from bundle directory...", flush=True)
        print("Step 2 started...", flush=True)

        # Run the renamed binary from within the bundle directory
        print(f"About to execute: {renamed_binary} with args ['arg1', 'arg2']", flush=True)
        print(f"Working directory: {bundle_dir}", flush=True)
        print("Starting subprocess.run()...", flush=True)
        result = subprocess.run(
            [str(renamed_binary), 'arg1', 'arg2'],
            cwd=str(bundle_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        print("subprocess.run() completed", flush=True)

        print(f"Process completed with exit code: {result.returncode}", flush=True)
        print(f"stdout: {result.stdout}", flush=True)
        print(f"stderr: {result.stderr}", flush=True)

        # Verify it executed successfully
        assert result.returncode == 0, f"Execution failed with code {result.returncode}"  # $REQ_BUNDLE_002
        print("✓ Binary executed from bundle directory", flush=True)  # $REQ_BUNDLE_002

        # Step 3: Verify arguments were passed through
        print("\n[Step 3] Verifying arguments passed through...", flush=True)
        assert 'arg1' in result.stdout, "arg1 not found in output"  # $REQ_BUNDLE_003
        assert 'arg2' in result.stdout, "arg2 not found in output"  # $REQ_BUNDLE_003
        print("✓ Arguments passed through correctly", flush=True)  # $REQ_BUNDLE_003

        # Step 4: Verify stdin pass-through
        print("\n[Step 4] Testing stdin pass-through...", flush=True)
        stdin_test_data = "test input data"
        print(f"About to test stdin with: {renamed_binary}", flush=True)
        print("Starting subprocess.run() with stdin...", flush=True)
        result_stdin = subprocess.run(
            [str(renamed_binary)],
            cwd=str(bundle_dir),
            input=stdin_test_data,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        print("subprocess.run() with stdin completed", flush=True)

        assert stdin_test_data in result_stdin.stdout, "stdin not passed through"  # $REQ_BUNDLE_004
        print("✓ stdin passed through correctly", flush=True)  # $REQ_BUNDLE_004

        # Step 5: Verify stdout pass-through (already verified above)
        print("\n[Step 5] Verifying stdout pass-through...", flush=True)
        assert "Script received args:" in result.stdout, "stdout not passed through"  # $REQ_BUNDLE_005
        print("✓ stdout passed through correctly", flush=True)  # $REQ_BUNDLE_005

        # Step 6: Verify stderr pass-through
        print("\n[Step 6] Verifying stderr pass-through...", flush=True)
        assert "Script stderr output" in result.stderr, "stderr not passed through"  # $REQ_BUNDLE_006
        print("✓ stderr passed through correctly", flush=True)  # $REQ_BUNDLE_006

        # Step 7: Verify exit code pass-through
        print("\n[Step 7] Testing exit code pass-through...", flush=True)
        print(f"About to test exit code with: {renamed_binary} fail", flush=True)
        print("Starting subprocess.run() with 'fail' argument...", flush=True)
        result_exit = subprocess.run(
            [str(renamed_binary), 'fail'],
            cwd=str(bundle_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        print("subprocess.run() with 'fail' argument completed", flush=True)

        assert result_exit.returncode == 42, f"Exit code not passed through, got {result_exit.returncode}"  # $REQ_BUNDLE_007
        print("✓ Exit code passed through correctly", flush=True)  # $REQ_BUNDLE_007

        # Step 8: Execute bundle from external location
        print("\n[Step 8] Testing execution from external location...", flush=True)

        # Run the binary using absolute path from a different directory
        external_cwd = Path('./tmp')
        print(f"About to test from external location: {renamed_binary.resolve()}", flush=True)
        print(f"External working directory: {external_cwd}", flush=True)
        print("Starting subprocess.run() from external location...", flush=True)
        result_external = subprocess.run(
            [str(renamed_binary.resolve()), 'external_test'],
            cwd=str(external_cwd),
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        print("subprocess.run() from external location completed", flush=True)

        assert result_external.returncode == 0, "Execution from external location failed"  # $REQ_BUNDLE_008
        assert 'external_test' in result_external.stdout, "Bundle didn't work from external location"  # $REQ_BUNDLE_008
        print("✓ Bundle works from external location", flush=True)  # $REQ_BUNDLE_008

        print("\n✓ All tests passed", flush=True)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}", flush=True)
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up bundle directory
        if bundle_dir and bundle_dir.exists():
            print(f"\nCleaning up test bundle directory: {bundle_dir}", flush=True)
            # On Windows, files may be briefly locked. Retry a few times.
            import time
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    shutil.rmtree(bundle_dir)
                    print("✓ Cleanup completed", flush=True)
                    break
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"Cleanup attempt {attempt + 1} failed, retrying... ({e})", flush=True)
                        time.sleep(0.5)
                    else:
                        print(f"Warning: Failed to clean up {bundle_dir} after {max_attempts} attempts: {e}", flush=True)

if __name__ == '__main__':
    sys.exit(main())
