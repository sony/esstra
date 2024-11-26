# Sample 1

This sample compiles two source files, `hello_main.c` and `hello_sub.c`, to
generate a binary file, `hello`.

Metadata is embedded in the binary file, `hello`, by applying ESSTRA Core during
compilation.

## How to build

If you have [ESSTRA Core](../../core/README.md) installed on your system, type:

```sh
$ make
```

in this directory.

Or, if you want to use `esstracore.so` which is not installed on the system
but has been compiled in [../../core/](../../core), type:

```sh
$ make ESSTRACORE=../../core/esstracore.so
```

Then the source files are compiled with ESSTRA Core applied and a binary file
`hello` is generated.
Running `hello` just displays a string `Hello, World!` on the standard output:

```sh
$ ./hello
Hello, World!
```

For reference, a prebuilt binary file `hello` is placed in the sub directory
[`output_example`](./output_example), which was built on our development environment mentioned in
the [README.md](../../README.md#status-of-this-version) file at the top directory.

## How to Display Metadata

Because the binary file `hello` is the result of compilation ESSTRA Core applied,
the file has metadata embedded by ESSTRA Core.

To verify this, use the ESSTRA Utility as shown below:

```sh
$ esstra.py show hello
```

Then the content of the metadata embedded in `hello` is displayed in YAML format:

```yaml
#
# BinaryFileName: hello
# BinaryPath: /home/snagao/esstra/samples/sample1/hello
#
---
- InputFileName: hello_main.c
  SourceFiles:
  - SourcePath: /home/snagao/esstra/samples/sample1/hello_main.c
  - SourcePath: /usr/include/stdc-predef.h
  - SourcePath: /home/snagao/esstra/samples/sample1/hello_sub.h
- InputFileName: hello_sub.c
  SourceFiles:
  - SourcePath: /home/snagao/esstra/samples/sample1/hello_sub.c
  - SourcePath: /usr/include/stdc-predef.h
  - SourcePath: /usr/include/stdio.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/libc-header-start.h
  - SourcePath: /usr/include/features.h
  - SourcePath: /usr/include/features-time64.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/wordsize.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/timesize.h
  - SourcePath: /usr/include/x86_64-linux-gnu/sys/cdefs.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/long-double.h
  - SourcePath: /usr/include/x86_64-linux-gnu/gnu/stubs.h
  - SourcePath: /usr/include/x86_64-linux-gnu/gnu/stubs-64.h
  - SourcePath: /usr/lib/gcc/x86_64-linux-gnu/11/include/stddef.h
  - SourcePath: /usr/lib/gcc/x86_64-linux-gnu/11/include/stdarg.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/types.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/typesizes.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/time64.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/types/__fpos_t.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/types/__mbstate_t.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/types/__fpos64_t.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/types/__FILE.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/types/FILE.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/stdio_lim.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/floatn.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/floatn-common.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/stdio.h
  - SourcePath: /usr/include/x86_64-linux-gnu/bits/stdio2.h
```
