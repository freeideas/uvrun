use std::env;
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode};

fn main() -> ExitCode {
    // Get the name of this executable (without .exe extension)
    let exe_path = env::current_exe().unwrap_or_else(|e| {
        eprintln!("Error: Cannot determine executable path: {}", e);
        std::process::exit(1);
    });

    let exe_name = exe_path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or_else(|| {
            eprintln!("Error: Cannot determine executable name");
            std::process::exit(1);
        });

    // Get the directory where this executable is located
    let exe_dir = exe_path.parent().unwrap_or_else(|| Path::new("."));

    // Get current working directory
    let cwd = env::current_dir().unwrap_or_else(|_| PathBuf::from("."));

    // Search locations for uv.exe and the script
    let search_paths = vec![
        cwd.clone(),                          // Current working directory
        cwd.join("bin"),                      // ./bin
        cwd.join("scripts"),                  // ./scripts
        exe_dir.to_path_buf(),               // Executable's directory
        exe_dir.join("bin"),                 // Executable's directory/bin
        exe_dir.join("scripts"),             // Executable's directory/scripts
    ];

    // Add PATH directories
    let mut all_search_paths = search_paths.clone();
    if let Ok(path_var) = env::var("PATH") {
        for path_str in env::split_paths(&path_var) {
            all_search_paths.push(path_str);
        }
    }

    // $REQ_BUNDLE_001: Find uv.exe in self-contained directory
    // $REQ_BUNDLE_002: Find script in bundle directory
    let uv_exe = find_file(&all_search_paths, "uv.exe").unwrap_or_else(|| {
        eprintln!("Error: Cannot find uv.exe in any search location");
        eprintln!("Searched in:");
        for path in &all_search_paths {
            eprintln!("  - {}", path.display());
        }
        std::process::exit(1);
    });

    // Find the matching script (.uvpy or .py)
    let script_name_uvpy = format!("{}.uvpy", exe_name);
    let script_name_py = format!("{}.py", exe_name);

    let script_path = find_file(&all_search_paths, &script_name_uvpy)
        .or_else(|| find_file(&all_search_paths, &script_name_py))
        .unwrap_or_else(|| {
            eprintln!("Error: Cannot find {} or {} in any search location", script_name_uvpy, script_name_py);
            eprintln!("Searched in:");
            for path in &all_search_paths {
                eprintln!("  - {}", path.display());
            }
            std::process::exit(1);
        });

    // $REQ_BUNDLE_003: Get command line arguments to pass through
    let args: Vec<String> = env::args().skip(1).collect();

    // $REQ_BUNDLE_002: Build the command: uv run --script <script> [args...]
    let mut cmd = Command::new(uv_exe);
    cmd.arg("run")
       .arg("--script")
       .arg(&script_path)
       .args(&args);

    // $REQ_BUNDLE_004: Pass through stdin
    // $REQ_BUNDLE_005: Pass through stdout
    // $REQ_BUNDLE_006: Pass through stderr
    // Inherit stdin, stdout, and stderr from parent process
    cmd.stdin(std::process::Stdio::inherit())
       .stdout(std::process::Stdio::inherit())
       .stderr(std::process::Stdio::inherit());

    // $REQ_BUNDLE_007: Pass through exit code
    // Execute the command and pass through everything
    match cmd.status() {
        Ok(status) => {
            if let Some(code) = status.code() {
                ExitCode::from(code as u8)
            } else {
                // Process was terminated by a signal
                ExitCode::FAILURE
            }
        }
        Err(e) => {
            eprintln!("Error executing uv: {}", e);
            ExitCode::FAILURE
        }
    }
}

/// Search for a file in the given paths
fn find_file(paths: &[PathBuf], filename: &str) -> Option<PathBuf> {
    for path in paths {
        let file_path = path.join(filename);
        if file_path.exists() && file_path.is_file() {
            return Some(file_path);
        }
    }
    None
}
