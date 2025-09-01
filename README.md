# Project ESSTRA

Project **ESSTRA**, a software suite for
**E**nhancing **S**oftware **S**upply Chain **Tra**nsparency,
aims to improve transparency of software supply chains as the name suggests.

More specifically, the goal of the project is to provide a set of tools to help illuminate and
unveil the "dark" areas in the software supply chain where critical information about software
components is unclear, primarily from a software traceability and compliance perspective.

In the current version of **ESSTRA**, metadata is embedded into the resulting binary files at
compile time using GCC.
The metadata contains information about the source and header files from which the binary file
has been generated.

For detailed usage and applications, please refer to the
[Samples](./samples/)
that help you understand **ESSTRA** using simple source code, as well as the
[Case Study documentation](./doc/case-study)
on using **ESSTRA** for open-source software and Linux distributions.

> [!NOTE]
> The current version of **ESSTRA** is under active development.
> The metadata format and content, as well as the specifications and functionality of each
> tool, are provisional and subject to change.

For a detailed overview of ESSTRA, please refer to [the presentation delivered at Open Source Summit Europe 2025](https://static.sched.com/hosted_files/osseu2025/64/20250825_OSSEU2025_ESSTRA.pdf).

## Status of This Version
>>>>>>> main

## Development Environment

**ESSTRA** is developed and tested on a PC (x86_64 architecture) running Ubuntu 24.04, using
GCC 13.3.0 and Python 3.12.3.
Compatibility testing has also been conducted on Ubuntu 22.04 with GCC 11.4.0 and Python 3.10.12.

## ESSTRA's Components

The current version of **ESSTRA** consists of the three tools:

* [**ESSTRA Core**](./core/README.md)
* [**ESSTRA Link**](./link/README.md)
* [**ESSTRA Utility**](./util/README.md)

**ESSTRA Core** (`esstracore.so`) is a [GCC plugin](https://gcc.gnu.org/wiki/plugins) that
intervenes the compilation process to embed metadata into the resulting binary files (i.e.,
object files).
In the current version, metadata is embedded for all source and header files involved in the
compilation, including their absolute paths and checksums.

**ESSTRA Link** (`esstralink.so`) is a
[GNU linker plugin](https://sourceware.org/binutils/docs/ld/Plugins.html)
that performs post-processing during the linking phase of GCC to optimize the metadata embedded
in the resulting binary file.
Specifically, it removes redundant entries from the metadata originating from multiple object
files, ensuring the uniqueness of the information.

**ESSTRA Utility** (`esstra`) is a Python script that provides access to the metadata embedded
in binary files by **ESSTRA Core** and **ESSTRA Link**.
It offers functionality such as displaying metadata contents, attaching related information,
and removing metadata from binary files.

## Technical Overview

**ESSTRA Core** creates an ELF section in the resulting object file to store metadata during
compilation.

**ESSTRA Link** performs post-linking analysis to inspect and optimize the metadata merged by
the linker.

**ESSTRA Utility** allows users to access the metadata.  For example, you can update the
metadata using license information detected from the source files, delete some or all of the
metadata, output the metadata to the console, or pass it to other SCA (Software Composition
Analysis) tools.

![Technical Overview](./assets/tech-overview.png)

## How to Build and Install

Before you build the GCC plugin, you have to install a package on your system.
For Debian/Ubuntu, check the version of GCC first:

```sh
$ gcc --version
gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
...
or
$ gcc -dumpversion
13
```

In this case, the major version is 13, so install the package named `gcc-13-plugin-dev`:

```sh
$ sudo apt install gcc-13-plugin-dev
```

Since **ESSTRA Utility** uses the [PyYAML](https://pyyaml.org/) module to handle YAML
data, you may need to install it:

```sh
$ sudo apt install python3-yaml
```

After that, run `make` in the top directory:

```sh
$ make
```

If no errors, the build is complete.

To install **ESSTRA Core**, **ESSTRA Link** and **ESSTRA Utility** on your system, run the following command:

```sh
$ sudo make install
```

Then, `esstracore.so` and `esstralink.so` are installed to
`/usr/local/lib/gcc/<gcc-arch>/<gcc-major-version>/plugin/`,
and the script `esstra` is installed to `/usr/local/bin/` by default.
Please make sure that `/usr/local/bin` is included in your system's PATH.

Here, `<gcc-arch>` refers to a string like `x86_64-linux-gnu`, which can be obtained using the
`gcc -dumpmachine` command, and `<gcc-major-version>` refers to a number like `13`, obtained
via `gcc -dumpversion`.

In the case of our development environment mentioned above, the installation path of
`esstracore.so` and `esstralink.so` is `/usr/local/lib/gcc/x86_64-linux-gnu/13/plugin/`.

## How to Use

The workflow using **ESSTRA** consists of the following steps:

1. Compile source files with GCC using **ESSTRA Core** to generate object files.
2. Link the object files using **ESSTRA Link** to produce the binary file.
3. Access the metadata embedded in the binary file using **ESSTRA Utility**.

The example below compiles the source file `main.c` and `sub.c` with `gcc` and generates the
binary file `hello`.

### Compiling

First, compile the source file `main.c` and `sub.c` by passing the path of `esstracore.so` to
the compiler with the option `-fplugin=`:

```sh
$ gcc -fplugin=/usr/local/.../esstracore.so -c main.c -o main.o
$ gcc -fplugin=/usr/local/.../esstracore.so -c sub.c -o sub.o
```

Then the intervention of `esstracore.so` embeds metadata in the resulting object files
`main.o` and `sub.o`.

For more details on **ESSTRA Core**, please refer to [core/README.md](/core/README.md).

### Linking

Since `gcc` allows linker options to be specified using the `-Wl,<option>` flag, the following
command links the object files and produces the binary file `hello`, while passing the path to
`esstralink.so` to the linker via the `-plugin=` option:

```sh
$ gcc -Wl,-plugin=/usr/local/.../esstralink.so main.o sub.o -o hello
```

As a result, the generated `hello` binary file contains optimized metadata inherited from the
object files `main.o` and `sub.o`.

Note that **ESSTRA**'s intervention in the compilation and linking process does not affect the
behavior of the resulting binary files.

For more details on **ESSTRA Link**, please refer to [link/README.md](/link/README.md).

### More Simple Way

The entire process can also be performed in a single command:

```sh
$ gcc -fplugin=/usr/local/.../esstracore.so \
      -Wl,-plugin=/usr/local/.../esstralink.so \
      main.c sub.c -o hello
```

### Accessing the Metadata

To access the embedded metadata, use the script `esstra`.  The
first argument of this script is a *command*, and the second or subsequent arguments are the
arguments of the *command*.

The command `show` outputs metadata in binary files in YAML format to the standard output.
A command line:

```sh
$ esstra show hello
```

would generate an output as follows:

```yaml
#
# BinaryFileName: hello
# BinaryPath: /home/snagao/work/esstra-test/hello
#
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.2.0
  DataFormatVersion: 0.1.0
  InputFileNames:
  - main.c
  - sub.c
SourceFiles:
- Directory: /home/snagao/work/esstra-test
  Files:
  - File: main.c
    SHA1: f7f5c447d68fd9685594a31cb10c8d8b1dd5ebd6
  - File: sub.c
    SHA1: cfb72998ae0242237fa42c8bcf61ee5887137392
  - File: sub.h
    SHA1: 3e5b3ed1aed966c0e0c183eac8fe6ea02dfa62a0
- Directory: /usr/include
  Files:
  - File: features-time64.h
    SHA1: 57c3c8093c3af70e5851f6d498600e2f6e24fdeb
  - File: features.h
    SHA1: d8725bb98129d6d70ddcbf010021c2841db783f7
  - File: stdc-predef.h
    SHA1: 2fef05d80514ca0be77efec90bda051cf87d771f
  - File: stdio.h
    SHA1: c7181b48c4194cd122024971527aab4056baf600
- Directory: /usr/include/x86_64-linux-gnu/bits
  Files:
  - File: floatn-common.h
    SHA1: 3f37104123a2e6180621331c1da87125808e47bd
  - File: floatn.h
    SHA1: 806b759ab6894a09a3b3a422eec5f2414ba7dab7
  - File: libc-header-start.h
    SHA1: e0a400c194cd3962a342a6504a441920163b799c
  - File: long-double.h
    SHA1: 4e3f5928e816ad29079d1c7d75f3a510a0939ffb
  - File: stdio.h
    SHA1: 521d7cd0f6572f70122386784120cc55d84899bc
  - File: stdio2.h
    SHA1: 6c3ee923db9679a79941a688de72e114a794fc54
  - File: stdio_lim.h
    SHA1: 6210c8ae410ee0f39a6096b0adb9fa86febd3517
  - File: time64.h
    SHA1: ab2017da21608498b58eea37b2aa6a3387ee978c
  - File: timesize.h
    SHA1: f1dd8d62a4d75288654626933edfc82ccf2394a7
  - File: types.h
    SHA1: e5893a9c4c523615c73a51feb9680279608027c6
  - File: typesizes.h
    SHA1: ee94b5a60d007c23bdda9e5c46c8ba40f4eb402c
  - File: wordsize.h
    SHA1: 281ddd3c93f1e8653e809a45b606574c9b691092
- Directory: /usr/include/x86_64-linux-gnu/bits/types
  Files:
  - File: FILE.h
    SHA1: 497924e329d53517631713ae52acb73e870d7d65
  - File: __FILE.h
    SHA1: 274242343e85d1c06e7f5ccc5abf15e120f6e957
  - File: __fpos64_t.h
    SHA1: ac38e294b004f6e2bf18f1c55e03dc80f48d6830
  - File: __fpos_t.h
    SHA1: 760ef77769ac1921f4b1f908cbf06863e2506775
  - File: __mbstate_t.h
    SHA1: e3a4f2ee55e635520db0b4610d2b361e9ce41de7
  - File: struct_FILE.h
    SHA1: 1dbf8bac589cb09e09aa4c1d36913e549a57bcf0
- Directory: /usr/include/x86_64-linux-gnu/gnu
  Files:
  - File: stubs-64.h
    SHA1: f7603fa3908b56e9d1b33c91590db3252e13a799
  - File: stubs.h
    SHA1: be168037b7503a82b1cf694cdbac8c063bb6e476
- Directory: /usr/include/x86_64-linux-gnu/sys
  Files:
  - File: cdefs.h
    SHA1: a419a6372029d89ba38ada0811d34f51df8d09b7
- Directory: /usr/lib/gcc/x86_64-linux-gnu/11/include
  Files:
  - File: stdarg.h
    SHA1: fa23f49da8a0a5068b781dff7182f1a1c363dc30
  - File: stddef.h
    SHA1: 0de70008ffa3f198baf55c7b3f3d03b4ca11c21f
```

For more details on **ESSTRA Utility** and the structure of the metadata, please refer to
[util/README.md](/util/README.md).

## Installing GCC Spec File

Specifying `-fplugin=...` and `-Wl,-plugin=...` every time you run `gcc` or `g++` can be
tedious. To simplify this process, run the following command:

```sh
$ sudo make install-specs
```

This installs a [GCC spec file](https://gcc.gnu.org/onlinedocs/gcc/Spec-Files.html)
that configures your system to automatically apply the following options:

* `-fplugin=/usr/local/.../esstracore.so` (for `gcc/g++`)
* `-plugin=/usr/local/.../esstralink.so` (for `ld`)

After installation, you can compile your code as usual:

```sh
$ gcc main.c sub.c -o hello
```

**ESSTRA Core** and **ESSTRA Link** will be automatically used during compilation and linking,
embedding and optimizing metadata in the resulting binary `hello`.

This is a very handy feature when you want to get the information **ESSTRA** generates while
compiling any kind of project -- whether it's open-source or closed-source.

> [!WARNING]
> Once the spec file is installed,
> **all compilation and linking processes across the entire system**
> will involve **ESSTRA Core** and **ESSTRA Link**.
> Please install the spec file with caution to avoid unintended interference.

To uninstall the spec file, run:

```sh
$ sudo make uninstall-specs
```

> [!WARNING]
> `make install-specs` and `make uninstall-specs` commands will overwrite or delete a spec file
> **regardless of whether you already have your own spec file**.
> So, if you have your own spec file, please refrain from using these commands and edit the
> spec file manually instead.

## How to Uninstall

To uninstall the ESSTRA Core, the ESSTRA Utility, and spec file from your system, run the
following command in the top directory :

```sh
$ sudo make uninstall
```

## License

See the [LICENSE](./LICENSE) file.
