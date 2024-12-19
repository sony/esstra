# Sample "hello-main-sub"

This sample compiles two source files, `hello_main.c` and `hello_sub.c`, to
generate a binary file, `hello`.

Metadata is embedded in the binary file, `hello`, by applying ESSTRA Core during
compilation.

This is very similar to another example [sample-hello](../sample-hello),
but in this case, we use two source files.

## Build

If you have [ESSTRA Core](../../core) installed on your system, type:

```sh
$ make
```

in this directory.
Or, if you want to use `esstracore.so` which is not installed on the system
but has been compiled in [../../core](../../core), type:

```sh
$ make ESSTRACORE=../../core/esstracore.so
```

Then the source files are compiled with ESSTRA Core applied and a binary file
`hello` is generated.

Running `hello` just displays a string `Hello, world!` on the standard output:

```sh
$ ./hello
Hello, world!
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
  - File: hello_main.c
    SHA1: 3bc2c234c171866b43a7d23d706eadd302477c21
  - File: hello_sub.h
    SHA1: d2374a9eba83aed3870b875deed71ef6846de0c8
  /usr/include:
  - File: stdc-predef.h
    SHA1: 2fef05d80514ca0be77efec90bda051cf87d771f
---
SourceFiles:
  /home/snagao/esstra/samples/sample-hello:
  - File: hello_sub.c
    SHA1: c8da467e6ea905483912de8865f3aa7a8919a40f
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

## Minimize Metadata

You can see that the file `stdc-predef.h` twice in the output above.

This is because ESSTRA Core, a GCC Plugin, can only get information about the
status and information about a source file currently being compiled.

In this example, we compile two source files, one is `hello_main.c` and the
other is `hello_sub.c`.  GCC compiles each file independently even if you
specify both files on the command line.

So, there may be duplication of the files stored in the metadata in the
resulting binary file.

To eliminate such duplication, type:

```sh
$ esstra.py shrink hello
```

Then, the metadata in `hello` is minimized.
To confirm it, run `show` again:

```yaml
$ esstra.py shrink hello
#
# BinaryFileName: hello
# BinaryPath: /home/snagao/esstra/samples/sample-hello/hello
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

For more details about the duplication in metadata, refer to the file
[README.md of ESSTRA Utility](../../util/README.md#command-shrink).

## Prebuilt Files

For reference, a prebuilt binary file `hello` is placed in the sub directory
[`output_example`](./output_example), which was built on our development environment mentioned in
the [README.md](../../README.md#status-of-this-version) file in the top directory.
