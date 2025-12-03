//! ESSTRA common library, in ESSTRA for LLVM
//!
//! This library provides types and tools used in ESSTRA for LLVM.

pub mod analysis;
pub mod format;

pub use format::*;

/// ESSTRA common error
#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("File IO Error: {0:?}")]
    FileIoError(std::io::Error),
    #[error("Binary parse error: {0:?}")]
    BinaryParseError(elf::ParseError),
    #[error("ESSTRA header not found")]
    EsstraHeaderNotFound,
    #[error("ESSTRA header is not UTF-8 encoded")]
    EsstraHeaderIsNotUtf8,
    #[error("ESSTRA data parse error")]
    EsstraDataParseError,
}

/// Get ESSTRA data from a binary specified in the path
pub fn get_esstra_data(path: impl AsRef<std::path::Path>) -> Result<EsstraFormat, Error> {
    let data = analysis::get_elf_section(path, ".esstra")?;
    if let Ok(yaml) = serde_yaml::from_str(&data) {
        Ok(EsstraFormat::Yaml(yaml))
    } else {
        let spdxs: Result<Vec<_>, _> = data
            .split("\n")
            .filter(|v| !v.is_empty())
            .map(serde_json::from_str)
            .collect();
        if let Ok(spdxs) = spdxs {
            Ok(EsstraFormat::Spdx(spdxs))
        } else {
            Err(Error::EsstraDataParseError)
        }
    }
}
