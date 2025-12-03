use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use esstra_lib::format::{yaml::*, *};

/// Make ESSTRA YAML data from currently processing file paths
pub fn make_esstra_yaml(filename: &str, files: impl Iterator<Item = impl AsRef<Path>>) -> String {
    // Base ESSTRA data format;
    // We do not use `serde_yaml` because we would like to use consistent format with
    // current ESSTRA Core's YAML format
    let mut data = format!(
        r###"---
Headers:
  ToolName: {ESSTRA_TOOL_NAME}
  ToolVersion: {ESSTRA_TOOL_VERSION}
  DataFormatVersion: {ESSTRA_DATA_FORMAT_VERSION}
  InputFileName: {filename}
SourceFiles:"###
    );

    // BTreeMap/BTreeSet's keys/items are sorted
    let mut dirs = BTreeMap::new();
    for file in files {
        let file_path = file.as_ref();
        if file_path.is_dir() {
            dirs.entry(file_path.to_string_lossy().to_string())
                .or_insert_with(BTreeSet::new);
        } else {
            let dir_path = file_path.parent().unwrap();
            dirs.entry(dir_path.to_string_lossy().to_string())
                .or_insert_with(BTreeSet::new)
                .insert(file_path.file_name().unwrap().to_string_lossy().to_string());
        }
    }
    for (dir, files) in dirs.iter() {
        data.push_str(&format!("\n- Directory: {dir}"));
        data.push_str("\n  Files:");
        for file in files.iter() {
            let file_path = PathBuf::from(dir).join(file);
            let file_data = process_file_for_metadata(file_path);
            data.push_str(&format!("\n  - File: {file}"));
            // Embed file data (hash, etc...)
            for (key, datum) in file_data.iter() {
                data.push_str(&format!("\n    {key}: {datum}"));
            }
        }
    }

    data
}

/// Process file for obtaining metadata
///
/// Currently, we get only SHA1 hash.
pub fn process_file_for_metadata(file_path: impl AsRef<Path>) -> BTreeMap<String, String> {
    let file_path = file_path.as_ref();
    let mut file_info = BTreeMap::new();

    if let Some(hash) = super::file_sha1(file_path) {
        file_info.insert("SHA1".to_string(), hash);
    }

    file_info
}

#[cfg(test)]
mod test {
    use super::*;

    /// Validate output YAML format with [`serde_yaml`].
    /// We already defined ESSTRA Core YAML format as Rust types in [`EsstraFormat`].
    #[test]
    fn generated_yaml_validation() {
        let data = make_esstra_yaml(
            "examples/clang/multiple_files/main.c",
            [
                "examples/clang/multiple_files/main.c",
                "examples/clang/multiple_files/add.c",
            ]
            .iter(),
        );
        let format: yaml::EsstraFormat = serde_yaml::from_str(&data).unwrap();
        assert_eq!(format.headers.tool_name, ESSTRA_TOOL_NAME);
    }
}
