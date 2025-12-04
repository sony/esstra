# ESSTRA Core

**ESSTRA Core** intervenes in the compilation process to gather information about all source
and header files involved, embedding this data as metadata in the resulting binary file.

In this version, **ESSTRA Core** creates an ELF section named `.esstra` in the resulting binary
file compiled with GCC. This section contains information about all files involved in the
compilation, including their full paths and SHA-1 hashes.

> [!NOTE]
> The current version of **ESSTRA** is under active development.
> Please be aware that the metadata format and content, as well as the specifications and
> functionality of each tool, are provisional and subject to change.

## How to Use

See the following sections in the [README.md](/README.md) file in the top-level directory for a
quick overview of how to use the tool:

* [How to Build and Install](/README.md#how-to-build-and-install)
* [Compiling](/README.md#compiling)
* [Installing GCC Spec File](/README.md#installing-gcc-spec-file)

## Applying **ESSTRA Core** at Compile Time

Use GCC's `-fplugin` option to specify the path to `esstracore.so`:

```shell
$ gcc -fplugin=/path/to/.../esstracore.so ...
```

This allows **ESSTRA Core** to intervene during compilation and embed metadata into the
resulting binary.

## Options of ESSTRA Core

You can pass options to **ESSTRA Core** by supplying the following arguments to GCC:

* `-fplugin-arg-esstracore-<option>[=<value>]`

Here, `<option>` is the option name, and `<value>` is the value assigned to that option.
Although the option names can become quite long, this is due to GCC’s specification

### Option `file-prefix-map`

The option:

* `-fplugin-arg-esstracore-file-prefix-map=<rule>`

is used to replace the initial part (prefix) of source file paths embedded as metadata with
another path name.
This feature can be used to achieve [Reproducible Builds](../doc/reproducible_builds.md).
The format for the option value `<rule>` is:

* `<before>:<after>`

This means that any path starting with `<before>` will be replaced with a path starting with
`<after>`.  You can also specify multiple replacement rules by enclosing the entire value in
double quotes and separating rules with spaces:

* `"<before1>:<after1> <before2>:<after2> ..."`

For example, specifying the following will replace all paths starting with `/home/snagao/esstra`
with paths starting with `.`:

* `-fplugin-arg-esstracore-file-prefix-map=/home/snagao/esstra:.`

When [Project ESSTRA's repository](https://github.com/sony/esstra) is cloned under
`/home/snagao/esstra`, the option above will transform the paths of source files included in
[samples/hello2](../samples/hello2) when they are embedded as metadata, as shown below:

| **Before**                                       | **After**                      |
|--------------------------------------------------|--------------------------------|
| /home/snagao/esstra/samples/hello2/hello\_sub.h  | ./samples/hello2/hello\_sub.h  |
| /home/snagao/esstra/samples/hello2/hello\_sub.c  | ./samples/hello2/hello\_sub.c  |
| /home/snagao/esstra/samples/hello2/hello\_main.c | ./samples/hello2/hello\_main.c |

#### Example

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -fplugin-arg-esstracore-file-prefix-map=/home/snagao/esstra:. \
      hello_main.c hello_sub.c -o hello2
$ esstra show hello2
Headers:
      :
      :
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

### Option `verbose`

The option:

* `-fplugin-arg-esstracore-verbose`

makes **ESSTRA Core** run in verbose mode.
This option helps you understand what operations **ESSTRA Core** is performing.

#### Example

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -fplugin-arg-esstracore-verbose \
      hello_main.c hello_sub.c -o hello2
```

### Option `silent`

The option:

* `-fplugin-arg-esstracore-silent`

makes **ESSTRA Core** mute and suppresses all message output, including errors.
If you want errors to be displayed, enable the [`show-error`](#option-show-error) option.

#### Example

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -fplugin-arg-esstracore-silent \
      hello_main.c hello_sub.c -o hello2
```

### Option `show-error`

The option:

* `-fplugin-arg-esstracore-show-error`

makes **ESSTRA Core** output errors even when muted by the [`silent`](#option-silent) option.

#### Example

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -fplugin-arg-esstracore-silent
      -fplugin-arg-esstracore-show-error \
      hello_main.c hello_sub.c -o hello2
```

### Option `debug`

The option:

* `-fplugin-arg-esstracore-debug=<value>`

controls the output of debug messages.  If you set `<value>` to 1, **ESSTRA Core** will output
debug messages and all other types of messages to `stderr`. By default, no debug messages are
output.

#### Example

```shell
$ gcc -fplugin=/path/to/.../esstracore.so \
      -fplugin-arg-esstracore-debug=1 \
      hello_main.c hello_sub.c -o hello2
```

## Known Issues

Here is the list of known issues in the current version:

* **LTO option prevents metadata generation**
  - **Description**: When using the LTO option (`-flto`) with `gcc`/`g++`,
    the generated binaries do not contain the expected metadata.
  - **Workaround**: Remove the LTO option.

## License

See the [LICENSE](/LICENSE) file.
