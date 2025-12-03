//! ESSTRA LLVM Plugin: An ESSTRA Core implementation for LLVM compilers

use esstra_lib::spdx;

use std::env;

use llvm_plugin::{
    inkwell::{
        // There are some functions not implemented in inkwell
        llvm_sys::core::LLVMAppendModuleInlineAsm,
    },
    LlvmModulePass, ModuleAnalysisManager, PassBuilder, PreservedAnalyses,
};

mod format;

/// ESSTRA core LLVM plugin entrypoint
///
/// Here, we register our _pass_ to LLVM callback.
/// It will be automatically called and embed ESSTRA data as assembly
#[llvm_plugin::plugin(name = "esstra_core", version = "0.4.0")]
fn plugin_registrar(builder: &mut PassBuilder) {
    // Setup logger for debug build only
    // This logger setup failed for some compilation tasks, so
    // we ignore an error.
    #[cfg(debug_assertions)]
    {
        let _ = simple_logger::SimpleLogger::new()
            .with_level(log::LevelFilter::Off)
            .env()
            .with_colors(true)
            .init();
    }

    #[cfg(not(feature = "llvm20-1"))]
    {
        builder.add_pipeline_early_simplification_ep_callback(|mpm, _optimization_level| {
            mpm.add_pass(AddSectionPass::default());
            log::info!("ESSTRA core registered");
        });
    }
    // callback registering interface is changed in LLVM 20.1
    #[cfg(feature = "llvm20-1")]
    {
        builder.add_pipeline_early_simplification_ep_callback(|mpm, _optimization_level, _lto| {
            mpm.add_pass(AddSectionPass::default());
            log::info!("ESSTRA core registered");
        });
    }
}

extern "C" fn is_required() -> bool {
    true
}

#[repr(C)]
#[allow(non_snake_case)]
pub struct AddSectionPass {
    isRequired: extern "C" fn() -> bool,
}
impl Default for AddSectionPass {
    fn default() -> Self {
        Self {
            isRequired: is_required,
        }
    }
}
/// A main implementation of ESSTRA Core for LLVM compilers
///
/// [`AddSectionPass::run_pass`] embeds ESSTRA data in binary.
impl LlvmModulePass for AddSectionPass {
    fn run_pass(
        &self,
        module: &mut llvm_plugin::inkwell::module::Module<'_>,
        _manager: &ModuleAnalysisManager,
    ) -> PreservedAnalyses {
        if let Ok(name) = env::var("CARGO_PKG_NAME") {
            if let Ok(version) = env::var("CARGO_PKG_VERSION") {
                // make embedding string
                let mut data = spdx::esstra_default_spdx_format();
                data.graph.push(spdx::SpdxV3AnyClass::SoftwarePackage {
                    props: spdx::SoftwarePackageProps {
                        version,
                        props: spdx::SoftwareArtifactProps {
                            props: spdx::ArtifactProps {
                                props: spdx::ElementProps {
                                    name: Some(name),
                                    creation_info: spdx::CreationInfo::IRI(spdx::IRI::default()),
                                    verified_using: None,
                                },
                            },
                        },
                    },
                });
                let data = serde_json::to_string(&data).unwrap();
                let asm = format::process_data_for_asm(&data);
                unsafe {
                    LLVMAppendModuleInlineAsm(
                        module.as_mut_ptr(),
                        asm.as_ptr() as *const i8,
                        asm.len(),
                    );
                }
                log::info!("inline asm appended");
                log::debug!("embedded data:\n{data}\n");
                return PreservedAnalyses::None;
            }
        }

        PreservedAnalyses::All
    }
}
