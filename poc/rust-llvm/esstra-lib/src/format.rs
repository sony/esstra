//! ESSTRA data format definitions and utilities module

use serde::{Deserialize, Serialize};

pub mod deps_file;
pub mod spdx;
pub mod yaml;

pub static ESSTRA_TOOL_NAME: &str = "ESSTRA Core";
pub static ESSTRA_TOOL_VERSION: &str = "0.4.0";

/// ESSTRA format
///
/// ESSTRA data has two representation: YAML and SPDX v3.
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(untagged)]
pub enum EsstraFormat {
    Yaml(Vec<yaml::EsstraFormat>),
    Spdx(Vec<spdx::SpdxV3Root>),
}
