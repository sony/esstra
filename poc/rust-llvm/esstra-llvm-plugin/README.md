# ESSTRA Core LLVM Plugin

This is ESSTRA Core implementation for LLVM.

## Build

For the first, you have to identify the version of LLVM installed in your environment.
The LLVM version must be compatible with the Rust compiler's one.

To know LLVM version:

```bash
llvm-config --version
```

To know rustc's LLVM version:

```bash
rustc -vV
```

For example, if you identify LLVM version as 20.1.7, you can build the plugin by running:

```bash
cargo build --release -F llvm20-1
```

You will get `libesstra_llvm_plugin.so` in `target/release` directory.

## Usage

You can use ESSTRA LLVM Plugin with any compiler that supports LLVM plugins and embeds debug information in the binary.

### Clang

You can use ESSTRA LLVM Plugin with Clang:

```bash
clang -g -fpass-plugin=target/release/libesstra_llvm_plugin.so examples/clang/main.c
```

You have to specify `-g` option to embed file information.

### Rust

You can embed ESSTRA data built with rustc by using `esstra-rustc`:

```bash
esstra-rustc examples/rustc/main.rs
```

You can also use with Cargo by setting an environment variable `RUSTC=esstra-rustc`:

```bash
cargo new project1
cd project1
cargo add log
echo 'fn main() { log::info!("Hello"); }' > src/main.rs
RUSTC=esstra-rustc cargo build
```

For Rust specific implementation, ESSTRA LLVM Plugin reads dependencies recording file written by esstra-rustc and embeds its data in the binary.

## Confirm the result

You can confirm the data embedded in the binary by running:

```bash
readelf -p.esstra [your-binary]
```

Also, you can use esstra-test-utils command:

```bash
esstra-test-utils extract [your-binary]
```

## Debugging

You can see debug output by specifying environment variable `RUST_LOG=debug`.
Debug output is disabled in release build.
