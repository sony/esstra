# ESSTRA Utility

ESSTRA Utility is a Python script for accessing metadata
in binary files embedded by ESSTRA Core.

## Status of This Version

ESSTRA Utility is being developed on Ubuntu 22.04 with Python 3.10.12
installed on a x86\_64 PC.

This version of the ESSTRA Utility has features named `show`, `shrink` and
`update` as described below.

Note that the specifications and features of ESSTRA Utility, the data formats
and content of the metadata, as well as the input/output specifications of each
tool are tentative and may change in the future versions.

## Prerequisite

Since ESSTRA Utility depends on the [PyYAML](https://pyyaml.org/)
module to handle YAML data, you may need to install it by, for example, typing:

```sh
$ pip install pyyaml
or
$ sudo apt install python3-yaml
```

## How to Install

To install `esstra.py` in `/usr/local/bin/`, type:

```sh
$ sudo make install
```

Make sure that the environment variable `PATH` contains `/usr/local/bin/`.

## How to Use

The first argument of `esstra.py` is a *command*, and the second or subsequent
arguments are the arguments of *command*:

```sh
$ esstra.py <command> <arg> [<arg>...]
```

Supported commands in this version are as follows:

* `show`: outputs metadata in binary files
* `shrink`: reduce sizes of binary files by removing duplication in metadata
* `update`: update metadata in binary files by specifying additional information of the source files

### Command "show"

A command line:

```sh
$ esstra.py show <binary> [<binary>...]
```

outputs metadata embedded in specified binary files in YAML format.
For example, a binary file `hello` built from `hello.c` as in
[../samples/sample-hello](../samples/sample-hello),

```sh
$ esstra.py show hello
````

would give you an output as follows:

```yaml
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

As the output of this command is in YAML format, you can parse it with any YAML
processors.
Below is an example of how to use the command
[`yq`](https://mikefarah.gitbook.io/yq) with a pipe to convert the output to JSON:

```sh
$ esstra.py show hello | yq -oj
{
  "SourceFiles": {
    "/home/snagao/esstra/samples/sample-hello": [
      {
        "File": "hello.c",
        "SHA1": "62592ce351eab2dfb75deb8c01101e07d6fe3c67"
      }
    ],
    "/usr/include": [
      {
        "File": "features-time64.h",
        "SHA1": "57c3c8093c3af70e5851f6d498600e2f6e24fdeb"
      },
      {
        "File": "features.h",
        "SHA1": "d8725bb98129d6d70ddcbf010021c2841db783f7"
      },
      {
        "File": "stdc-predef.h",
        "SHA1": "2fef05d80514ca0be77efec90bda051cf87d771f"
      },
          :
        (snip)
          :
```

### Command "shrink"

The current version of ESSTRA Core cannot avoid data duplication which
especially occurs when a binary file is built from two or more source files.

The command `shrink` is meant to be used in such situation. It reduces the size
of binary files by removing duplication in the metadata.

```sh
$ esstra.py shrink <binary> [<binary> ...]
```

More detailed examples are stored in the directories
[../samples/sample-hello](../samples/sample-hello) and
[../samples/sample-util-linux](../samples/sample-util-linux).

Here is the answer to the question "Why does duplication occur?"
In short, this arises from constraints of the mechanism of GCC Plugin.

First, ESTTRA Core intervenes with GCC as a GCC plugin, gathers information about the source
and header files involved in the current compilation process, and writes information from all
those files into the object file as metadata.

Then, when the linker finally combines the object files into a single binary file, the metadata
in the individual object files is combined "as-is" in the binary file.

However, GCC compiles each source file "independently," even if multiple source files are
specified on the command line. This means that even if multiple source files are compiled to
produce a single binary file, a GCC plugin during compilation of one source file does not know
the information during compilation of another source file.

In software development, it is very common for a single binary file to be built from multiple
source files, common header files are `#include`'d, and recursively common header files are
`#include`'d. This ultimately results in duplication in metadata in binary files.

To eliminate this duplication, ESSTRA utility provides a `shrink` command. The command
minimizes the size of binary files by removing duplication in the metadata and leaving only the
necessary data.

In the future versions of ESSTRA, we plan to use technologies other than GCC Plugin (possibly using
[Linker Plugins](https://sourceware.org/binutils/docs/ld/Plugins.html)) to automatically remove
duplication in metadata without user intervention such as the `shrink` command.

### Command "update"

The command `update` of the current version attaches "license information" to
each file's information in binary files' metadata.

We think some other kinds of information would also be helpful.
For example, copyright information, CVE numbers and so on.
Since ESSTRA is at an early stage in development, we have developed a feature
that attaches license information as a sort of feasibility study.

To attach license information, you need to prepare an
[SPDX 2.3 tag-value](https://spdx.github.io/spdx-spec/v2.3/) file
including `LicenseInfoInFile:` tags.
Some license scanners like [FOSSology](https://fossology.github.io/) can
generate such kind of files.

A typical usage is:

```sh
$ esstra.py update <binary> -i <spdx-tv-file>
```

If you want to update two or binary files with two or more license information
files at once, you can specify them all on the command line:

```sh
$ esstra.py update <binary> [<binary> ...] -i <spdx-tv-file> [<spdx-tv-file> ..]
```

The example [../samples/sample-util-linux](../samples/sample-util-linux)
gives you an overall guide to compile
[util-linux](https://github.com/util-linux/util-linux/) with the ESSTRA system.

In the document, we build util-linux with ESSTRA Core applied, perform license
scan with [FOSSology](https://fossology.github.io/) to generate an SPDX
tag-value file containing license information, attach the information to binary
files of util-linux by using ESSTRA Utility, and show the result of it.

So, for more details of the command `update`, please refer to
[the document](../samples/sample-util-linux/README.md).

## License

See the [LICENSE](../LICENSE) file.
