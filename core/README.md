# ESSTRA Core

ESSTRA Core intervenes in compilation and embeds information about all source
and header files involved in compilation as metadata in the resulting binary
file.

## Status of This Version

ESSTRA Core is being developed on Ubuntu 22.04 with GCC 11.4.0 installed on a
x86\_64 PC.

This version of ESSTRA Core has a feature to embed a list of the absolute paths
of all source and header files involved in compilation into a binary file as
metadata.

Note that the data formats and content of the metadata, as well as the
input/output specifications of each tool, are tentative and may change in the
future.

## How to Build and Install

Before you build the GCC plugin, you have to install a package on your system.
For Debian/Ubuntu, check the version of GCC first:

```sh
$ gcc --version
gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0
...
```

In this case, the major version is 11, so install the package named
`gcc-11-plugin-dev`:

```sh
$ sudo apt install gcc-11-plugin-dev
```

Here, ESSTRA depends on third party modules stored in the
[`../third_party`](../third_party) directory.  Since the modules are [git
submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), you may need
to type:

```sh
$ git submodule init
$ git submodule update
```

to clone the source code in the directory for the first time.


After that, run `make` in the top directory:

```sh
$ make
```

If no errors, a file named `esstracore.so` is generated.
This is the GCC plugin "ESSTRA Core."

To install ESSTRA Core on your system, run the following command:

```sh
$ sudo make install
```

Then `esstracore.so` is installed in `/usr/local/share/esstra/`.

## How to Use

To use ESSTRA Core, specify the path of `esstracore.so` using the option
`-fplugin=` of `gcc` or `g++`.

For example, if you compile a source file `helloworld.c` with `gcc` and
generates a binary file `helloworld`, type:

```sh
$ gcc -fplugin=/usr/local/share/esstra/esstracore.so helloworld.c -o helloworld
```

For a C++ source file `helloworld.cpp`, type:

```sh
$ g++ -fplugin=/usr/local/share/esstra/esstracore.so helloworld.cpp -o helloworld
```

The generated binary file `helloworld` has metadata embedded by ESSTRA Core.

Use [ESSTRA Utility](../util/README.md) a to access metadata embedded in binary
files.

Note that this does not affect the behavior of the binary file itself.

## Spec Files

It might be annoying to specify the option `-fplugin= ` for every `gcc` or
`g++`.
In such case, you can take advantage of GCC's
[Spec Files](https://gcc.gnu.org/onlinedocs/gcc/Spec-Files.html) mechanism
which allows you to implicitly specify the default options of the compiler.
See the linked article for more information.

## License

See the [LICENSE](../LICENSE) file.
