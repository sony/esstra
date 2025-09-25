# Sample "hello"

This sample explains how to use **ESSTRA** with a simple C source code. The
document is structured as a step-by-step guide, allowing you to easily
understand the basic operations of **ESSTRA** by following each step in sequence.

First, in this sample, we will compile [`hello.c`](./hello.c), which is
provided in this directory, using [**ESSTRA Core**](/core/README.md) to
generate the binary file `hello`. This binary has metadata embedded that
contains information about all source files involved in the compilation, such
as absolute paths and checksums. We will verify this using
[**ESSTRA Utility**](/util/README.md).

Next, we will demonstrate how to use **ESSTRA Utility**'s feature that adds license information
of source files to the metadata.  In this sample, we will use the license information files
prepared by the license analysis tools.  Using this information, we will update the metadata
with **ESSTRA Utility** and verify that the license information has been correctly associated
with the metadata.

The license information files
[`SPDX2TV_esstra_fossology.spdx`](../output-examples/SPDX2TV_esstra_fossology.spdx) and [`SPDX2TV_esstra_scancode.spdx`](../output-examples/SPDX2TV_esstra_scancode.spdx)
were generated using the open-source license analysis tools
[FOSSology](https://github.com/fossology/fossology) and [ScanCode toolkit](https://github.com/aboutcode-org/scancode-toolkit) respectively.
If you are interested in how to use these tools, please refer to the following documents:

* [License Analysis Using FOSSology](./README_FOSSOLOGY.md)
* [License Analysis Using ScanCode toolkit](./README_SCANCODE.md)

## Building and Installing ESSTRA

First, build and install **ESSTRA** on your system. In the top directory, enter:

```sh
$ make
```

If there are no errors, the build is complete. Then, enter:

```sh
$ sudo make install
```

This will install **ESSTRA Core**, **ESSTRA Link** and **ESSTRA Utility** on your system.

## Source Code to Compile

In this sample, we will compile the source code [`hello.c`](hello.c) using
**ESSTRA Core**. The content of the code is as follows, and it is a very simple
program that just prints `Hello, world!` to the standard output:

```c
#include <stdio.h>

int main(void)
{
    printf("Hello, world!\n");
    return 0;
}
```

Additionally, at the beginning of the source code, we explicitly state the
license so that FOSSology can scan it:

```c
// SPDX-License-Identifier: MIT
```

This declaration indicates that this file is available under the
[MIT License](https://spdx.org/licenses/MIT.html).

## Compiling with ESSTRA Core

Use the following command line to compile [`hello.c`](./hello.c) and generate
the binary `hello`. By involving **ESSTRA Core** during compilation,
metadata will be embedded into `hello`.
Since we are using GCC version 11 on an x86\_64 PC, the command line would be as follows:

```sh
$ gcc -fplugin=/usr/local/lib/gcc/x86_64-linux-gnu/11/plugin/esstracore.so hello.c -o hello
```

If you have already [installed the Spec File](/README.md#installing-spec-file),
**ESSTRA Core** will intervene in the compilation without needing the
`-fplugin=` option, yielding the same result as above:

```sh
$ gcc hello.c -o hello
```

Note that **ESSTRA Core** does not affect the behavior of the binary.
When you run the generated binary `hello`, you will get the following result:

```sh
$ ./hello
Hello, world!
```

## Verifying Metadata in the Binary

To display metadata embedded in the binary file `hello`, type:

```sh
$ esstra show hello
```

You can see a list of directories and files as well as SHA-1 hashes in YAML
format. These files are all involved in the compilation of the file `hello`:

```yaml
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.4.0
  DataFormatVersion: 0.1.0
  InputFileNames:
  - hello.c
SourceFiles:
- Directory: /home/snagao/esstra/samples/hello
  Files:
  - File: hello.c
    SHA1: 4bbee85215cbcb6a4f1625e4851cca19b0d3f6e2
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

The output of the `show` command is in YAML format and includes the following
information about all source files involved in the compilation:

* Absolute path of the source file in the compilation environment
* SHA-1 checksum of the source file

The structure of the output YAML data is as follows, with the information for
each file grouped by directory:

```yaml
Headers:
  ToolName: <esstra_tool_name>
  ToolVersion: <esstra_tool_version>
  DataFormatVersion: <data_format_version>
  InputFileNames:
  - <filename_passed_to_gcc>
     :
     :
  BinaryFile: <path_to_binary_file>
SourceFiles:
- Directory: <directory_name>
  Files:
  - File: <filename>
    SHA1: <sha1_checksum>
  - File: <filename>
    SHA1: <sha1_checksum>
- Directory: <directory name>
  Files:
  - File: <filename>
    SHA1: <sha1_checksum>
  - File: <filename>
    SHA1: <sha1_checksum>
      :
      :
```

The metadata of the binary `hello` includes not only the source code
[`hello.c`](./hello.c) specified at compile time and the explicitly
`#include`'d `stdio.h` from `hello.c`, but also additional header files. This
is because GCC implicitly `#include`'s the header file `stdc-predef.h` and all
the header files recursively `#include`'d from `stdio.h`.

## Adding License Information to Metadata

Here, we have to prepare an SPDX 2.3 tag-value format file that contains the
license information for [`hello.c`](./hello.c). In this case, we will use the
license information file that has already been prepared,
[`SPDX2TV_esstra.spdx`](../output-examples/SPDX2TV_esstra.spdx),
generated using the open-source license analysis tool
[FOSSology](https://github.com/fossology/fossology).
To associate the license information with the metadata in the binary using
**ESSTRA Utility**, execute the following command:

```sh
$ esstra update hello -i ${SPDX_FILE}
* processing 'hello'...
* done.
```

Where `${SPDX_FILE}` is one of the following:

* [`SPDX2TV_esstra_fossology.spdx`](../output-examples/SPDX2TV_esstra_fossology.spdx)
* [`SPDX2TV_esstra_scancode.spdx`](../output-examples/SPDX2TV_esstra_scancode.spdx)

If no errors occur, the process is successful. To display the metadata content
of the binary `hello`, execute the command:

```sh
$ esstra show hello
```

The result will be as follows:

```yaml
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.4.0
  DataFormatVersion: 0.1.0
  InputFileNames:
  - hello.c
  BinaryFile: /home/snagao/esstra/samples/hello/hello
SourceFiles:
- Directory: /home/snagao/esstra/samples/hello
  Files:
  - File: hello.c
    SHA1: 4bbee85215cbcb6a4f1625e4851cca19b0d3f6e2
    LicenseInfo:
    - MIT
- Directory: /usr/include
  Files:
  - File: features-time64.h
    SHA1: 57c3c8093c3af70e5851f6d498600e2f6e24fdeb
     :
```

> [!NOTE]
> The above data will be similar for either of the SPDX reports used.

From the above result, we can see that the file [`hello.c`](./hello.c) has
been tagged with `LicenseInfo`, and the value assigned to it is `MIT`.

Please note that the files
[`SPDX2TV_esstra_fossology.spdx`](../output-examples/SPDX2TV_esstra_fossology.spdx) and [`SPDX2TV_esstra_scancode.spdx`](../output-examples/SPDX2TV_esstra_scancode.spdx) contain only the
license information for the files present in the
[ESSTRA GitHub repository](https://github.com/sony/esstra).
Therefore, in this sample, license information will not be associated with any
files other than [`hello.c`](./hello.c).

You can also prepare an SPDX 2.3 tag-value format file for files other than
[`hello.c`](./hello.c) and provide it to
**ESSTRA Utility** to associate license information with those files.

## Summary

In this sample, we first compiled the source file [`hello.c`](./hello.c) using
**ESSTRA Core** to generate the binary `hello`, and
confirmed that the metadata in `hello` contains information about all files
involved in the compilation.

Then, using a file in SPDX 2.3 tag-value format, we updated the metadata in the
binary `hello` with **ESSTRA Utility**'s feature to associate license information
with the metadata.
