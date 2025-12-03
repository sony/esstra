use crate::Error;
use std::path::Path;

mod binary;

/// utility function to get specified ELF section
pub fn get_elf_section(path: impl AsRef<Path>, section: &str) -> Result<String, Error> {
    let binary = binary::read_binary(path)?;
    let v = get_elf_section_from_binary(&binary, section)?;
    String::from_utf8(v.to_vec()).map_err(|_| Error::EsstraHeaderIsNotUtf8)
}

/// utility function to get specified ELF section from specified binary file
pub fn get_elf_section_from_binary<'a>(binary: &'a [u8], section: &str) -> Result<&'a [u8], Error> {
    let data = binary::minimal_parse(binary)?;
    let header = binary::get_header(&data, section)?.ok_or(Error::EsstraHeaderNotFound)?;
    binary::get_section_data(&data, &header)
}
