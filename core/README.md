# ESSTRA Core

**ESSTRA Core** intervenes in the compilation process to gather information about all source
and header files involved, embedding this data as metadata in the resulting binary file.

In this version, **ESSTRA Core** creates an ELF section named `.esstra` in the resulting binary
file compiled with GCC. This section contains information about all files involved in the
compilation, including their full paths and SHA-1 hashes.

> [!NOTE]
> The current version of **ESSTRA** is under active development.
> Please be aware that the metadata format and content, as well as the specifications and
> functionality of each tool, are provisional and subject to change.

## How to Use

See the following sections in the [README.md](/README.md) file in the top-level directory for a
quick overview of how to use the tool:

* [How to Build and Install](/README.md#how-to-build-and-install)
* [Compiling](/README.md#compiling)
* [Installing GCC Spec File](/README.md#installing-gcc-spec-file)

## Known Issues

Here is the list of known issues in the current version:

* **LTO option prevents metadata generation**
  - **Description**: When using the LTO option (`-flto`) with `gcc`/`g++`,
    the generated binaries do not contain the expected metadata.
  - **Workaround**: Remove the LTO option.

## License

See the [LICENSE](/LICENSE) file.
