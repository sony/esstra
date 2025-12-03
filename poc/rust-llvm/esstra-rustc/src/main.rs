//! rustc-esstra manipulates command-line arguments and call standard rustc because interacting
//! private API (`rustc_private`) causes memory error at the last phase of runtime.
//!
//! ESSTRA LLVM Plugin works with standard rustc, but it requires to set some complex value to
//! environment variable, or command-line arguments. So we implement this for ease of using ESSTRA
//!
//! Also, rustc-esstra collects building package data from command-line arguments passed to
//! them, and writes those data into JSON file.
//! ESSTRA LLVM Plugin reads these JSON files and knows the packages which is used to compile.

use esstra_lib::deps_file::EsstraDepsData;
use file_lock::{FileLock, FileOptions};
use nix::unistd::execvp;
use std::env;
use std::ffi::CString;
use std::fs;
use std::io::Write;
use std::path::PathBuf;

fn main() {
    let mut plugin_path = env::var("ESSTRA_LLVM_PLUGIN_PATH").ok();

    let mut crates = Vec::new();
    let mut out_dir = None;

    let mut args = Vec::new();
    let mut iter = env::args();
    while let Some(arg) = iter.next() {
        // get ESSTRA LLVM Plugin path and remove it from args to pass to rustc
        match parse_arg(&arg, "--esstra-plugin-path") {
            ArgParseResult::Specified(parsed) => {
                plugin_path = Some(parsed);
            }
            ArgParseResult::ReadNext => {
                plugin_path = Some(iter.next().expect("Expected ESSTRA plugin path"));
            }
            ArgParseResult::None => {
                args.push(arg.clone());

                // check extern arg to get dependent crate
                let mut extern_crate = None;
                match parse_arg(&arg, "--extern") {
                    ArgParseResult::Specified(krate) => {
                        extern_crate = Some(krate);
                    }
                    ArgParseResult::ReadNext => {
                        let krate = iter.next().expect("Expected crate");
                        args.push(krate.clone());
                        extern_crate = Some(krate);
                    }
                    ArgParseResult::None => {}
                }
                if let Some(krate) = extern_crate {
                    crates.push(krate);
                }

                // get output dir to write dependencies record file
                match parse_arg(&arg, "--out-dir") {
                    ArgParseResult::Specified(dir) => out_dir = Some(dir),
                    ArgParseResult::ReadNext => {
                        let dir = iter.next().expect("Expected out_dir");
                        args.push(dir.clone());
                        out_dir = Some(dir);
                    }
                    ArgParseResult::None => {}
                }
            }
        }
    }

    // set plugin arg and debug option
    if let Some(path) = plugin_path {
        args.push(format!("-Zllvm-plugins={path}"));
        let mut debug_info = false;
        for arg in &mut args {
            if arg.starts_with("debuginfo=") {
                // ESSTRA LLVM Plugin only works with debuginfo=1
                *arg = "debuginfo=1".to_string();
                debug_info = true;
                break;
            }
        }
        if !debug_info {
            args.push("-C".to_string());
            args.push("debuginfo=1".to_string());
        }
    }

    // set env vars
    unsafe {
        env::remove_var("ESSTRA_DEPS_FILE");
        if let Some(out_dir) = out_dir {
            // get package info from env var
            let pkg_name = env::var("CARGO_PKG_NAME").expect("package name not set");
            let json_path = PathBuf::from(out_dir)
                .join(format!("{}.esstra-deps.json", pkg_name.replace("-", "_")));
            let mut data = EsstraDepsData {
                name: pkg_name,
                version: env::var("CARGO_PKG_VERSION").expect("package name not set"),
                deps: Vec::with_capacity(crates.len()),
            };
            // read dependencies file
            for krate in &crates {
                let mut iter = krate.split("=");
                let name = iter.next().unwrap().replace("-", "_");
                let mut path = PathBuf::from(iter.collect::<Vec<_>>().join("="));
                path.set_file_name(format!("{name}.esstra-deps.json"));
                match fs::read_to_string(&path)
                    .map(|json| serde_json::from_str(&json).expect("invalid JSON format"))
                {
                    Ok(dep) => {
                        data.deps.push(dep);
                    }
                    Err(e) => {
                        log::warn!("failed to read dep file: {e}");
                    }
                }
            }

            // write dependencies file
            let file = FileOptions::new().write(true).create(true).truncate(true);
            let mut lock = FileLock::lock(&json_path, true, file)
                .expect("failed to lock ESSTRA dependencies file");
            lock.file
                .write_all(serde_json::to_string(&data).unwrap().as_bytes())
                .expect("failed to write file");
            let _ = lock.unlock();
            env::set_var("ESSTRA_DEPS_FILE", json_path.as_os_str());
        }

        // enable nightly feature for llvm-plugins.
        // we cannot avoid this now.
        env::set_var("RUSTC_BOOTSTRAP", "1");
    }

    let cs_args: Vec<_> = args
        .iter()
        .map(|v| CString::new(&**v).expect("failed to convert command-line arguments to C string"))
        .collect();

    execvp(CString::new("rustc").unwrap().as_c_str(), &cs_args).expect("failed to call execvp");
}

// argument parser and its type
enum ArgParseResult {
    None,
    Specified(String),
    ReadNext,
}
fn parse_arg(arg: &str, get: &str) -> ArgParseResult {
    let include_equal = format!("{get}=");
    if arg.starts_with(&include_equal) {
        let (_, data) = arg.split_at(include_equal.len());
        ArgParseResult::Specified(data.to_string())
    } else if arg == get {
        ArgParseResult::ReadNext
    } else {
        ArgParseResult::None
    }
}
