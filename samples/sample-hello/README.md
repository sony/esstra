# Sample "hello"

This is a primary and very simple example. Just compiles `hello.c` and generate
a binary file `hello`.

Metadata is embedded in the binary file `hello` by applying ESSTRA Core during
compilation.

## Build

If you have [ESSTRA Core](../../core/README.md) installed on your system, type:

```sh
$ make
```

in this directory.
Or, if you want to use `esstracore.so` in [../../core/](../../core) without
installing it, type:

```sh
$ make ESSTRACORE=../../core/esstracore.so
```

Then the source file is compiled with ESSTRA Core applied and a binary file
`hello` is generated.

Running `hello` just displays a string `Hello, world!` on the standard output:

```sh
$ ./hello
Hello, World!
```

## Display Metadata

Since the binary file `hello` is the result of compilation ESSTRA Core applied,
the file has metadata embedded by ESSTRA Core.

To verify this, use the ESSTRA Utility as shown below:

```sh
$ esstra.py show hello
```

Then the content of the metadata embedded in `hello` is displayed in YAML format:

```yaml
#
# BinaryFileName: hello
# BinaryPath: /home/snagao/esstra/samples/sample-hello/hello
#
---
SourceFiles:
  /home/snagao/esstra/samples/sample-hello:
  - FileName: hello.c
    SHA1: 62592ce351eab2dfb75deb8c01101e07d6fe3c67
  /usr/include:
  - FileName: features-time64.h
    SHA1: 57c3c8093c3af70e5851f6d498600e2f6e24fdeb
  - FileName: features.h
    SHA1: d8725bb98129d6d70ddcbf010021c2841db783f7
  - FileName: stdc-predef.h
    SHA1: 2fef05d80514ca0be77efec90bda051cf87d771f
  - FileName: stdio.h
    SHA1: c7181b48c4194cd122024971527aab4056baf600
  /usr/include/x86_64-linux-gnu/bits:
  - FileName: typesizes.h
    SHA1: ee94b5a60d007c23bdda9e5c46c8ba40f4eb402c
  - FileName: wordsize.h
    SHA1: 281ddd3c93f1e8653e809a45b606574c9b691092
  /usr/include/x86_64-linux-gnu/bits/types:
  - FileName: FILE.h
    SHA1: 497924e329d53517631713ae52acb73e870d7d65
  - FileName: __FILE.h
    SHA1: 274242343e85d1c06e7f5ccc5abf15e120f6e957
  - FileName: __fpos64_t.h
    SHA1: ac38e294b004f6e2bf18f1c55e03dc80f48d6830
  - FileName: __fpos_t.h
    SHA1: 760ef77769ac1921f4b1f908cbf06863e2506775
  - FileName: __mbstate_t.h
    SHA1: e3a4f2ee55e635520db0b4610d2b361e9ce41de7
  - FileName: struct_FILE.h
    SHA1: 1dbf8bac589cb09e09aa4c1d36913e549a57bcf0
  /usr/include/x86_64-linux-gnu/gnu:
  - FileName: stubs-64.h
    SHA1: f7603fa3908b56e9d1b33c91590db3252e13a799
  - FileName: stubs.h
    SHA1: be168037b7503a82b1cf694cdbac8c063bb6e476
  /usr/include/x86_64-linux-gnu/sys:
  - FileName: cdefs.h
    SHA1: a419a6372029d89ba38ada0811d34f51df8d09b7
  /usr/lib/gcc/x86_64-linux-gnu/11/include:
  - FileName: stdarg.h
    SHA1: fa23f49da8a0a5068b781dff7182f1a1c363dc30
  - FileName: stddef.h
    SHA1: 0de70008ffa3f198baf55c7b3f3d03b4ca11c21f
```

## Prebuilt Files

For reference, a prebuilt binary file `hello` is placed in the sub directory
[`output_example`](./output_example), which was built on our development environment mentioned in
the [README.md](../../README.md#status-of-this-version) file at the top directory.
