# ESSTRA Utility

ESSTRA Utility is a Python script for accessing metadata
in binary files embedded by ESSTRA Core.

## Status of This Version

ESSTRA Utility is being developed on Ubuntu 22.04 with Python 3.10.12
installed on a x86\_64 PC.

In this version, ESSTRA Utility has a feature to display contents of metadata
embedded by [ESSTRA Core](../core/README.md) in binary files in YAML format.

Note that the data formats and content of the metadata, as well as the
input/output specifications of each tool, are tentative and may change in the
future.

## How to Install

To install `esstra.py` in `/usr/local/bin/`, type:

```sh
$ sudo make install
```

Make sure that the environment variable `PATH` contains `/usr/local/bin/`.

## How to Use

The first argument of `esstra.py` is a *command*, and the second or subsequent
arguments are the arguments of *command*.

The supported command in this version is `show`, which displays metadata in
binary files  , passed as the second and subsequent arguments in YAML format.

This command outputs contents of metadata embedded in the binary files in YAML
format by passing binary files built with ESSTRA Core as arguments.

Sample output is as follows:

```sh
$ esstra.py show helloworld
---
File: helloworld
Information:
- InputFileName: helloworld.c
- SourcePath: /home/snagao/esstra-test/helloworld.c
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
```

## License

See the [LICENSE](../LICENSE) file.
