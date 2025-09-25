# ESSTRA Link

**ESSTRA Link** is a [GNU linker plugin](https://sourceware.org/binutils/docs/ld/Plugins.html)
that performs post-processing during the linking phase of GCC to optimize the metadata embedded
in the resulting binary file.

Specifically, it removes redundant entries from the metadata originating from multiple object
files, ensuring the uniqueness of the information.

It also removes environment-specific path prefixes from file paths in metadata and converts
them to relative paths in order to ensure consistent path information across different
environments.

## Status of This Version

**ESSTRA Link** is currently being developed on Ubuntu 24.04 with GCC 13.3.0 and GNU ld 2.42
installed on an x86\_64 PC.

The current version of **ESSTRA Link** requires **ESSTRA Utility** to be installed on the
system in order to perform metadata optimization for binary files.

Please note that the specifications and the features of **ESSTRA Link** are tentative and may
change in future versions.

## How to Build and Install

Refer to the [How to Build and Install](/README.md#how-to-build-and-install) section of the
documentation found in the top-level directory.

## How to Use

Refer to the [Linking](/README.md#linking) section of the documentation found in the top-level
directory.


## License

See the [LICENSE](/LICENSE) file.
