use serde::{Deserialize, Serialize};

/// ESSTRA dependencies file representation
///
/// ESSTRA uses this representation to track dependencies in Rust.
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct EsstraDepsData {
    pub name: String,
    pub version: String,
    pub deps: Vec<EsstraDepsData>,
}
