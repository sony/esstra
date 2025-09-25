# ESSTRA Link

**ESSTRA Link** is a [GNU linker plugin](https://sourceware.org/binutils/docs/ld/Plugins.html)
that performs post-processing during the linking phase of GCC to optimize the metadata embedded
in the resulting binary file.

Specifically, it removes redundant entries from the metadata originating from multiple object
files, ensuring the uniqueness of the information.

It also removes environment-specific path prefixes from file paths in metadata and converts
them to relative paths in order to ensure consistent path information across different
environments.

> [!NOTE]
> The current version of **ESSTRA** is under active development.
> Please be aware that the metadata format and content, as well as the specifications and
> functionality of each tool, are provisional and subject to change.
>
> Additionally, the current version of **ESSTRA Link** requires **ESSTRA Utility** to be
> installed on the system in order to perform metadata optimization for binary files.

## How to Use

See the following sections in the [README.md](/README.md) file in the top-level directory for a
quick overview of how to use the tool:

* [How to Build and Install](/README.md#how-to-build-and-install)
* [Linking](/README.md#linking)
* [Installing GCC Spec File](/README.md#installing-gcc-spec-file)

## License

See the [LICENSE](/LICENSE) file.
