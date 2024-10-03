# Sample 1

This sample compiles two source files, `hello_main.c` and `hello_sub.c`, to
generate a binary file, `hello`.

Metadata is embedded in the binary file, `hello`, by applying ESSTRA Core during
compilation.

## How to build

In this directory, type:

```sh
$ make
```

Then the source files are compiled with ESSTRA Core applied and a binary file
`hello` is generated.
Running `hello` just displays a string `Hello, World!` on the standard output:

```sh
$ ./hello
Hello, World!
```

## How to Display Metadata

Because the binary file `hello` is the result of compilation ESSTRA Core applied,
the file has metadata embedded by ESSTRA Core.

To verify this, use the ESSTRA Utility as shown below:

```sh
$ esstra.py show hello
```

Then the content of the metadata embedded in `hello` is displayed in YAML format.

```
$ esstra.py show hello
---
File: hello
Information:
- <hello_main.c>
- /home/snagao/esstra/samples/sample1/hello_main.c
- /usr/include/stdc-predef.h
- /home/snagao/esstra/samples/sample1/hello_sub.h
- <hello_sub.c>
- /home/snagao/esstra/samples/sample1/hello_sub.c
- /usr/include/stdc-predef.h
- /usr/include/stdio.h
- /usr/include/x86_64-linux-gnu/bits/libc-header-start.h
- /usr/include/features.h
- /usr/include/features-time64.h
- /usr/include/x86_64-linux-gnu/bits/wordsize.h
- /usr/include/x86_64-linux-gnu/bits/timesize.h
- /usr/include/x86_64-linux-gnu/sys/cdefs.h
- /usr/include/x86_64-linux-gnu/bits/long-double.h
- /usr/include/x86_64-linux-gnu/gnu/stubs.h
- /usr/include/x86_64-linux-gnu/gnu/stubs-64.h
- /usr/lib/gcc/x86_64-linux-gnu/11/include/stddef.h
- /usr/lib/gcc/x86_64-linux-gnu/11/include/stdarg.h
- /usr/include/x86_64-linux-gnu/bits/types.h
- /usr/include/x86_64-linux-gnu/bits/typesizes.h
- /usr/include/x86_64-linux-gnu/bits/time64.h
- /usr/include/x86_64-linux-gnu/bits/types/__fpos_t.h
- /usr/include/x86_64-linux-gnu/bits/types/__mbstate_t.h
- /usr/include/x86_64-linux-gnu/bits/types/__fpos64_t.h
- /usr/include/x86_64-linux-gnu/bits/types/__FILE.h
- /usr/include/x86_64-linux-gnu/bits/types/FILE.h
- /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h
- /usr/include/x86_64-linux-gnu/bits/stdio_lim.h
- /usr/include/x86_64-linux-gnu/bits/floatn.h
- /usr/include/x86_64-linux-gnu/bits/floatn-common.h
- /usr/include/x86_64-linux-gnu/bits/stdio.h
- /usr/include/x86_64-linux-gnu/bits/stdio2.h
```
