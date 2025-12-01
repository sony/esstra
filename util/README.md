# ESSTRA Utility

**ESSTRA Utility** is a Python script for accessing metadata embedded in binary files by
**ESSTRA Core**.

This version of **ESSTRA Utility** includes features named `show`, `rm`, `update` and `shrink`
as described below.

> [!NOTE]
> The current version of **ESSTRA** is under active development.
> Please be aware that the metadata format and content, as well as the specifications and
> functionality of each tool, are provisional and subject to change.

## How to Use

See the following sections in the [README.md](/README.md) file in the top-level directory for a
quick overview of how to use the tool:

* [How to Build and Install](/README.md#how-to-build-and-install)
* [Accessing Metadata](/README.md#accessing-metadata)

## Commands

The first argument of `esstra` is a *command*, and the second or subsequent arguments are the
arguments for the *command*:

```sh
$ esstra <command> <arg> [<arg>...]
```

Supported commands in this version are as follows:

* `show`: outputs metadata in binary files
* `rm`: removes metadata from binary files
* `update`: updates metadata in binary files by specifying additional information about the source files
* `shrink`: reduces the size of binary files by removing duplication in metadata

### Command "show"

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
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.4.0
  DataFormatVersion: 0.1.0
  InputFileNames:
  - hello.c
SourceFiles:
- Directory: .
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
          :
        (snip)
          :
```

As the output of this command is in YAML format, you can parse it with any YAML
processors.
Below is an example of how to use the command
[`yq`](https://mikefarah.gitbook.io/yq) with a pipe to convert the output to JSON:

```sh
$ esstra show hello | yq -oj
{
  "Headers": {
    "ToolName": "ESSTRA Core",
    "ToolVersion": "0.4.0",
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

Please note that the `show` command always displays [**shrunk**](#command-shrink) data even if
the binary file's metadata itself is not shrunk.

### Command "rm"

The `rm` command completely removes metadata embedded in binary files by
**ESSTRA Core** during compilation:

```sh
$ esstra rm <binary> [<binary> ...]
```

When a binary file with metadata removed is specified for **ESSTRA Utility**, an
error occurs as shown below:

```sh
$ esstra rm hello
* processing 'hello'...
* done.
$ esstra show hello
Exception: RuntimeError("section not found: .'esstra")
```

### Command "update"

The `update` command in the current version attaches "license information" to
each file's information in the binary files' metadata.

We believe that other kinds of information could also be helpful, such as
copyright information, CVE numbers and so on.
Since ESSTRA is at an early stage in development, we have developed a feature
that attaches license information as a sort of feasibility study.

To attach license information, you need to prepare an
SPDX tag-value file with a minimum version of [SPDX 2.2](https://spdx.github.io/spdx-spec/v2.2.2/) file
including `LicenseInfoInFile:` tags.
Some license scanners like [FOSSology](https://fossology.github.io/) and [ScanCode toolkit](https://github.com/aboutcode-org/scancode-toolkit) can generate such files.

A typical usage is:

```sh
$ esstra update <binary> -i <spdx-tv-file>
```

If you want to update two or binary files with two or more license information
files at once, you can specify them all on the command line:

```sh
$ esstra update <binary> [<binary> ...] -i <spdx-tv-file> [<spdx-tv-file> ..]
```

When multiple SPDX tag-value files are provided, or when license information is already
embedded in the binary metadata, all license data for each file will be **appended** in a
deduplicated manner.  For example, if the binary metadata specifies that the file:

* `/home/snagao/esstra/samples/hello2/hello_main.c`

is licensed under:

* `MIT`

and the SPDX tag-value file assigns the same file the license:

* `BSD-3-Clause`

then the resulting license information for that file will be:

* `[MIT, BSD-3-Clause]`

For more details on the `update` command, please refer to the document
[Sample "hello2"](../samples/hello2/README.md).

### Command "shrink"

> [!NOTE]
> This command is intended to be invoked by [**ESSTRA Link**](../link/README.md).

**ESSTRA Core** cannot avoid data duplication, which especially occurs when a binary file
is built from two or more source files.

The `shrink` command is meant to be used in such situations. It reduces the size of the binary
files by removing duplication in the metadata:

```sh
$ esstra shrink <binary> [<binary> ...]
```

For more details, refer to the case study document
[Demo of ESSTRA Usage on OpenSSL Package](../doc/case-study/openssl.md).

#### Why Duplication Occurs

Duplication occurs due to limitations in how GCC plugins work.

**ESSTRA Core** operates as a GCC plugin, collecting metadata from source and header files
during compilation and embedding it into object files. When the linker combines these object
files into a binary, the metadata is merged as-is.

Since GCC compiles each source file independently, the plugin cannot share context across
files. As a result, common headers included in multiple files lead to duplicated metadata in
the final binary.

To address this, **ESSTRA Utility** provides the shrink command, which removes redundant
metadata and reduces binary size.

## License

See the [LICENSE](/LICENSE) file.
