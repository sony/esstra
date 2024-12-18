# ESSTRA Utility

ESSTRA Utility is a Python script for accessing metadata
in binary files embedded by ESSTRA Core.

## Status of This Version

ESSTRA Utility is being developed on Ubuntu 22.04 with Python 3.10.12
installed on a x86\_64 PC.

This version of the ESSTRA Utility has features named `show`, `update` and
`shrink` as described below.

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
* `update`: update metadata in binary files by specifying additional information of the source files
* `shrink`: reduce sizes of binary files by removing duplication in metadata

### Command "show"

A command line:

```sh
$ esstra.py show <binary> [<binary>...]
```

outputs metadata embedded in specified binary files in YAML format.
For example, a binary file `helloworld` built from `helloworld.c`:

```sh
$ esstra.py show helloworld
````

would give you an output as follows:

```yaml
#
# BinaryFileName: helloworld
# BinaryPath: /home/snagao/esstra-test/helloworld
#
---
InputFileName: helloworld.c
SourceFiles:
  /home/snagao/esstra-test:
  - FileName: helloworld.c
    SHA1: 8a4090e4471481310808c664efc73b5b2ae6112c
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
  - FileName: floatn-common.h
    SHA1: 3f37104123a2e6180621331c1da87125808e47bd
          :
        (snip)
          :
```

As the output of this command is in YAML format, you can parse it with any YAML
processors.
Below is an example of how to use the command
[`yq`](https://mikefarah.gitbook.io/yq) with a pipe to convert the output to JSON:

```sh
$ esstra.py show helloworld | yq -oj
{
  "InputFileName": "helloworld.c",
  "SourceFiles": {
    "/home/snagao/esstra-test": [
      {
        "FileName": "helloworld.c",
        "SHA1": "8a4090e4471481310808c664efc73b5b2ae6112c"
      }
    ],
    "/usr/include": [
      {
        "FileName": "features-time64.h",
        "SHA1": "57c3c8093c3af70e5851f6d498600e2f6e24fdeb"
      },
      {
        "FileName": "features.h",
        "SHA1": "d8725bb98129d6d70ddcbf010021c2841db783f7"
      },
      {
        "FileName": "stdc-predef.h",
        "SHA1": "2fef05d80514ca0be77efec90bda051cf87d771f"
      },
      {
        "FileName": "stdio.h",
        "SHA1": "c7181b48c4194cd122024971527aab4056baf600"
      }
    ],
    "/usr/include/x86_64-linux-gnu/bits": [
      {
        "FileName": "typesizes.h",
        "SHA1": "ee94b5a60d007c23bdda9e5c46c8ba40f4eb402c"
      },
          :
        (snip)
          :
```

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

The directory [../samples/sample-util-linux](../samples/sample-util-linux)
contains [an overall guide](../samples/sample-util-linux/README.md) to compile
[util-linux](https://github.com/util-linux/util-linux) with ESSTRA Core
applied.

In the document, we build util-linux with ESSTRA Core applied, perform license
scan with [FOSSology](https://fossology.github.io/) to generate an SPDX
tag-value file containing license information, attach the information to binary
files of util-linux by using ESSTRA Utility, and show the result of it.

So, for more details of the command `update`, please refer to
[the document](../samples/sample-util-linux/README.md).

### Command "shrink"

The `shrink` command reduces the size of binary files built with ESTTRA Core by removing
duplication in the metadata.

Here is the answer to the question "Why duplication occurs." In short, this arises from
constraints of the GCC Plugin mechanism.

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

In future versions of ESSTRA, we plan to use technologies other than GCC Plugin (possibly using
[Linker Plugins](https://sourceware.org/binutils/docs/ld/Plugins.html)) to automatically remove
duplication in metadata without user intervention such as the `shrink` command.

## License

See the [LICENSE](../LICENSE) file.
