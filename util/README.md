# ESSTRA Utility

The ESSTRA Utility is a Python script for accessing metadata embedded in
binary files by the ESSTRA Core.

## Status of This Version

The ESSTRA Utility is being developed on Ubuntu 22.04 with Python 3.10.12
installed on a x86\_64 PC.

This version of the ESSTRA Utility includes features named `show`, `shrink`,
`update` and `rm` as described below.

Please note that the specifications and features of the ESSTRA Utility, the
data formats and the content of the metadata, as well as the input/output
specifications of each tool are tentative and may change in future versions.

## Prerequisite

Since the ESSTRA Utility depends on the [PyYAML](https://pyyaml.org/)
module to handle YAML data, you may need to install it by typing:

```sh
$ pip install pyyaml
or
$ sudo apt install python3-yaml
```

## How to Install

To install `esstra` in `/usr/local/bin/`, type:

```sh
$ sudo make install
```

Ensure that the environment variable `PATH` includes `/usr/local/bin/`.

## How to Use

The first argument of `esstra` is a *command*, and the second or subsequent
arguments are the arguments for the *command*:

```sh
$ esstra <command> <arg> [<arg>...]
```

Supported commands in this version are as follows:

* `show`: outputs metadata in binary files
* `shrink`: reduces the size of binary files by removing duplication in metadata
* `update`: updates metadata in binary files by specifying additional information about the source files
* `rm`: removes metadata from binary files

## Command "show"

A command line:

```sh
$ esstra show <binary> [<binary>...]
```

outputs metadata embedded in the specified binary files in YAML format.
For example, passing a binary file `hello` built from `hello.c` as in
[Sample "hello"](../samples/hello/) to the command:

```sh
$ esstra show hello
```

would give you an output as follows:

```yaml
#
# BinaryFileName: hello
# BinaryPath: /home/snagao/esstra/samples/hello/hello
#
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.2.0
  DataFormatVersion: 0.1.0
  InputFileNames:
  - hello.c
SourceFiles:
- Directory: /home/snagao/esstra/samples/hello
  Files:
  - File: hello.c
    SHA1: 62592ce351eab2dfb75deb8c01101e07d6fe3c67
- Directory: /usr/include
  Files:
  - File: features-time64.h
    SHA1: 57c3c8093c3af70e5851f6d498600e2f6e24fdeb
  - File: features.h
    SHA1: d8725bb98129d6d70ddcbf010021c2841db783f7
  - File: stdc-predef.h
    SHA1: 2fef05d80514ca0be77efec90bda051cf87d771f
  - File: stdio.h
    SHA1: c7181b48c4194cd122024971527aab4056baf600
          :
        (snip)
          :
```

Please note that the `show` command always displays [**shrunk**](#command-shrink) data even if
the binary file's metadata itself is not shrunk.

As the output of this command is in YAML format, you can parse it with any YAML
processors.
Below is an example of how to use the command
[`yq`](https://mikefarah.gitbook.io/yq) with a pipe to convert the output to JSON:

```sh
$ esstra show hello | yq -oj
{
  "Headers": {
    "ToolName": "ESSTRA Core",
    "ToolVersion": "0.2.0",
    "DataFormatVersion": "0.1.0",
    "InputFileNames": [
      "hello.c"
    ]
  },
  "SourceFiles": [
    {
      "Directory": "/home/snagao/esstra/samples/hello",
      "Files": [
        {
          "File": "hello.c",
          "SHA1": "62592ce351eab2dfb75deb8c01101e07d6fe3c67"
        }
      ],
      "Directory": "/usr/include",
      "Files": [
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

## Command "shrink"

> [!NOTE]
> We are planning to remove this command in future versions by using
> technologies other than the GCC Plugin (possibly by using
> [Linker Plugins](https://sourceware.org/binutils/docs/ld/Plugins.html))
> to automatically remove duplication in metadata without user intervention.

The current version of the ESSTRA Core cannot avoid data duplication, which
especially occurs when a binary file is built from two or more source files.

The `shrink` command is meant to be used in such situations. It reduces the
size of the binary files by removing duplication in the metadata:

```sh
$ esstra shrink <binary> [<binary> ...]
```

For more details, refer to the case study document
[Demo of ESSTRA Usage on OpenSSL Package](../doc/case-study/openssl.md).

### Why duplication?

Here is the answer to the question "Why does duplication occur?"
In short, this arises from constraints of the mechanism of the GCC Plugin.

First, the ESSTRA Core intervenes with GCC as a GCC plugin, gathers information about the source
and header files involved in the current compilation process, and writes information from all
those files into the object file as metadata.

Then, when the linker finally combines the object files into a single binary file, the metadata
in the individual object files is combined "as-is" in the binary file.

However, GCC compiles each source file "independently," even if multiple source files are
specified on the command line. This means that even if multiple source files are compiled to
produce a single binary file, a GCC plugin during the compilation of one source file does not know
the information during compilation of another source file.

In software development, it is very common for a single binary file to be built from multiple
source files, common header files are `#include`'d, and recursively common header files are
`#include`'d. This ultimately results in duplication in metadata in binary files.

To eliminate this duplication, the ESSTRA utility provides a `shrink` command. The command
minimizes the size of binary files by removing duplication in the metadata and leaving only the
necessary data.

## Command "update"

The `update` command in the current version attaches "license information" to
each file's information in the binary files' metadata.

We believe that other kinds of information could also be helpful, such as
copyright information, CVE numbers and so on.
Since ESSTRA is at an early stage in development, we have developed a feature
that attaches license information as a sort of feasibility study.

To attach license information, you need to prepare an
[SPDX 2.3 tag-value](https://spdx.github.io/spdx-spec/v2.3/) file
including `LicenseInfoInFile:` tags.
Some license scanners like [FOSSology](https://fossology.github.io/) can
generate such files.

A typical usage is:

```sh
$ esstra update <binary> -i <spdx-tv-file>
```

If you want to update two or binary files with two or more license information
files at once, you can specify them all on the command line:

```sh
$ esstra update <binary> [<binary> ...] -i <spdx-tv-file> [<spdx-tv-file> ..]
```

For more details on the `update` command, please refer to the document
[Sample "hello2"](../samples/hello2/README.md).

## Command "rm"

The `rm` command completely removes metadata embedded in binary files by
the ESSTRA Core during compilation:

```sh
$ esstra rm <binary> [<binary> ...]
```

When a binary file with metadata removed is specified for the ESSTRA Utility, an
error occurs as shown below:

```sh
$ esstra rm hello
* processing 'hello'...
* done.
$ esstra show hello
#
# BinaryFileName: hello
#
Exception: RuntimeError("section not found: .'esstra")
```

## License

See the [LICENSE](../LICENSE) file.
