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

We think some other kinds of information would also be helpful.  For example,
copyright information, CVE numbers of fixed vulnerabilities, and so on.
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

In that document, we perform license scan with FOSSology to generate an SPDX
tag-value file, attach license information to binary files of util-linux by
using ESSTRA Utility, and show the result of it.

So, for more details of the command `update`, please refer to
[the document](../samples/sample-util-linux/README.md).

### Command "shrink"

The current version of ESSTRA is making use of the mechanism of
[GCC Plugin](https://gcc.gnu.org/wiki/plugins).
This can easily cause the size of the resulting binary files' metadata very large.

The reason is ... (write it later)




## License

See the [LICENSE](../LICENSE) file.
