use esstra_lib::format::deps_file::EsstraDepsData;
use esstra_lib::*;
use std::env;
use std::fs;
use std::path::Path;
use std::process::exit;

/// Get SPDX representation from [`EsstraDepsData`] representation
fn get_spdx_recursive(data: EsstraDepsData) -> Vec<spdx::SpdxV3AnyClass> {
    let mut deps = Vec::new();
    deps.push(spdx::SpdxV3AnyClass::SoftwarePackage {
        props: spdx::SoftwarePackageProps {
            version: data.version,
            props: spdx::SoftwareArtifactProps {
                props: spdx::ArtifactProps {
                    props: spdx::ElementProps {
                        name: Some(data.name),
                        creation_info: spdx::CreationInfo::IRI(spdx::IRI::default()),
                        verified_using: None,
                    },
                },
            },
        },
    });
    for dep in data.deps {
        deps.extend_from_slice(&get_spdx_recursive(dep));
    }
    deps
}

/// Make ESSTRA data in SPDX v3 format.
/// We panic if serialization failed, which should not be occurred.
/// And we should panic instead of silently ignore errors.
pub fn make_esstra_spdx(files: impl Iterator<Item = impl AsRef<Path>>) -> String {
    let mut data = spdx::esstra_default_spdx_format();
    let files: Vec<_> = files.collect();

    // check Rust package information
    //
    // By default, we exclude packages that would not be linked, e.g, macro packages.
    // ESSTRA cannot know these packages from final binary.
    if let Ok(path) = env::var("ESSTRA_DEPS_FILE") {
        match fs::read_to_string(&path) {
            Ok(json) => match serde_json::from_str::<EsstraDepsData>(&json) {
                Ok(deps) => {
                    data.graph.extend_from_slice(&get_spdx_recursive(deps));
                }
                Err(e) => {
                    log::error!("invalid ESSTRA dependencies file format: {e}");
                    exit(1);
                }
            },
            Err(e) => {
                log::error!("failed to read ESSTRA dependencies file: {e}");
                exit(1);
            }
        }
    }

    // append all file metadata
    let file_data = files.iter().map(|v| spdx::SpdxV3AnyClass::SoftwareFile {
        props: spdx::SoftwareFileProps {
            artifact_props: spdx::SoftwareArtifactProps {
                props: spdx::ArtifactProps {
                    props: spdx::ElementProps {
                        name: Some(v.as_ref().to_string_lossy().to_string()),
                        creation_info: spdx::CreationInfo::IRI(spdx::IRI::default()),
                        verified_using: super::file_sha1(v.as_ref()).map(|v| {
                            vec![spdx::IntegrityMethod::Hash(spdx::Hash::Sha1 {
                                hash_value: v,
                            })]
                        }),
                    },
                },
            },
        },
    });
    for file in file_data {
        data.graph.push(file);
    }

    serde_json::to_string(&data).expect("failed to serialize SPDX v3")
}
