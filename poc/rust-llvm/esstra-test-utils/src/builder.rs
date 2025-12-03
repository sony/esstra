use anyhow::Context as _;
use std::path::{Path, PathBuf};
use std::process::Command;

/// Get LLVM version to pass feature flag to LLVM Plugin build command
pub fn get_llvm_feature_flag() -> anyhow::Result<String> {
    let output = Command::new("llvm-config")
        .args(["--version"])
        .output()
        .context("failed to execute llvm-config")?;
    let version = String::from_utf8(output.stdout)
        .context("failed to decode stdout as UTF-8")?
        .trim()
        .to_string();
    let flag = version.split(".").take(2).collect::<Vec<_>>().join("-");
    Ok(format!("llvm{flag}"))
}

/// A function to build ESSTRA LLVM Plugin
pub fn build_esstra_llvm_plugin(dir: impl AsRef<Path>, release: bool) -> anyhow::Result<PathBuf> {
    let metadata = cargo_metadata::MetadataCommand::new()
        .current_dir(dir.as_ref())
        .exec()
        .context("failed to get cargo metadata")?;
    let mut cargo = Command::new("cargo");
    cargo
        .current_dir(dir.as_ref())
        .args(["build", "-F", &get_llvm_feature_flag()?]);
    if release {
        cargo.arg("--release");
    }
    let code = cargo
        .spawn()
        .context("failed to spawn cargo")?
        .wait()
        .context("failed to wait finishing cargo")?
        .code();
    if code == Some(0) {
        let path = metadata
            .target_directory
            .as_std_path()
            .join(if release { "release" } else { "debug" })
            .join("libesstra_llvm_plugin.so");
        log::info!("ESSTRA LLVM Plugin successfully built: {}", path.display());
        Ok(path)
    } else {
        anyhow::bail!(format!("cargo process returns error code: {code:?}"))
    }
}

/// A function to build esstra-rustc
pub fn build_esstra_rustc(dir: impl AsRef<Path>, release: bool) -> anyhow::Result<PathBuf> {
    let metadata = cargo_metadata::MetadataCommand::new()
        .current_dir(dir.as_ref())
        .exec()
        .context("failed to get cargo metadata")?;
    let mut cargo = Command::new("cargo");
    cargo.current_dir(dir.as_ref()).args(["build"]);
    if release {
        cargo.arg("--release");
    }
    let code = cargo
        .spawn()
        .context("failed to spawn cargo")?
        .wait()
        .context("failed to wait finishing cargo")?
        .code();
    if code == Some(0) {
        let path = metadata
            .target_directory
            .as_std_path()
            .join(if release { "release" } else { "debug" })
            .join("esstra-rustc");
        log::info!("esstra-rustc successfully built: {}", path.display());
        Ok(path)
    } else {
        anyhow::bail!(format!("cargo process returns error code: {code:?}"))
    }
}
