# Support for Reproducible Builds in ESSTRA

[Reproducible Builds](https://reproducible-builds.org/) is a mechanism aimed at ensuring that,
regardless of who, when, or where the build is performed, the exact same binary can be
generated from the same source code.

**Project ESSTRA** supports Reproducible Builds by providing a feature that unifies the file
path information embedded in binaries, making it independent of the build environment.

This document explains the mechanism **ESSTRA** provides for path unification and describes how to
use this feature in **ESSTRA Core** and **ESSTRA Link**.

## Overview

**ESSTRA** obtains the absolute paths of all source files referenced during compilation in the
build environment and embeds the information as metadata in the final binary.

However, since **ESSTRA** collects file information at compile time, it cannot determine the
hierarchy or location of files within the source tree. Additionally, it is difficult to
standardize build environments.

Even when building from the same source tree, situations easily arise where, for example,
environment A builds under `/home/snagao`, while environment B builds under `/builds/target`:

| Environment A                                           | Environment B                                             |
|---------------------------------------------------------|-----------------------------------------------------------|
| <b>/home/snagao</b>/esstra/samples/hello/hello.c        | <b>/builds/target</b>/esstra/samples/hello/hello.c        |
| <b>/home/snagao</b>/esstra/samples/hello2/hello\_sub.c  | <b>/builds/target</b>/esstra/samples/hello2/hello\_sub.c  |
| <b>/home/snagao</b>/esstra/samples/hello2/hello\_sub.h  | <b>/builds/target</b>/esstra/samples/hello2/hello\_sub.h  |
| <b>/home/snagao</b>/esstra/samples/hello2/hello\_main.c | <b>/builds/target</b>/esstra/samples/hello2/hello\_main.c |

This means that the metadata embedded by **ESSTRA** may differ depending on the environment, even
if the binary is generated from the same source tree.

To resolve such path inconsistencies caused by the build environment, **ESSTRA** provides a feature
that allows users to replace the prefix of absolute source file paths according to specified
rules. By using this feature, the metadata embedded by **ESSTRA** can be made unique and
environment-independent.

## file-prefix-map Option

**ESSTRA** introduces the `file-prefix-map` option, which works similarly to gcc's `-f*-prefix-map`
option.

By specifying path prefix replacement rules for the build environment with this option, source
file paths can be unified across all environments.

The replacement rule is basically as follows:

- `<before>:<after>`

This means that if the beginning of a file path matches `<before>`, the entire `<before>` part
is replaced with `<after>`.

You can also enclose multiple rules in double quotes and separate them with spaces:

- `"<before_1>:<after_1> <before_2>:<after_2> ..."`

For example, given the rule:

- `/home/snagao/esstra:/tmp/build/src`

The comparison between the original and replaced paths is as follows:

| Before                                                  | After                                              |
|---------------------------------------------------------|----------------------------------------------------|
| <b>/home/snagao</b>/esstra/samples/hello/hello.c        | <b>/tmp/build/src</b>/samples/hello/hello.c        |
| <b>/home/snagao</b>/esstra/samples/hello2/hello\_sub.c  | <b>/tmp/build/src</b>/samples/hello2/hello\_sub.c  |
| <b>/home/snagao</b>/esstra/samples/hello2/hello\_sub.h  | <b>/tmp/build/src</b>/samples/hello2/hello\_sub.h  |
| <b>/home/snagao</b>/esstra/samples/hello2/hello\_main.c | <b>/tmp/build/src</b>/samples/hello2/hello\_main.c |

By utilizing this feature, you can unify or abstract environment-specific paths embedded in
metadata.

Path prefix replacement can be performed by **ESSTRA Core** (at compile time) or **ESSTRA Link** (at
link time).

## Differences Between Replacement by **ESSTRA Core** and **ESSTRA Link**

You can choose whether to perform path prefix replacement in the metadata embedded by **ESSTRA**
Core at compile time or by **ESSTRA Link** at link time.

The difference is:

- Replacement at compile time affects the metadata embedded in object files (`*.o`).
- Replacement at link time affects the metadata when object files are combined to generate the binary.

If you need to consider the metadata in object files generated during compilation, use **ESSTRA**
Core to replace paths for each compilation unit. If you only need to consider the metadata in
the final binary, **ESSTRA Link** can perform path replacement at link time.

It is not recommended to perform path replacement with both **ESSTRA Core** and **ESSTRA Link** in a
single build, as this can cause confusion due to double conversion.

## Path Replacement by ESSTRA Core

To replace path prefixes with **ESSTRA Core**, specify the path to the GCC Plugin `esstracore.so`
with `gcc`/`g++`:

- `-fplugin=/path/to/.../esstracore.so`

Then pass the replacement rule with the following option:

- `-fplugin-arg-esstracore-file-prefix-map=<rule>`

For example, when compiling [samples/hello2](../samples/hello2), assuming the **ESSTRA** repository
is cloned under `/home/snagao/esstra`:

```shell
$ cd /home/snagao/esstra/samples/hello2
$ gcc -fplugin=/path/to/.../esstracore.so -fplugin-arg-esstracore-file-prefix-map=/home/snagao:/tmp/build \
  hello_main.c hello_sub.c -o hello2
```

Here, the rule replaces `/home/snagao` with `/tmp/build`. As a result, the `SourceFiles:`
metadata embedded in the binary `hello2` will look like:

```yaml
SourceFiles:
- Directory: /tmp/build/esstra/samples/hello2
  Files:
  - File: hello_main.c
    SHA1: f7f5c447d68fd9685594a31cb10c8d8b1dd5ebd6
  - File: hello_sub.c
    SHA1: cfb72998ae0242237fa42c8bcf61ee5887137392
  - File: hello_sub.h
    SHA1: 3e5b3ed1aed966c0e0c183eac8fe6ea02dfa62a0
- Directory: /usr/include
  Files:
  - File: features-time64.h
      :
```

### Specifying Path Replacement in Build Rules

When building open source software, build rules such as Makefile usually exist, and options
passed to the C compiler are often stored in the `CFLAGS` variable.

In such cases, you can add the **ESSTRA Core** plugin specification and replacement rule option to
`CFLAGS` to include **ESSTRA** metadata in the generated binary, and ensure that the metadata does
not contain environment-specific path prefixes.

For example, in the section [Adding Provenance Information to Debug
Packages](case-study/debian.md#adding-provenance-information-to-debug-packages) of the document
[Demo of Adding Provenance Information to Debug Packages](case-study/debian.md), the option
`-fplugin` is added to the `CFLAGS` variable to specify the path to `esstracore.so`.

By further adding the `-fplugin-arg-esstracore-file-prefix-map` option to `CFLAGS`, you can
convert the path prefix embedded in the metadata:

```diff
 #!/usr/bin/make -f

+ESSTRA_CORE := -fplugin=/usr/local/lib/gcc/x86_64-linux-gnu/11/plugin/esstracore.so
+ESSTRA_CORE += -fplugin-arg-esstracore-file-prefix-map=$(CURDIR):/tmp/build

 export DEB_BUILD_MAINT_OPTIONS=hardening=-format

 DEB_HOST_GNU_TYPE := $(shell dpkg-architecture -qDEB_HOST_GNU_TYPE)
 CC = $(DEB_HOST_GNU_TYPE)-gcc
 CFLAGS := `dpkg-buildflags --get CFLAGS` -Wall
+CFLAGS += $(**ESSTRA**_CORE)
 LDFLAGS := `dpkg-buildflags --get LDFLAGS`
    :
```

In the above example,the directory `$(CURDIR)` where the build rule is executed, that is, the
top directory of the source files, is replaced with `/tmp/build`.  As a result, the
`SourceFiles:` metadata will look like:

```yaml
SourceFiles:
- Directory: /tmp/build
  Files:
  - File: consts.h
    SHA1: 9301a1db2faa3fa34eba5b55919868a07214972e
  - File: crc32.c
    SHA1: 34c68d749778dd48752ab8136b688c7e8321587d
  - File: crc32.h
    SHA1: 981bdf5d05188a9ab36b2beceeebf75a0c8142ab
      :

- Directory: /tmp/build/unix
  Files:
  - File: unix.c
    SHA1: c8e3fc02d41d405f88992921611fd0aaa8b74271
  - File: unxcfg.h
    SHA1: 7fb54a3538642300c1ad27f1b8f047e82a7149b4
      :

- Directory: /usr/include
  Files:
  - File: alloca.h
    SHA1: 83e3e7761b60dfd6a78ba7c3d56cbfb5ab0ddd0f
  - File: ctype.h
    SHA1: 0f24cc508799871003f045496777f02cb841a75a
  - File: dirent.h
      :

```

## Path Replacement by ESSTRA Link

To replace path prefixes with **ESSTRA Link**, specify the path to the Linker Plugin
`esstralink.so` with `gcc`/`g++`:

* `-Wl,-plugin=/path/to/.../esstralink.so`

Then pass the replacement rule with the following option:

* `-Wl,-plugin-opt=file-prefix-map=<rule>`

In addition to the rule format described above, you can also use the format `auto:<prefix>`.

When the rule `auto:<prefix>` is given:

* The common prefix of all source file paths is automatically identified and replaced with the
  specified `<prefix>`.
* If only `auto` is given, the common prefix is replaced with `"."` (current directory).
* Files included in system header include paths are not subject to replacement.

Below is an example of replacing the paths when linking [samples/hello2](../samples/hello2).
Assume that the entire **ESSTRA** repository has been cloned under `/home/snagao/esstra`:

```shell
$ cd /home/snagao/esstra/samples/hello2
$ gcc -fplugin=/path/to/.../esstracore.so \
  -Wl,-plugin=/path/to/.../esstralink.so,-plugin-opt=file-prefix-map=/home/snagao:/tmp/build \
  hello_main.c hello_sub.c -o hello2
```

As in the **ESSTRA Core** replacement example, the rule replaces `/home/snagao` with `/tmp/build`.
As a result, the metadata `SourceFiles:` embedded in the binary `hello2` will be the same as
the result obtained when replaced by **ESSTRA Core**:

```yaml
SourceFiles:
- Directory: /tmp/build/esstra/samples/hello2
  Files:
  - File: hello_main.c
    SHA1: f7f5c447d68fd9685594a31cb10c8d8b1dd5ebd6
  - File: hello_sub.c
    SHA1: cfb72998ae0242237fa42c8bcf61ee5887137392
  - File: hello_sub.h
    SHA1: 3e5b3ed1aed966c0e0c183eac8fe6ea02dfa62a0
- Directory: /usr/include
  Files:
  - File: features-time64.h
      :
```

Example applying the `auto` rule:

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
  -Wl,-plugin=/path/to/.../esstralink.so,-plugin-opt=file-prefix-map=auto:/project \
  hello_main.c hello_sub.c -o hello2
```

As a result, the `SourceFiles:` metadata embedded in the binary `hello2` will look like:

```yaml
SourceFiles:
- Directory: /project
  Files:
  - File: hello_main.c
    SHA1: f7f5c447d68fd9685594a31cb10c8d8b1dd5ebd6
  - File: hello_sub.c
    SHA1: cfb72998ae0242237fa42c8bcf61ee5887137392
  - File: hello_sub.h
    SHA1: 3e5b3ed1aed966c0e0c183eac8fe6ea02dfa62a0
- Directory: /usr/include
  Files:
  - File: features-time64.h
      :
```

In this example, since all source files are located under `/home/snagao/esstra/samples/hello2`,
the path is treated as the common prefix and is replaced with `/project` as specified by the
`auto` option.

### Specifying Path Replacement in Build Rules

Here, as with the **ESSTRA Core** example, we show how to perform path replacement using **ESSTRA**
Link, based on the example in the section [Adding Provenance Information to Debug
Packages](case-study/debian.md#adding-provenance-information-to-debug-packages) of the document
[Demo of Adding Provenance Information to Debug Packages](case-study/debian.md).

First, specify the path to `esstracore.so` with the `-fplugin` option to embed metadata in
object files at compile time. Then, use the `-Wl,-plugin` option to specify the path to
`esstralink.so` so that **ESSTRA Link** operates at link time, and specify the path replacement
rule with the `-Wl,-plugin-opt=file-prefix-map` option.

Usually, options passed to the compiler at link time are stored in the `LDFLAGS` variable. The
following example shows how to add options to `LDFLAGS`:

```diff
 #!/usr/bin/make -f

+ESSTRA_CORE := -fplugin=/usr/local/lib/gcc/x86_64-linux-gnu/11/plugin/esstracore.so
+ESSTRA_LINK := -Wl,-plugin=/usr/local/lib/gcc/x86_64-linux-gnu/11/plugin/esstralink.so
+ESSTRA_LINK += -Wl,-plugin-opt=file-prefix-map=$(CURDIR):/tmp/build

 export DEB_BUILD_MAINT_OPTIONS=hardening=-format

 DEB_HOST_GNU_TYPE := $(shell dpkg-architecture -qDEB_HOST_GNU_TYPE)
 CC = $(DEB_HOST_GNU_TYPE)-gcc
 CFLAGS := `dpkg-buildflags --get CFLAGS` -Wall
+CFLAGS += $(ESSTRA_CORE)
 LDFLAGS := `dpkg-buildflags --get LDFLAGS`
+LDFLAGS += $(ESSTRA_LINK)
    :

```

As with the **ESSTRA Core** example, the directory `$(CURDIR)` where the build rule is executed,
i.e., the top directory of the source files) is replaced with `/tmp/build`. As a result, the
contents of `SourceFiles:` in the metadata will be shown below, which is the same as in the
**ESSTRA Core** example:

```yaml
SourceFiles:
- Directory: /tmp/build
  Files:
  - File: consts.h
    SHA1: 9301a1db2faa3fa34eba5b55919868a07214972e
  - File: crc32.c
    SHA1: 34c68d749778dd48752ab8136b688c7e8321587d
  - File: crc32.h
    SHA1: 981bdf5d05188a9ab36b2beceeebf75a0c8142ab
      :

- Directory: /tmp/build/unix
  Files:
  - File: unix.c
    SHA1: c8e3fc02d41d405f88992921611fd0aaa8b74271
  - File: unxcfg.h
    SHA1: 7fb54a3538642300c1ad27f1b8f047e82a7149b4
      :

- Directory: /usr/include
  Files:
  - File: alloca.h
    SHA1: 83e3e7761b60dfd6a78ba7c3d56cbfb5ab0ddd0f
  - File: ctype.h
    SHA1: 0f24cc508799871003f045496777f02cb841a75a
  - File: dirent.h
      :

```

## Summary

This document explained that by providing path prefix replacement rules to **ESSTRA** via the
`file-prefix-map` option in **ESSTRA Core** and **ESSTRA Link**, users can unify the path information
in the metadata embedded in binaries, making it independent of the build environment.

For detailed specifications of the `file-prefix-map` option, please refer to the README files
for [**ESSTRA Core**](../core/README.md) and [**ESSTRA Link**](../link/README.md).
