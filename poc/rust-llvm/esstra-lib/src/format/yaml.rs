//! ESSTRA YAML format representation
//!
//! this module defines a YAML format used in ESSTRA.

use serde::{Deserialize, Serialize};

pub static ESSTRA_DATA_FORMAT_VERSION: &str = "0.1.0";

/// ESSTRA core embedding data format, root
///
/// This is not currently used in production code,
/// but it is used in test, and might be used in production in the future.
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "PascalCase")]
pub struct EsstraFormat {
    pub headers: EsstraHeader,
    pub source_files: Vec<EsstraSourceDir>,
}
/// Represents ESSTRA header part
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "PascalCase")]
pub struct EsstraHeader {
    pub tool_name: String,
    pub tool_version: String,
    pub data_format_version: String,
    pub input_file_name: String,
}
/// Represents single source directory and its children
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "PascalCase")]
pub struct EsstraSourceDir {
    pub directory: String,
    pub files: Vec<EsstraSourceFile>,
}
/// Represents single source file
#[allow(non_snake_case)]
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "PascalCase")]
pub struct EsstraSourceFile {
    pub file: String,
    pub SHA1: String,
}
