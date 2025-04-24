# Sample "hello"

This sample explains how to use ESSTRA with a simple C source code. The
document is structured as a step-by-step guide, allowing you to easily
understand the basic operations of ESSTRA by following each step in sequence.

First, in this sample, we will compile [`hello.c`](./hello.c), which is
provided in this directory, using the [ESSTRA Core](/core/README.md) to
generate the binary file `hello`. This binary has metadata embedded that
contains information about all source files involved in the compilation, such
as absolute paths and checksums. We will verify this using the
[ESSTRA Utility](/util/README.md).

Next, we will demonstrate how to use the
[ESSTRA Utility](/util/README.md)'s feature that adds
license information of source files to the metadata.
In this sample, we will use a prepared license information file
[`SPDX2TV_esstra.spdx`](../output-examples/SPDX2TV_esstra.spdx).
Using this information, we will update the metadata with the ESSTRA
Utility and verify that the license information has been correctly associated
with the metadata.

The license information file
[`SPDX2TV_esstra.spdx`](../output-examples/SPDX2TV_esstra.spdx)
was generated using the open-source license analysis tool
[FOSSology](https://github.com/fossology/fossology).
If you are interested in how to use FOSSology, please refer to the document
[License Analysis Using FOSSology](./README_FOSSOLOGY.md).

## Building and Installing ESSTRA

First, build and install ESSTRA on your system. In the top directory, enter:

```sh
$ make
```

If there are no errors, the build is complete. Then, enter:

```sh
$ sudo make install
```

This will install the [ESSTRA Core](/core/README.md) and the
[ESSTRA Utility](/util/README.md) on your system.

## Source Code to Compile

In this sample, we will compile the source code [`hello.c`](./hello.c) using
the ESSTRA Core. The content of the code is as follows, and it is a very simple
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
the binary `hello`. By involving the [ESSTRA Core](../../core/README.md)
during compilation, metadata will be embedded into `hello`.

```sh
$ gcc -fplugin=/usr/local/share/esstra/esstracore.so hello.c -o hello
```

If you have already [installed the Spec File](../../README.md),
the ESSTRA Core will intervene in
the compilation without needing the `-fplugin=` option, yielding the same
result as above:

```sh
$ gcc hello.c -o hello
```

Note that the [ESSTRA Core](../../core/README.md) does not affect the behavior
of the binary. When you run the generated binary `hello`, you will get the
following result:

```sh
$ ./hello
Hello, world!
```

## Verifying Metadata in the Binary

To display metadata embedded in the binary file `hello`, type:

```sh
$ esstar.py show hello
```

You can see a list of directories and files as well as SHA-1 hashes in YAML
format. These files are all involved in the compilation of the file `hello`:

```yaml
#
# BinaryFileName: output_example/hello
# BinaryPath: /home/snagao/esstra/samples/sample-hello/output_example/hello
#
---
SourceFiles:
  /home/snagao/esstra/samples/sample-hello:
  - File: hello.c
    SHA1: 62592ce351eab2dfb75deb8c01101e07d6fe3c67
  /usr/include:
  - File: features-time64.h
    SHA1: 57c3c8093c3af70e5851f6d498600e2f6e24fdeb
  - File: features.h
    SHA1: d8725bb98129d6d70ddcbf010021c2841db783f7
  - File: stdc-predef.h
    SHA1: 2fef05d80514ca0be77efec90bda051cf87d771f
  - File: stdio.h
    SHA1: c7181b48c4194cd122024971527aab4056baf600
  /usr/include/x86_64-linux-gnu/bits:
  - File: typesizes.h
    SHA1: ee94b5a60d007c23bdda9e5c46c8ba40f4eb402c
  - File: wordsize.h
    SHA1: 281ddd3c93f1e8653e809a45b606574c9b691092
  /usr/include/x86_64-linux-gnu/bits/types:
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
  /usr/include/x86_64-linux-gnu/gnu:
  - File: stubs-64.h
    SHA1: f7603fa3908b56e9d1b33c91590db3252e13a799
  - File: stubs.h
    SHA1: be168037b7503a82b1cf694cdbac8c063bb6e476
  /usr/include/x86_64-linux-gnu/sys:
  - File: cdefs.h
    SHA1: a419a6372029d89ba38ada0811d34f51df8d09b7
  /usr/lib/gcc/x86_64-linux-gnu/11/include:
  - File: stdarg.h
    SHA1: fa23f49da8a0a5068b781dff7182f1a1c363dc30
  - File: stddef.h
    SHA1: 0de70008ffa3f198baf55c7b3f3d03b4ca11c21f
```

The output of the `show` command is in YAML format and includes the following
information about all source files involved in the compilation:

* Absolute path of the source file in the compilation environment
* SHA-1 checksum of the source file

The structure of the output YAML data is as follows, with the information for each file grouped by directory:

```yaml
#
# BinaryFileName: <specified_binary_name>
# BinaryPath: <absolute_path_of_the_specified_binary>
#
SourceFiles:
  <directory_name>:
  - File: <filename>
    SHA1: <SHA1_checksum>
  - File: <filename>
    SHA1: <SHA1_checksum>
  <directory name>:
  - File: <filename>
    SHA1: <SHA1_checksum>
  - File: <filename>
    SHA1: <SHA1_checksum>
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
To associate the license information with the metadata in the binary using the
[ESSTRA Utility](/util/README.md), execute the following command:

```sh
$ esstra.py update hello -i SPDX2TV_esstra.spdx
* processing 'hello'...
* done.
```

If no errors occur, the process is successful. To display the metadata content
of the binary `hello`, execute the command:

```sh
$ esstra.py show hello
```

The result will be as follows:

```yaml
#
# BinaryFileName: hello
# BinaryPath: /home/snagao/esstra/samples/hello/hello
#
SourceFiles:
  /home/snagao/esstra/samples/hello:
  - File: hello.c
    SHA1: e7834d0b9cb6cb116c72f0bee7da29e3d280b27e
    LicenseInfo:
    - MIT
  /usr/include:
  - File: features-time64.h

       :

```

From the above result, we can see that the file [`hello.c`](./hello.c) has
been tagged with `LicenseInfo`, and the value assigned to it is `MIT`.

Please note that the file
[`SPDX2TV_esstra.spdx`](../output-examples/SPDX2TV_esstra.spdx) only contains
license information for the files present in the
[ESSTRA GitHub repository](https://github.com/sony/esstra).
Therefore, in this sample, license information will not be associated with any
files other than [`hello.c`](./hello.c).

You can also prepare an SPDX 2.3 tag-value format file for files other than
[`hello.c`](./hello.c) and provide it to the
[ESSTRA Utility](/util/README.md) to associate
license information with those files.

## Summary

In this sample, we first compiled the source file [`hello.c`](./hello.c) using
the [ESSTRA Core](../../core/README.md) to generate the binary `hello`, and
confirmed that the metadata in `hello` contains information about all files
involved in the compilation.

Then, using a file in SPDX 2.3 tag-value format, we updated the metadata in the
binary `hello` with the [ESSTRA Utility](/util/README.md)'s feature to
associate license information with the metadata.
