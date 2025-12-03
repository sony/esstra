# ESSTRA for the Rust compiler

esstra-rustc is an ESSTRA implementation for the Rust compiler, rustc.

## Implementation

esstra-rustc simply behaves as rustc wrapper.
esstra-rustc parses command-line arguments to know the path of ESSTRA LLVM Plugin and to identify which crates are built with.

esstra-rustc will create dependency recording file in `target` directory to use in ESSTRA LLVM Plugin later.

## Usage

To specify ESSTRA LLVM Plugin path, set `ESSTRA_LLVM_PLUGIN_PATH` environment variable or use `--esstra-plugin-path=` command-line argument.

You can use esstra-rustc with cargo by setting an environment variable `RUSTC=esstra-rustc`.
By setting this environment variable, cargo will use esstra-rustc command instead of rustc to build a crate.
