//! ESSTRA for LLVM Test Utilities
//!
//! This program manages build and test suites for ESSTRA LLVM Plugin.

use anyhow::Context as _;
use clap::Parser;
use std::fs;
use std::path::PathBuf;
use std::process::exit;

mod builder;
mod crate_test;

#[derive(clap::Parser, Clone, Debug)]
struct Cli {
    #[clap(subcommand)]
    command: SubCommand,
}

#[derive(clap::Subcommand, Clone, Debug)]
enum SubCommand {
    Build {
        #[clap(default_value = "esstra-llvm-plugin")]
        plugin_dir: PathBuf,
        #[clap(default_value = "esstra-rustc")]
        rustc_esstra_dir: PathBuf,
        release: bool,
    },
    Install {
        #[clap(default_value = "esstra-llvm-plugin")]
        plugin_dir: PathBuf,
        #[clap(default_value = "esstra-rustc")]
        rustc_esstra_dir: PathBuf,
        release: bool,
        #[clap(default_value = "/usr/lib")]
        lib_install_dir: PathBuf,
        #[clap(default_value = "/usr/bin")]
        bin_install_dir: PathBuf,
    },

    Extract {
        binary: PathBuf,
    },
    Test {
        krate: String,
        version: String,
    },
}

fn main() {
    simple_logger::SimpleLogger::new()
        .with_colors(true)
        .with_level(log::LevelFilter::Info)
        .env()
        .init()
        .unwrap();

    let parsed = Cli::parse();
    match &parsed.command {
        SubCommand::Build {
            plugin_dir,
            rustc_esstra_dir,
            release,
        }
        | SubCommand::Install {
            plugin_dir,
            rustc_esstra_dir,
            release,
            ..
        } => {
            let plugin_path = match builder::build_esstra_llvm_plugin(plugin_dir, *release)
                .context("failed to build ESSTRA LLVM Plugin")
            {
                Ok(v) => v,
                Err(e) => {
                    log::error!("{e:?}");
                    exit(1);
                }
            };
            let esstra_rustc_path = match builder::build_esstra_rustc(rustc_esstra_dir, *release)
                .context("failed to build esstra-rustc")
            {
                Ok(v) => v,
                Err(e) => {
                    log::error!("{e:?}");
                    exit(1);
                }
            };

            if let SubCommand::Install {
                lib_install_dir,
                bin_install_dir,
                ..
            } = &parsed.command
            {
                let plugin_install_path = lib_install_dir.join(
                    match plugin_path
                        .file_name()
                        .context("failed to get plugin file name")
                    {
                        Ok(v) => v,
                        Err(e) => {
                            log::error!("{e:?}");
                            exit(1);
                        }
                    },
                );
                if let Err(e) =
                    fs::copy(&plugin_path, &plugin_install_path).context("failed to install plugin")
                {
                    log::error!("{e:?}");
                    exit(1);
                }
                log::info!(
                    "ESSTRA LLVM Plugin successfully installed at {}",
                    plugin_install_path.display(),
                );

                let esstra_rustc_install_path = bin_install_dir.join(
                    match esstra_rustc_path
                        .file_name()
                        .context("failed to get plugin file name")
                    {
                        Ok(v) => v,
                        Err(e) => {
                            log::error!("{e:?}");
                            exit(1);
                        }
                    },
                );
                if let Err(e) = fs::copy(&esstra_rustc_path, &esstra_rustc_install_path)
                    .context("failed to install esstra-rustc")
                {
                    log::error!("{e:?}");
                    exit(1);
                }
                log::info!(
                    "rustc-esstra successfully installed at {}",
                    esstra_rustc_install_path.display(),
                );
            }
        }

        SubCommand::Extract { binary } => {
            let res = match esstra_lib::analysis::get_elf_section(binary, ".esstra")
                .context("failed to extract ESSTRA data")
            {
                Ok(v) => v,
                Err(e) => {
                    log::error!("{e:?}");
                    exit(1);
                }
            };
            println!("{res}");
        }

        SubCommand::Test { krate, version } => {
            match crate_test::build_check(krate, version)
                .context(format!("failed to test {krate} v{version}"))
            {
                Ok(v) => {
                    exit(v);
                }
                Err(e) => {
                    log::error!("{e:?}");
                    exit(1);
                }
            }
        }
    }
}
