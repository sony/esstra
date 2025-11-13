# ESSTRA Link

**ESSTRA Link** is a [GNU linker plugin](https://sourceware.org/binutils/docs/ld/Plugins.html)
that performs post-processing during the linking phase of GCC to optimize the metadata embedded
in the resulting binary file.

Specifically, it removes redundant entries from the metadata originating from multiple object
files, ensuring the uniqueness of the information.

It also removes environment-specific path prefixes from file paths in metadata and converts
them to relative paths in order to ensure consistent path information across different
environments.

> [!NOTE]
> The current version of **ESSTRA** is under active development.
> Please be aware that the metadata format and content, as well as the specifications and
> functionality of each tool, are provisional and subject to change.

## How to Use

See the following sections in the [README.md](/README.md) file in the top-level directory for a
quick overview of how to use the tool:

* [How to Build and Install](/README.md#how-to-build-and-install)
* [Linking](/README.md#linking)
* [Installing GCC Spec File](/README.md#installing-gcc-spec-file)

## Applying ESSTRA Link at Link Time

**ESSTRA Link** works by passing the path to `esstralink.so` to the linker `ld` using the
`-plugin` option.  However, linking is usually performed via GCC rather than directly with
`ld`.  Therefore, this section explains how to use **ESSTRA Link** through GCC.

In GCC, you can enable **ESSTRA Link** by specifying linker options using the `-Wl` option:

```shell
$ gcc -Wl,-plugin=/path/to/.../esstralink.so ...
```

This allows **ESSTRA Link** to intervene during GCC's linking stage and optimize the metadata
embedded in the resulting binary.

## Options of ESSTRA Link

Options for **ESSTRA Link** can be provided using the linker option `-plugin-opt`.  From GCC,
you can pass these options via `-Wl` as follows:

```shell
$ gcc -Wl,-plugin-opt=...
```

Since the `-Wl` option allows multiple linker options to be concatenated with commas, you can
pass both the `-plugin` and `-plugin-opt` options to GCC as follows:

```shell
$ gcc -Wl,-plugin=/path/to/.../esstralink.so,-plugin-opt=...
```

Note that **ESSTRA Link** optimizes the metadata in the resulting binary based on the metadata
embedded by **ESSTRA Core**.  So, ensure that you specify `esstracore.so` using the `-fplugin`
option:

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -Wl,-plugin=/path/to/.../esstralink.so,-plugin-opt=...
```

### Option `file-prefix-map`

The option `-plugin-opt=file-prefix-map` is used to replace the initial part (prefix) of source
file paths embedded as metadata with another path name.  This feature can be used to achieve
[Reproducible Builds](../doc/reproducible_builds.md).

The format for specifying the option value is:

* `-plugin-opt=file-prefix-map=<rule>` (for a single rule), or
* `-plugin-opt=file-prefix-map="<rule1> <rule2> ..."` (for multiple rules)

Each `<rule>` defines a path replacement rule.
Note that the `=` character appears twice in the syntax.

You can specify `<rule>` in one of the following formats:

* `<before>:<after>` --  If the path prefix matches `<before>`, it will be replaced with `<after>`.
* `auto` -- Automatically detect the common path prefix and replace it with`.` (the current directory).
* `auto:<after>` --  Automatically detect the common path prefix and replace it with `<after>`.

For example, the following argument replaces all paths starting with `/home/snagao/esstra` with
paths starting with `.` (the current directory):

* `-plugin-opt=file-prefix-map=/home/snagao/esstra:.`

When [Project ESSTRA's repository] https://github.com/sony/esstra is cloned under
`/home/snagao/esstra`, the option above transforms the paths of source files under
[samples/hello2](../samples/hello2) embedded in the binary metadata as follows:

| **Before**                                       | **After**                      |
|--------------------------------------------------|--------------------------------|
| /home/snagao/esstra/samples/hello2/hello\_sub.h  | ./samples/hello2/hello\_sub.h  |
| /home/snagao/esstra/samples/hello2/hello\_sub.c  | ./samples/hello2/hello\_sub.c  |
| /home/snagao/esstra/samples/hello2/hello\_main.c | ./samples/hello2/hello\_main.c |

When `auto` is specified, files contained in system header include paths such as `/usr/include`
are excluded from replacement.

#### Command Line

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -Wl,-plugin=/path/to/.../esstralink.so \
      -Wl,-plugin-opt=file-prefix-map=/home/snagao/esstra:. \
      hello_main.c hello_sub.c -o hello2
```

#### Result

```yaml
SourceFiles:
- Directory: ./samples/hello2
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

Additionally, when:

* `-plugin-opt=file-prefix-map=auto:/project`

specified, the common path shared by all source files:

* `/home/snagao/esstra/samples/hello2`

is automatically detected and replaced with `/project`:

| **Before**                                       | **After**              |
|--------------------------------------------------|------------------------|
| /home/snagao/esstra/samples/hello2/hello\_sub.h  | /project/hello\_sub.h  |
| /home/snagao/esstra/samples/hello2/hello\_sub.c  | /project/hello\_sub.c  |
| /home/snagao/esstra/samples/hello2/hello\_main.c | /project/hello\_main.c |

#### Command Line

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -Wl,-plugin=/path/to/.../esstralink.so \
      -Wl,-plugin-opt=file-prefix-map=auto:/project \
      hello_main.c hello_sub.c -o hello2
```

#### Result

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

## License

See the [LICENSE](/LICENSE) file.
