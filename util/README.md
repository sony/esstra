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

Since [ESSTRA Utility](./util/README.md) depends on the [PyYAML](https://pyyaml.org/)
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
$ esstra.py <command> <arg> ...
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
  - FileName: floatn.h
    SHA1: 806b759ab6894a09a3b3a422eec5f2414ba7dab7
  - FileName: libc-header-start.h
    SHA1: e0a400c194cd3962a342a6504a441920163b799c
  - FileName: long-double.h
    SHA1: 4e3f5928e816ad29079d1c7d75f3a510a0939ffb
  - FileName: stdio_lim.h
    SHA1: 6210c8ae410ee0f39a6096b0adb9fa86febd3517
  - FileName: time64.h
    SHA1: ab2017da21608498b58eea37b2aa6a3387ee978c
  - FileName: timesize.h
    SHA1: f1dd8d62a4d75288654626933edfc82ccf2394a7
  - FileName: types.h
    SHA1: e5893a9c4c523615c73a51feb9680279608027c6
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
  /usr/include/x86_64-linux-gnu/bits:
  - FileName: typesizes.h
    SHA1: ee94b5a60d007c23bdda9e5c46c8ba40f4eb402c
  - FileName: wordsize.h
    SHA1: 281ddd3c93f1e8653e809a45b606574c9b691092
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

### Command "update"

The command `update` of the current version attaches **license information** to
each file's information in the metadata.

We think some other kinds of information would also be helpful.  For example,
copyright information, CVE numbers of fixed vulnerabilities, and so on.

Since ESSTRA is at an early stage in development now, we have developed a
feature that attaches license information as a sort of feasibility study.

To attach license information, you need to prepare an
[SPDX 2.3 tag-value](https://spdx.github.io/spdx-spec/v2.3/) file
including `LicenseInfoInFile:` tags.

Some license scanners such as [FOSSology](https://fossology.github.io/) can
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
contains an overall guide to compile
[util-linux](https://github.com/util-linux/util-linux) with ESSTRA Core
applied, perform license scan with FOSSology and download the resulting SPDX
tag-value file, attach license information to the binary files of util-linux by
using ESSTRA Utility, and show the result of it.

One of the result would be as follows:

```yaml

(some simple binary's result here)

```


### Command "shrink"

The current version of ESSTRA is making use of the mechanism of
[GCC Plugin](https://gcc.gnu.org/wiki/plugins).
This can easily cause the size of the resulting binary files' metadata very large.

The reason is ... (write it later)




## License

See the [LICENSE](../LICENSE) file.
