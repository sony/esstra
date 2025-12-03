# ESSTRA for LLVM compilers

This directory contains a proof-of-concept implementation of ESSRA for Rust and LLVM.

## LLVM Plugin

Please refer [ESSTRA LLVM Plugin](esstra-llvm-plugin/README.md) document.

## The Rust compiler of ESSTRA

Please refer [rustc-esstra](rustc-esstra/README.md) document.

## Try using ESSTRA

We provide Dockerfile to try using ESSTRA for ease.

Run:

```bash
docker build esstra-llvm:latest .
```

Now you can use ESSTRA LLVM Plugin:

```bash
docker run -it --rm esstra-llvm:latest /bin/bash
echo 'fn main() { println!("Hello, ESSTRA!"); }' > main.rs
rustc-esstra main.rs
```

You can see the data ESSTRA embedded in the executable `main`:

```bash
readelf -p.esstra main
```

Also, you can try ESSTRA with Clang:

```bash
echo 'int main() { return 0; }' > main.c
clang -g -fpass-plugin=/usr/lib/libesstra_llvm_plugin.so main.c
readelf -p.esstra a.out
```

We provide test utilities to show embedded ESSTRA data:

```bash
esstra-test-utils extract main
```

## Test ESSTRA in a Rust project

If you would like to test ESSTRA data embedding in `tree-sitter-cli` crate version `v0.25.9`, run

```bash
esstra-test-utils test tree-sitter-cli 0.25.9
```

You will receive the message `all expected dependencies are covered in SPDX v3 embedded in the binary` if the test succeeds.
