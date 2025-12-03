# ESSTRA for LLVM test utilities

This utility provides utilities to build ESSTRA for LLVM and testing its functionality.

## Usage

You can see all available commands:

```bash
esstra-test-utils --help
```

## Example

You can test ESSTRA for LLVM functionality by running test command:

```bash
esstra-test-utils test tree-sitter-cli 0.25.9
```
The example shown above will build `tree-sitter-cli` version 0.25.9 with `esstra-rustc` and check embedded ESSTRA data.
