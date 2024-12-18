# ESSTRA Core

ESSTRA Core intervenes in compilation to gather information about all source
and header files involved in compilation and embed it as metadata in the
resulting binary file.

## Status of This Version

ESSTRA Core is being developed on Ubuntu 22.04 with GCC 11.4.0 installed on a
x86\_64 PC.

This version of ESSTRA Core creates an ELF section `esstra_info` in the
resulting binary file of compilation with GCC.
This section contains information about all files involved in compilation,
including the full path and SHA-1 hash.

Note that the specifications and features of ESSTRA Core, including the name of
the ELF section, the data formats, and content of the metadata as well as the
input/output specifications of each tool are tentative and may change in the
future versions.

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

For example, if you compile a source file `helloworld.c` or `helloworld.cpp`
with `gcc` or `g++` to generate a binary file `helloworld`, type:

```sh
$ gcc -fplugin=/usr/local/share/esstra/esstracore.so helloworld.c -o helloworld
or
$ g++ -fplugin=/usr/local/share/esstra/esstracore.so helloworld.cpp -o helloworld
```

The generated binary file `helloworld` has metadata embedded by ESSTRA Core.

Use [ESSTRA Utility](../util/README.md) to access metadata embedded in binary
files.

Note that this does not affect the behavior of the binary file itself.

## Installing a Spec File

It will surely be annoying that you have to specify `-fplugin=....` for every
gcc/g++ invocation.
If you want to apply ESSTRA Core to any gcc/g++ occurrence, just type:

```sh
$ sudo make install-specs
```

This installs a [GCC spec file](https://gcc.gnu.org/onlinedocs/gcc/Spec-Files.html)
on your system which enables the option `-fplugin=....` as default.
So, compiling anything hereafter with GCC as usual:

```sh
$ gcc helloworld.c -o helloworld
```

generates a binary file with metadata embedded by ESSTRA Core.

This is a very useful feature if you compile some open source (or closed or
whatever) projects and also want information ESSTRA generates for them.
You do not ever need to modify Makefiles, CMakeList.txts, build.ninjas,
meson.builds, etc, etc...

However, please note that installing the spec file causes every gcc/g++
call hereafter will be intervened by ESSTRA Core on systemwide.

To disable this, type:

```sh
$ sudo make uninstall-specs
```

to remove the spec file.

## License

See the [LICENSE](../LICENSE) file.
