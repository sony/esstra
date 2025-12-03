use anyhow::Context as _;
use cargo_metadata::TargetKind;
use esstra_lib::format::spdx;
use flate2::bufread::GzDecoder;
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process;
use tar::Archive;

// get host target to filter target-specific dependencies
fn get_host_tuple() -> anyhow::Result<String> {
    let output = process::Command::new("rustc")
        .arg("--print=host-tuple")
        .output()
        .context("failed to get host-tuple")?;
    String::from_utf8(output.stdout)
        .context("string is not UTF-8 encoded")
        .map(|v| v.trim().to_string())
}

/// Download crate from crates.io and extract it to destination directory.
pub fn download_and_extract_crate(
    dest: impl AsRef<Path>,
    name: &str,
    version: &str,
) -> anyhow::Result<PathBuf> {
    log::info!("downloading {name} v{version}...");
    // FIXME: we need to specify User-Agent
    let resp = reqwest::blocking::get(format!(
        "https://crates.io/api/v1/crates/{name}/{version}/download"
    ))
    .context("failed to download")?;
    let bytes = resp.bytes().context("failed to download bytes")?;
    let gze = GzDecoder::new(bytes.as_ref());
    log::info!("extracting {name} v{version}...");
    Archive::new(gze)
        .unpack(dest.as_ref())
        .context("failed to unpack")?;
    Ok(dest.as_ref().join(format!("{name}-{version}")))
}

/// this returns a map from binary name to all dependencies of its binary package
pub fn get_bin_deps(
    name: &str,
    crate_dir: impl AsRef<Path>,
) -> anyhow::Result<BTreeMap<String, BTreeMap<String, String>>> {
    let target = get_host_tuple()?;

    // get binary package list
    let metadata = cargo_metadata::MetadataCommand::new()
        .current_dir(crate_dir.as_ref())
        .exec()
        .context("failed to get cargo metadata")?;
    let bins: Vec<_> = metadata
        .packages
        .iter()
        .filter_map(|v| {
            if v.name == name {
                Some(v.targets.iter().filter_map(|w| {
                    if w.kind.contains(&TargetKind::Bin) {
                        Some(w.name.clone())
                    } else {
                        None
                    }
                }))
            } else {
                None
            }
        })
        .flatten()
        .collect();

    let mut result = BTreeMap::new();
    for bin in bins {
        // parse `cargo tree` command
        let entry = result.entry(bin).or_insert_with(BTreeMap::new);
        let mut cmd = process::Command::new("cargo");
        let output = cmd
            .current_dir(crate_dir.as_ref())
            .args([
                "tree",
                &format!("--package={name}"),
                "--edges=normal",
                "--prefix=none",
                &format!("--target={target}"),
            ])
            .output()
            .context("failed to get cargo tree")?;

        let deps = String::from_utf8(output.stdout).context("failed to decode as UTF-8")?;
        for dep in deps.lines() {
            if dep.is_empty() {
                continue;
            }
            let mut split = dep.split(" ");
            let krate = split.next().context("failed to get crate name")?;
            let version = split.next().context("failed to get crate version")?;
            let (_v, version) = version.split_at(1);
            entry.insert(krate.to_string(), version.to_string());
        }
    }
    Ok(result)
}

/// Test ESSTRA by download, build a binary package, and extract embedded info from the binary.
pub fn build_check(name: &str, version: &str) -> anyhow::Result<i32> {
    let path = download_and_extract_crate("/tmp", name, version)
        .context("failed to download/extract crate")?;
    let bin_deps = get_bin_deps(name, &path).context("failed to get crate's dependencies")?;

    // build package
    let mut cmd = process::Command::new("cargo");
    let mut child = cmd
        .current_dir(&path)
        .args(["build", "--release"])
        .env("RUSTC", "esstra-rustc")
        .env("RUST_LOG", "off")
        .env("ESSTRA_FORMAT_YAML", "0")
        .spawn()
        .context("failed to spawn build process")?;
    let status = child.wait().context("failed to wait build process")?;
    if !status.success() {
        anyhow::bail!("build process exited with unsuccessful status");
    }
    // get target directory path
    let target = cargo_metadata::MetadataCommand::new()
        .current_dir(&path)
        .exec()
        .context("failed to get crate's metadata")?
        .target_directory
        .as_std_path()
        .to_path_buf();
    let dir = target.join("release");

    // check dependencies for each package, i.e. package build artifact
    for (bin, deps) in bin_deps.into_iter() {
        log::info!("start analyzing binary: {bin}");
        let bin_path = dir.join(bin);
        let data =
            esstra_lib::get_esstra_data(&bin_path).context("failed to get ESSTRA section")?;
        let mut embedded_packages = BTreeMap::new();
        let mut covered_packages = BTreeMap::new();
        if let esstra_lib::EsstraFormat::Spdx(spdx) = data {
            for root in &spdx {
                for data in &root.graph {
                    if let spdx::SpdxV3AnyClass::SoftwarePackage {
                        props:
                            spdx::SoftwarePackageProps {
                                props:
                                    spdx::SoftwareArtifactProps {
                                        props:
                                            spdx::ArtifactProps {
                                                props:
                                                    spdx::ElementProps {
                                                        name: Some(name), ..
                                                    },
                                            },
                                        ..
                                    },
                                version,
                            },
                    } = data
                    {
                        embedded_packages.insert(name.clone(), version.clone());
                        if let Some(expected_version) = deps.get(name) {
                            if !covered_packages.contains_key(name) && version == expected_version {
                                log::debug!("{name} v{version} covered");
                                covered_packages.insert(name.clone(), version.clone());
                            }
                        }
                    }
                }
            }
            log::debug!("embedded total packages: {embedded_packages:?}");
            log::debug!("expected dependent packages: {deps:?}");
            let deps_keys: BTreeSet<_> = deps.keys().cloned().collect();
            let embedded_keys: BTreeSet<_> = embedded_packages.keys().cloned().collect();
            let not_covered: BTreeSet<_> = deps_keys.difference(&embedded_keys).collect();
            if !not_covered.is_empty() {
                log::error!("not-covered packages: {not_covered:?}");
                log::error!(
                    "some expected dependencies are not covered in SPDX v3 embedded in the binary; see debug log"
                );
                return Ok(1);
            } else {
                log::info!(
                    "all expected dependencies are covered in SPDX v3 embedded in the binary"
                );
                if deps.len() < embedded_packages.len() {
                    log::warn!(
                        "there are some dependencies not expected in the binary; it's may be grandchild dependencies"
                    )
                }
            }
        } else {
            anyhow::bail!("crate test does not support ESSTRA YAML format");
        }
    }
    Ok(0)
}
