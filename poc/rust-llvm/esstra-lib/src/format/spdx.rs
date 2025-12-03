//! ESSTRA format compliant with SPDX v3
//! This format definition is WIP and it is subset of SPDX v3.0.1
//!
//! Please refer [a schema file](https://spdx.github.io/spdx-spec/v3.0.1/rdf/schema.json).

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub enum SpdxGlobalContext {
    #[serde(rename = "https://spdx.org/rdf/3.0.1/spdx-context.jsonld")]
    V3_0_1,
}

/// SPDX v3 representation Root
/// We define this based on [JSON-LD schema](https://spdx.github.io/spdx-spec/v3.0.1/rdf/schema.json)
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SpdxV3Root {
    #[serde(rename = "@context")]
    pub context: SpdxGlobalContext,
    #[serde(rename = "@graph")]
    pub graph: Vec<SpdxV3AnyClass>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(tag = "type")]
pub enum SpdxV3AnyClass {
    Tool {
        #[serde(rename = "spdxId")]
        spdx_id: IRI,
        #[serde(flatten)]
        props: ElementProps,
    },
    #[serde(rename = "software_File")]
    SoftwareFile {
        #[serde(flatten)]
        props: SoftwareFileProps,
    },
    #[serde(rename = "software_ContentIdentifier")]
    SoftwareContentIdentifier {
        #[serde(flatten)]
        props: SoftwareContentIdentifierProps,
    },

    #[serde(rename = "software_Package")]
    SoftwarePackage {
        #[serde(flatten)]
        props: SoftwarePackageProps,
    },
}

#[derive(Serialize, Deserialize, Default, Clone, Debug)]
#[serde(transparent)]
pub struct IRI(pub String);
impl From<&str> for IRI {
    fn from(value: &str) -> Self {
        Self(value.to_string())
    }
}

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(tag = "type")]
pub enum CreationInfo {
    CreationInfo {
        #[serde(rename = "@id")]
        id: IRI,
        #[serde(flatten)]
        props: CreationInfoProps,
    },
    #[serde(untagged)]
    IRI(IRI),
}
//
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct CreationInfoProps {
    pub created: String,
    #[serde(rename = "createdBy")]
    pub created_by: Vec<Agent>,
    //#[serde(rename = "createdUsing")]
    //pub created_using: Vec<ElementProps>,
    //#[serde(rename = "specVersion")]
    //pub spec_version: String,
}
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ElementProps {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(rename = "creationInfo")]
    pub creation_info: CreationInfo,
    #[serde(rename = "verifiedUsing", skip_serializing_if = "Option::is_none")]
    pub verified_using: Option<Vec<IntegrityMethod>>,
}
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(tag = "type")]
pub enum IntegrityMethod {
    Hash(Hash),
}
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(tag = "algorithm")]
pub enum Hash {
    #[serde(rename = "SHA1")]
    Sha1 {
        #[serde(rename = "hashValue")]
        hash_value: String,
    },
}
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct ArtifactProps {
    #[serde(flatten)]
    pub props: ElementProps,
}

//
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SoftwareFileProps {
    #[serde(flatten)]
    pub artifact_props: SoftwareArtifactProps,
}

//
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SoftwareArtifactProps {
    #[serde(flatten)]
    pub props: ArtifactProps,
    //#[serde(rename = "software_contentIdentifier")]
    //pub software_content_identifier: Option<Vec<SoftwareContentIdentifier>>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(tag = "type")]
pub enum SoftwareContentIdentifier {
    #[serde(rename = "software_ContentIdentifier")]
    ContentIdentifier(SoftwareContentIdentifierProps),
}
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SoftwareContentIdentifierProps {
    #[serde(rename = "software_contentIdentifierValue")]
    pub value: SoftwareContentIdentifierValue,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct SoftwarePackageProps {
    #[serde(flatten)]
    pub props: SoftwareArtifactProps,
    #[serde(rename = "software_packageVersion")]
    pub version: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(transparent)]
pub struct SoftwareContentIdentifierValue(pub AnyUri);

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(transparent)]
pub struct AnyUri(pub String);

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(tag = "type")]
pub enum Agent {
    Organization {
        #[serde(rename = "spdxId")]
        spdx_id: IRI,
        #[serde(flatten)]
        props: ElementProps,
    },
}

pub fn esstra_default_spdx_format() -> SpdxV3Root {
    SpdxV3Root {
        context: SpdxGlobalContext::V3_0_1,
        graph: vec![SpdxV3AnyClass::Tool {
            // FIXME: Do we have to include version or commit hash in this link?
            spdx_id: IRI::from("https://github.com/sony/esstra/tree/main"),
            props: ElementProps {
                name: Some(super::ESSTRA_TOOL_NAME.to_string()),
                creation_info: CreationInfo::CreationInfo {
                    // FIXME: Replace appropriate license link
                    // it should be fixed by commit hash
                    id: IRI::from("https://github.com/sony/esstra/blob/main/LICENSE"),
                    props: CreationInfoProps {
                        created: "".to_string(),
                        created_by: vec![Agent::Organization {
                            spdx_id: IRI::default(),
                            props: ElementProps {
                                name: Some("Sony Group Corporation".to_string()),
                                creation_info: CreationInfo::IRI(IRI::default()),
                                verified_using: None,
                            },
                        }],
                    },
                },
                verified_using: None,
            },
        }],
    }
}
