//! ESSTRA binary analysis utilities

use crate::Error;
use elf::{endian::AnyEndian, section::SectionHeader, ElfBytes};
use std::fs;
use std::path::Path;

pub fn read_binary(path: impl AsRef<Path>) -> Result<Vec<u8>, Error> {
    let path = path.as_ref();
    fs::read(path).map_err(Error::FileIoError)
}
pub fn minimal_parse(binary: &[u8]) -> Result<ElfBytes<'_, AnyEndian>, Error> {
    ElfBytes::<AnyEndian>::minimal_parse(binary).map_err(Error::BinaryParseError)
}

pub fn get_header(
    data: &ElfBytes<AnyEndian>,
    header_name: &str,
) -> Result<Option<SectionHeader>, Error> {
    data.section_header_by_name(header_name)
        .map_err(Error::BinaryParseError)
}

pub fn get_section_data<'data>(
    data: &ElfBytes<'data, AnyEndian>,
    header: &SectionHeader,
) -> Result<&'data [u8], Error> {
    data.section_data(header)
        .map(|(data, _)| data)
        .map_err(Error::BinaryParseError)
}
