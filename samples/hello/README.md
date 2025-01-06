# Sample "hello"

This is a primary and very simple example. Just compiles `hello.c` and generate
a binary file `hello`.

This document gives you an overall guide:

* To compile a source file with ESSTRA Core applied to build a binary file with
  metadata embedded,
* To update license information in the metadata with an SPDX tag-value file
  generated with FOSSology,

and finally,

* To confirm that the license information is surely applied to the metadata in
  the binary file.

## Notice

Each source file in this directory has an `SPDX-License-Identifier:` with some
license ID, however, it's just for feasibility of this guide.

Though this directory contains a `Makefile`, we will explain what to do one by
one precisely without using the `Makefile`.

## Preparation

Before you begin this guide,
install ESSTRA Core and ESSTRA Utility on your system by following
[How to Build and Install](../../README.md#how-to-build-and-install).

## Build with ESSTRA Core

The file `hello.c` is a very simple C source file:

```c
#include <stdio.h>

int main(void)
{
    printf("Hello, world!\n");
    return 0;
}
```

To compile `hello.c` with ESSTRA Core applied and generate a binary file named
`hello`, type:

```sh
$ gcc -fplugin=/usr/local/share/esstra/esstracore.so hello.c -o hello
```

on the command line. If no errors, the file `hello` is generated.

Executing `hello` just displays a string `Hello, world!` on the standard output:

```sh
$ ./hello
Hello, world!
```

Note that compilation with ESSTRA Core applied does not affect the behavior of
the resulting binary file at all.

## Check What's Embedded

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

## Generate SPDX File with FOSSology

One of the features of ESSTRA is to attach license information to metadata by
the ESTTRA Utility's command `update` as mentioned
[here](../../util/README.md#command-update).


## Prebuilt Files

For reference, a prebuilt binary file `hello` is placed in the sub directory
[`output_example`](./output_example), which was built on our development environment mentioned in
the [README.md](../../README.md#status-of-this-version) file in the top directory.
