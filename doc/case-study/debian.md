# Demo of Adding Provenance Information to Debug Packages

Debian, one of the most popular Linux distributions, distributes its software components as
precompiled "binary packages." Since binary packages have debugging information removed, they
also distribute "debug packages" that include such information for debugging purposes.

In this demo, from a perspective of Linux distributors, we will demonstrate a way to include
provenance information obtained using ESSTRA into a debug package by modifying the
`debian/rules` file. This approach extends the concept of Debian debug package.

We will use a relatively compact **unzip** package as an example to explain the specific steps.

## Purpose of This Demo

By including in the packages to distribute the provenance information of the binary files,
which details the source files used to create the binary flies, Linux distributions can offer
the following benefits to distributors, users, and the entire software supply chain:

* **Identify Binary Provenance**: With clear provenance information for each binary,
  distributors can more easily guarantee quality and reliability, and users can verify the
  quality and safety of the software.
* **Provide Accurate License Information**: By precisely identifying the license information of
  source files, distributors can provide more accurate license details, and users can better
  comply with licenses when using or redistributing binaries.
* **Identify and Respond to Vulnerabilities Rapidly**: When vulnerabilities are reported,
  provenance information allows for the quick identification of affected components and the
  implementation of countermeasures, minimizing security risks.
* **Enhance Software Supply Chain Transparency**: Sharing accurate provenance information
  improves transparency across the entire supply chain.
* **Generate SBOMs**: By utilizing provenance information, the accuracy of the Software Bill of
  Materials (SBOM) can be enhanced. This allows for detailed documentation of components and
  dependencies, thereby improving transparency and security.

Based on the above background, this demo will illustrate how to package binary provenance
information with ESSTRA, using Debian as an example, which is one of the most popular Linux
distributions. The concepts demonstrated here can be applied not only to Debian but to any
Linux distribution.

## Execution Environment

This document assumes an x86_64 PC with Ubuntu 22.04 installed as the execution environment,
just as described in the top directory's [README.md](/README.md) for ESSTRA.

First, build and install ESSTRA on your PC:

```shell
$ sudo apt install -y gcc-11-plugin-dev python3-yaml
$ git clone https://github.com/sony/esstra.git
$ cd esstra
$ make
$ sudo make install
```

Next, uncomment the `deb-src` lines in `/etc/apt/sources.list` and update the package list:

```shell
$ sudo sed -i 's/^# deb-src/deb-src/' /etc/apt/sources.list
$ sudo apt update
```

Then, install the necessary packages for building and managing Debian packages:

```shell
$ sudo apt install -y debhelper devscripts
```

If you have already installed the Spec File as described in Section [Installing a Spec
File](/README.md#installing-spec-file) in the top directory's README.md,
**uninstall it before proceeding**:

```shell
$ sudo make uninstall-specs
```

## Debian Package Types

Debian offers several types of packages. In this demo, we will focus on the following three types:

* **Binary Package**: Software in executable form. Ready to use upon installation.
* **Debug Package**: Contains debugging information. Helps developers identify issues.
* **Source Package**: Includes source code and build information. Used to create binary and debug packages.

Using the **unzip** package as an example, the steps to build packages from a source package are as follows:

1. Install the build dependencies:
   ```shell
   $ sudo apt build-dep unzip
   ```
2. Download and unpack the source package:
   ```shell
   $ apt source unzip
   $ ls -l
   drwxrwxr-x 31 snagao snagao 4.0K Apr 21 16:02 unzip-6.0/
   -rw-r--r--  1 snagao snagao  29K Feb  8  2024 unzip_6.0-26ubuntu3.2.debian.tar.xz
   -rw-r--r--  1 snagao snagao 1.8K Feb  8  2024 unzip_6.0-26ubuntu3.2.dsc
   -rw-r--r--  1 snagao snagao 1.4M Jun  8  2009 unzip_6.0.orig.tar.gz
   ```
3. Go to the unpacked source directory:
   ```shell
   $ cd unzip-6.0
   ```
4. Run the build command:
   ```shell
   $ dpkg-buildpackage -us -uc
   ```
5. Return to the parent directory and verify the generated packages.
   ```shell
   $ cd ..
   $ ls -l
   drwxrwxr-x 31 snagao snagao 4.0K Apr 21 16:02 unzip-6.0/
   -rw-rw-r--  1 snagao snagao 6.9K Apr 21 16:02 unzip_6.0-26ubuntu3.2_amd64.buildinfo
   -rw-rw-r--  1 snagao snagao 2.1K Apr 21 16:02 unzip_6.0-26ubuntu3.2_amd64.changes
   -rw-r--r--  1 snagao snagao 178K Apr 21 16:02 unzip_6.0-26ubuntu3.2_amd64.deb           # binary package
   -rw-r--r--  1 snagao snagao  29K Apr 21 16:02 unzip_6.0-26ubuntu3.2.debian.tar.xz
   -rw-r--r--  1 snagao snagao  928 Apr 21 16:02 unzip_6.0-26ubuntu3.2.dsc
   -rw-r--r--  1 snagao snagao 1.4M Jun  8  2009 unzip_6.0.orig.tar.gz
   -rw-r--r--  1 snagao snagao 284K Apr 21 16:02 unzip-dbgsym_6.0-26ubuntu3.2_amd64.ddeb   # debug package
   ```

The following files generated are the binary and debug packages for **unzip**:

* `unzip_6.0-26ubuntu3.2_amd64.deb` (binary package)
* `unzip-dbgsym_6.0-26ubuntu3.2_amd64.ddeb` (debug package)

The contents of these packages are shown below using the `dpkg -c` command:

* **`unzip_6.0-26ubuntu3.2_amd64.deb`**
  ```shell
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/bin/
  -rwxr-xr-x root/root     22832 2024-02-02 00:52 ./usr/bin/funzip
  -rwxr-xr-x root/root    182720 2024-02-02 00:52 ./usr/bin/unzip
  -rwxr-xr-x root/root     84400 2024-02-02 00:52 ./usr/bin/unzipsfx
  -rwxr-xr-x root/root      2959 2024-02-02 00:52 ./usr/bin/zipgrep
  hrwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/bin/zipinfo link to ./usr/bin/unzip
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/mime/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/mime/packages/
  -rw-r--r-- root/root        77 2021-01-11 06:44 ./usr/lib/mime/packages/unzip
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/doc/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/doc/unzip/
  -rw-r--r-- root/root      4633 2009-01-03 01:33 ./usr/share/doc/unzip/BUGS
  -rw-r--r-- root/root     21529 2009-04-20 09:02 ./usr/share/doc/unzip/History.600.gz
  -rw-r--r-- root/root      9113 2009-04-20 08:10 ./usr/share/doc/unzip/ToDo
  -rw-r--r-- root/root      7169 2024-02-02 00:52 ./usr/share/doc/unzip/changelog.Debian.gz
  -rw-r--r-- root/root      4086 2021-01-11 06:44 ./usr/share/doc/unzip/copyright
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/man/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/man/man1/
  -rw-r--r-- root/root      1977 2024-02-02 00:52 ./usr/share/man/man1/funzip.1.gz
  -rw-r--r-- root/root     18130 2024-02-02 00:52 ./usr/share/man/man1/unzip.1.gz
  -rw-r--r-- root/root      5508 2024-02-02 00:52 ./usr/share/man/man1/unzipsfx.1.gz
  -rw-r--r-- root/root      1541 2024-02-02 00:52 ./usr/share/man/man1/zipgrep.1.gz
  -rw-r--r-- root/root      8884 2024-02-02 00:52 ./usr/share/man/man1/zipinfo.1.gz
  lrwxrwxrwx root/root         0 2024-02-02 00:52 ./usr/share/doc/unzip/changelog.gz -> History.600.gz
  ```
* **`unzip-dbgsym_6.0-26ubuntu3.2_amd64.ddeb`**
  ```shell
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/40/
  -rw-r--r-- root/root    101808 2024-02-02 00:52 ./usr/lib/debug/.build-id/40/0caf854a6ba84bfaaa39ae64da5f9197ad5dde.debug
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/e2/
  -rw-r--r-- root/root    187936 2024-02-02 00:52 ./usr/lib/debug/.build-id/e2/b924e80bdd8fa01cb2ebeee7d8074d91315fe4.debug
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/e9/
  -rw-r--r-- root/root     25800 2024-02-02 00:52 ./usr/lib/debug/.build-id/e9/0bae57722e2d11de6912bb7ff1e3003af0c372.debug
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.dwz/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.dwz/x86_64-linux-gnu/
  -rw-r--r-- root/root     15752 2024-02-02 00:52 ./usr/lib/debug/.dwz/x86_64-linux-gnu/unzip.debug
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/doc/
  lrwxrwxrwx root/root         0 2024-02-02 00:52 ./usr/share/doc/unzip-dbgsym -> unzip
  ```

For more detail of building packages,
refer to [the official site](https://www.debian.org/doc/manuals/maint-guide/build.en.html).

## Editing `debian/rules`

Debian source packages include a `debian/` directory that contains some files related to
packaging.

Among these files, the `debian/rules` file is written in Makefile format and specifies the
rules for building packages.
When the `dpkg-buildpackage` command is executed, the compilation and packaging processes are
carried out according to the content of the file.

In this demo, we aim to achieve the following two objectives,
both of these objectives can be done by editing the rules in the `debian/rules` file:

* Apply the ESSTRA Core during compilation to include the obtained provenance information in
  the debug package in YAML format.
* Remove the metadata embedded by the ESSTRA Core from the binaries to be included in the
  packages, ensuring they are in the same state as the original package.

In this demo, we will describe how to "separate" provenance information from each binaries and
write it to an individual file as mentioned above. However, it is also possible to keep the
information within the binaries.

### Applying ESSTRA Core during Compilation

The `debian/rules` file defines the variable `CFLAGS` that are passed to GCC.

By adding the option `-fplugin=/usr/local/share/esstra/esstracore.so`,
the ESSTRA Core will intervene in the compiler during the package build process:

```diff
 #!/usr/bin/make -f

+ESSTRA_CORE := -fplugin=/usr/local/share/esstra/esstracore.so

 export DEB_BUILD_MAINT_OPTIONS=hardening=-format

 DEB_HOST_GNU_TYPE := $(shell dpkg-architecture -qDEB_HOST_GNU_TYPE)
 CC = $(DEB_HOST_GNU_TYPE)-gcc
 CFLAGS := `dpkg-buildflags --get CFLAGS` -Wall
+CFLAGS += $(ESSTRA_CORE)
 LDFLAGS := `dpkg-buildflags --get LDFLAGS`
    :
    :
```

### Adding Provenance Information to Debug Packages

By adding a rule with the target name `override_dh_strip:` to the `debian/rules` file, you can
[override `dh_strip`](https://wiki.debian.org/DebugPackage) and add custom processing during
the generation of the debug package.

`dh_strip` is a `dehelper` command that generates files for a debug package and removes debug
information from ELF files which are to be included in the binary package.

Note that source packages for some software may already have an `override_dh_strip:`
target. For example, the **unzip** package includes the following `override_dh_strip:` rule:

```makfile
override_dh_strip:
       dh_strip
       cd debian/unzip/usr/bin && rm -f zipinfo && ln unzip zipinfo
```

In such cases, you only need to add some lines after the existing `override_dh_strip:` rule.

When the command `dpkg-buildflags -us -uc` is executed, it creates files and directories under
`debian/unzip/` and `debian/.debhelper/unzip/dbgsym-root/`, which are to be included in the
binary package and the debug package, respectively. It also strips debug information from
binaries under `debian/unzip/`:

* **`debian/unzip`**: Temporary directory for the binary package
  ```shell
  $ find debian/unzip
  debian/unzip/
  debian/unzip/usr
  debian/unzip/usr/bin
  debian/unzip/usr/bin/zipinfo
  debian/unzip/usr/bin/funzip
  debian/unzip/usr/bin/unzip
  debian/unzip/usr/bin/unzipsfx
  debian/unzip/usr/bin/zipgrep
  debian/unzip/usr/lib
    :
  (snip)
    :
  ```
* **`debian/.debhelper/unzip/dbgsym-root/`**: Temporary directory for the debug package
  ```shell
  $ find debian/.debhelper/unzip/dbgsym-root
  debian/.debhelper/unzip/
  debian/.debhelper/unzip/dbgsym-root
  debian/.debhelper/unzip/dbgsym-root/usr
  debian/.debhelper/unzip/dbgsym-root/usr/lib
  debian/.debhelper/unzip/dbgsym-root/usr/lib/debug
  debian/.debhelper/unzip/dbgsym-root/usr/lib/debug/.build-id
  debian/.debhelper/unzip/dbgsym-root/usr/lib/debug/.build-id/e9
  debian/.debhelper/unzip/dbgsym-root/usr/lib/debug/.build-id/e9/0bae57722e2d11de6912bb7ff1e3003af0c372.debug
  debian/.debhelper/unzip/dbgsym-root/usr/lib/debug/.build-id/e2
  debian/.debhelper/unzip/dbgsym-root/usr/lib/debug/.build-id/e2/b924e80bdd8fa01cb2ebeee7d8074d91315fe4.debug
    :
  (snip)
    :
  ```

Note that binaries under `debian/unzip/` contain ESSTRA's provenance information due to the
recent changes in `debian/rules`.
This is because the `strip` command removes debug information but does not recognize ESSTRA's
metadata.

To begin with, we use the `rm` command of the ESSTRA Utility to remove ESSTRA's metadata from
all the ELF files that are to be included in the binary package:

```diff
 #!/usr/bin/make -f

+ESSTRA_CORE := -fplugin=/usr/local/share/esstra/esstracore.so
+ESSTRA_UTIL := /usr/local/bin/esstra.py
    :
  (snip)
    :
 override_dh_strip:
        dh_strip
        cd debian/unzip/usr/bin && rm -f zipinfo && ln unzip zipinfo
+       $(ESSTRA_UTIL) rm --ignore-errors `find debian/unzip/ -type f -executable`
```

Next, we will describe the process to include provenance information in the debug package.
For each ELF file in the binary package, a corresponding file named
`usr/lib/debug/.build-id/AA/XX...XX.debug`
is created to be stored in the debug package.
This file is essentially a copy of the corresponding ELF file, and just renamed.

The name of the `.debug` file is based on the BuildID of the ELF file, and it varies for each
file and each build.

Therefore, the `.debug` file contains embedded ESSTRA's metadata. So, we will use the ESSTRA
Utility to:

* Export the metadata content from the `.debug` file to a `.yaml` file by the `show` command, and
* Remove the metadata from the `.debug` file by the `rm` command:

```diff
 override_dh_strip:
        dh_strip
        cd debian/unzip/usr/bin && rm -f zipinfo && ln unzip zipinfo
+       $(ESSTRA_UTIL) rm --ignore-errors `find debian/unzip/ -type f -executable`
+       for debug in `find debian/.debhelper/unzip/dbgsym-root/ -name "*.debug"` ; do \
+               yaml=$${debug%.debug}.yaml ; \
+               ($(ESSTRA_UTIL) show --no-comments $$debug > $$yaml && $(ESSTRA_UTIL) rm $$debug) || rm -f $$yaml ; \
+       done
```

As a result, a `.yaml` file with the same name will be placed in the same location as the
`.debug` file and will be included in the debug package.

### Summary of Changes to `debian/rules`

To summarize the changes to `debian/rules` explained so far, the following lines starting
with `+` should be added:

```diff
 #!/usr/bin/make -f

+ESSTRA_CORE := -fplugin=/usr/local/share/esstra/esstracore.so
+ESSTRA_UTIL := /usr/local/bin/esstra.py

 export DEB_BUILD_MAINT_OPTIONS=hardening=-format

 DEB_HOST_GNU_TYPE := $(shell dpkg-architecture -qDEB_HOST_GNU_TYPE)
 CC = $(DEB_HOST_GNU_TYPE)-gcc
 CFLAGS := `dpkg-buildflags --get CFLAGS` -Wall
+CFLAGS += $(ESSTRA_CORE)
 LDFLAGS := `dpkg-buildflags --get LDFLAGS`

    :
  (snip)
    :

 override_dh_strip:
         dh_strip
         cd debian/unzip/usr/bin && rm -f zipinfo && ln unzip zipinfo
+        $(ESSTRAUTIL) rm --ignore-errors `find debian/unzip/ -type f -executable`
+        for debug in `find debian/.debhelper/unzip/dbgsym-root/ -name "*.debug"` ; do \
+                yaml=$${debug%.debug}.yaml ; \
+                ($(ESSTRA_UTIL) show --no-comments $$debug > $$yaml && $(ESSTRAUTIL) rm $$debug) || rm -f $$yaml ; \
+        done

 override_dh_compress:
         dh_compress -XBUGS -XToDo
```

## The LTO Issue and Its Workaround

There is a known issue with the current ESSTRA Core:

* When the GCC's LTO (Link Time Optimization) option is enabled, the ESSTRA's metadata is not
  embedded as expected in the generated binaries.

Since the Debian packaging system enables the LTO option by default, the known issue prevents
the expected results.

However, we have found that packages listed in the file
`/usr/share/lto-disabled-list/lto-disabled-list` have the LTO option disabled during
packaging.

As a workaround, we will use this feature to ensure that the LTO option is not specified during
the packaging of **unzip**:

```diff
 # list of source packages not to build with link time optimization (LTO).
 # format: <source> any | <arch> [<arch> ...]
     :
   (snip)
     :
 zemberek-ooo amd64
 zfs-fuse amd64 ppc64el

+unzip any       # added as a workaround
```

The cause of the known issue is currently under investigation. This workaround is expected to
be unnecessary in the future.

## Building and Verifying the Package

Build the package using the following command. The `debian/rules` file edited so far will be
referenced during the process:

```shell
$ cd unzip-6.0
$ dpkg-buildpackage -us -uc
```

This will compile and package the files, and the following files will be generated in the
parent directory:

* `unzip_6.0-26ubuntu3.2_amd64.deb` (binary package)
* `unzip-dbgsym_6.0-26ubuntu3.2_amd64.ddeb`  (debug package)

The content of the binary package is shown below:

* **`unzip_6.0-26ubuntu3.2_amd64.deb`**
  ```shell
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/bin/
  -rwxr-xr-x root/root     22832 2024-02-02 00:52 ./usr/bin/funzip
  -rwxr-xr-x root/root    182720 2024-02-02 00:52 ./usr/bin/unzip
  -rwxr-xr-x root/root     84400 2024-02-02 00:52 ./usr/bin/unzipsfx
  -rwxr-xr-x root/root      2959 2024-02-02 00:52 ./usr/bin/zipgrep
  hrwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/bin/zipinfo link to ./usr/bin/unzip
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/mime/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/mime/packages/
  -rw-r--r-- root/root        77 2021-01-11 06:44 ./usr/lib/mime/packages/unzip
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/doc/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/doc/unzip/
  -rw-r--r-- root/root      4633 2009-01-03 01:33 ./usr/share/doc/unzip/BUGS
  -rw-r--r-- root/root     21529 2009-04-20 09:02 ./usr/share/doc/unzip/History.600.gz
  -rw-r--r-- root/root      9113 2009-04-20 08:10 ./usr/share/doc/unzip/ToDo
  -rw-r--r-- root/root      7169 2024-02-02 00:52 ./usr/share/doc/unzip/changelog.Debian.gz
  -rw-r--r-- root/root      4086 2021-01-11 06:44 ./usr/share/doc/unzip/copyright
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/man/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/man/man1/
  -rw-r--r-- root/root      1977 2024-02-02 00:52 ./usr/share/man/man1/funzip.1.gz
  -rw-r--r-- root/root     18130 2024-02-02 00:52 ./usr/share/man/man1/unzip.1.gz
  -rw-r--r-- root/root      5508 2024-02-02 00:52 ./usr/share/man/man1/unzipsfx.1.gz
  -rw-r--r-- root/root      1541 2024-02-02 00:52 ./usr/share/man/man1/zipgrep.1.gz
  -rw-r--r-- root/root      8884 2024-02-02 00:52 ./usr/share/man/man1/zipinfo.1.gz
  lrwxrwxrwx root/root         0 2024-02-02 00:52 ./usr/share/doc/unzip/changelog.gz -> History.600.gz
  ```

Due to the modifications made so far to the `debian/rules`, the metadata embedded by the ESSTRA
Core has been removed from the ELF files included in the binary package.
So, this binary package is essentially identical to the original **unzip** binary package as shown
in Section [Debian Package Types](#debian-package-types).

And the content of the debug package is as follows:

* **`unzip-dbgsym_6.0-26ubuntu3.2_amd64.ddeb`**
  ```shell
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/3f/
  -rw-r--r-- root/root    187936 2024-02-02 00:52 ./usr/lib/debug/.build-id/3f/651fe9f8c7e40beea539860aef9689cfc6f4f9.debug
  -rw-r--r-- root/root      6522 2024-02-02 00:52 ./usr/lib/debug/.build-id/3f/651fe9f8c7e40beea539860aef9689cfc6f4f9.yaml
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/52/
  -rw-r--r-- root/root     25800 2024-02-02 00:52 ./usr/lib/debug/.build-id/52/86e01e3211833017e926a0fba155740f9fe5a8.debug
  -rw-r--r-- root/root      5611 2024-02-02 00:52 ./usr/lib/debug/.build-id/52/86e01e3211833017e926a0fba155740f9fe5a8.yaml
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.build-id/ad/
  -rw-r--r-- root/root    101816 2024-02-02 00:52 ./usr/lib/debug/.build-id/ad/0846b45034ff52f175f07613318a974c5bf190.debug
  -rw-r--r-- root/root      6307 2024-02-02 00:52 ./usr/lib/debug/.build-id/ad/0846b45034ff52f175f07613318a974c5bf190.yaml
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.dwz/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/lib/debug/.dwz/x86_64-linux-gnu/
  -rw-r--r-- root/root     15792 2024-02-02 00:52 ./usr/lib/debug/.dwz/x86_64-linux-gnu/unzip.debug
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/
  drwxr-xr-x root/root         0 2024-02-02 00:52 ./usr/share/doc/
  lrwxrwxrwx root/root         0 2024-02-02 00:52 ./usr/share/doc/unzip-dbgsym -> unzip
  ```

Similarly, the metadata from each `.debug` file (actually an ELF file with debug information)
has been removed, making them essentially identical to the original `.debug` files.
Instead, the package includes `.yaml` files corresponding to each `.debug` file.
Note that the filenames are based on the BuildID's, so they differ with each build.

The following shows the first few dozen lines of the three `.yaml` files.
From these results, we can confirm that the provenance information of each ELF file has been
successfully included in the debug package in YAML format:

```yaml
$ head -20 usr/lib/debug/.build-id/3f/651fe9f8c7e40beea539860aef9689cfc6f4f9.yaml
SourceFiles:
  /home/snagao/src/unzip-6.0:
  - File: unreduce.c
    SHA1: 8a4d010e61dbb691082f8aba66730cd4adcca3c1
  - File: unshrink.c
    SHA1: 29816ed9e4f3392a76045678cc14a33f6655d552
  - File: unzip.c
    SHA1: ae9d9773630b2f1d537f1de549769ed39b1d5de5
  - File: unzip.h
    SHA1: b1e9d52ca7ae76936dcb2c175ec7def191a46576
  - File: unzpriv.h
    SHA1: 7db7e87adcdd4288cb52b417987060bd988c9aa3
  - File: unzvers.h
    SHA1: 78e5390d9dd17971dc7a29eb43fd7084277d92fe
  - File: zip.h
    SHA1: 8d8abe7a4b3c0ba5ec6414562e4f2f41520e81fb
  - File: zipinfo.c
    SHA1: f038797cca43c178801dd5ef24436568b55555dd
  /home/snagao/src/unzip-6.0/unix:
  - File: unix.c
$ head -20 usr/lib/debug/.build-id/52/86e01e3211833017e926a0fba155740f9fe5a8.yaml
SourceFiles:
  /home/snagao/src/unzip-6.0:
  - File: unzip.h
    SHA1: b1e9d52ca7ae76936dcb2c175ec7def191a46576
  - File: unzpriv.h
    SHA1: 7db7e87adcdd4288cb52b417987060bd988c9aa3
  - File: zip.h
    SHA1: 8d8abe7a4b3c0ba5ec6414562e4f2f41520e81fb
  /home/snagao/src/unzip-6.0/unix:
  - File: unxcfg.h
    SHA1: 7fb54a3538642300c1ad27f1b8f047e82a7149b4
  /usr/include:
  - File: locale.h
    SHA1: 5ed60979e46357bea95cba5eeebd82d5e516add0
  - File: signal.h
    SHA1: 8c1b26c724f82828d838e51667f208d7b4c164de
  - File: stdc-predef.h
    SHA1: 2fef05d80514ca0be77efec90bda051cf87d771f
  - File: stdio.h
    SHA1: c7181b48c4194cd122024971527aab4056baf600
$ head -20 usr/lib/debug/.build-id/ad/0846b45034ff52f175f07613318a974c5bf190.yaml
SourceFiles:
  /home/snagao/src/unzip-6.0:
  - File: unzip.c
    SHA1: ae9d9773630b2f1d537f1de549769ed39b1d5de5
  - File: unzip.h
    SHA1: b1e9d52ca7ae76936dcb2c175ec7def191a46576
  - File: unzpriv.h
    SHA1: 7db7e87adcdd4288cb52b417987060bd988c9aa3
  - File: unzvers.h
    SHA1: 78e5390d9dd17971dc7a29eb43fd7084277d92fe
  - File: zip.h
    SHA1: 8d8abe7a4b3c0ba5ec6414562e4f2f41520e81fb
  /home/snagao/src/unzip-6.0/unix:
  - File: unix.c
    SHA1: c8e3fc02d41d405f88992921611fd0aaa8b74271
  - File: unxcfg.h
    SHA1: 7fb54a3538642300c1ad27f1b8f047e82a7149b4
  /usr/include:
  - File: locale.h
    SHA1: 5ed60979e46357bea95cba5eeebd82d5e516add0
```

## Examples of Other Software

By editing the `debian/rules` file with the same approach, you can include provenance
information in the debug package for packages other than **unzip**.

Below are examples for **bzip2** and **openssl**.
Note that the person responsible for creating or maintaining the `debian/rules` file may differ
for each package, so the ways of defining variables and rules may vary.

### bzip2

```diff
 !/usr/bin/make -f
 # debian/rules file for building the Debian GNU/Linux package bzip2.
 # Copyright (C) 1999, 2000, 2001, 2002 Philippe Troin
 # Copyright (C) 2004-2007 Anibal Monsalve Salazar <anibal@debian.org>
 # Copyright 2014 Canonical Ltd.

 include /usr/share/dpkg/architecture.mk
 ifneq ($(DEB_HOST_GNU_TYPE),$(DEB_BUILD_GNU_TYPE))
   CC=$(DEB_HOST_GNU_TYPE)-gcc
 else
   CC=gcc
 endif

+ESSTRA_CORE := -fplugin=/usr/local/share/esstra/esstracore.so
+ESSTRA_UTIL := /usr/local/bin/esstra.py

 DEB_BUILD_MAINT_OPTIONS := hardening=+all
 DEB_CFLAGS_MAINT_APPEND := -Wall -Winline
+DEB_CFLAGS_MAINT_APPEND += $(ESSTRA_CORE)
 DEB_CPPFLAGS_MAINT_APPEND := -D_REENTRANT
    :
  (snip)
    :
 .PHONY: override_dh_installdocs
 override_dh_installdocs:
         dh_installdocs -plibbz2-dev --link-doc=libbz2-1.0
         dh_installdocs --remaining-packages

+.PHONY: override_dh_strip
+override_dh_strip:
+        dh_strip
+        $(ESSTRA_UTIL) rm --ignore-errors `find debian/bzip2/ -type f -executable`
+        for debug in `find debian/.debhelper/bzip2/dbgsym-root/ -name "*.debug"` ; do \
+                yaml=$${debug%.debug}.yaml ; \
+                ($(ESSTRA_UTIL) show --no-comments $$debug > $$yaml && $(ESSTRA_UTIL) rm $$debug) || rm -f $$yaml ; \
+        done
```

### openssl

```diff
 #!/usr/bin/make -f
 # Sample debian.rules file - for GNU Hello (1.3).
 # Copyright 1994,1995 by Ian Jackson.
   :
 (snip)
   :
 include /usr/share/dpkg/architecture.mk
 include /usr/share/dpkg/pkg-info.mk

+ESSTRA_CORE := -fplugin=/usr/local/share/esstra/esstracore.so
+ESSTRA_UTIL := /usr/local/bin/esstra.py

 export DEB_BUILD_MAINT_OPTIONS = hardening=+all future=+lfs
-export DEB_CFLAGS_MAINT_APPEND = -DOPENSSL_TLS_SECURITY_LEVEL=2
+export DEB_CFLAGS_MAINT_APPEND = -DOPENSSL_TLS_SECURITY_LEVEL=2 $(ESSTRA_CORE)

 SHELL=/bin/bash
   :
 (snip)
   :
 override_dh_shlibdeps:
         sed -i '/^udeb: libssl/s/libcrypto3-udeb/libssl3-udeb/' debian/libssl3/DEBIAN/shlibs
         dh_shlibdeps -a -L libssl3

+override_dh_strip:
+        dh_strip
+        $(ESSTRA_UTIL) rm -I `find debian/*/ -type f`
+        for i in `find debian/.debhelper/*/dbgsym-root/ -name "*.debug"` ; do \
+                yaml=$${debug%.debug}.yaml ; \
+                ($(ESSTRA_UTIL) show --no-comments $$i > $$yaml && $(ESSTRA_UTIL) rm $$i) || rm -f $$yaml ; \
+        done
```

## Discussion

This list below outlines the points that need to be considered, discussed, and addressed in the
future based on the content of this document:

* Need to identify and fix The cause of the LTO issue in the ESSTRA Core.
* In this demo, provenance information is separated into `.yaml` files, but it can also be keep
  within binaries or `.debug` files.
* Including provenance information in binaries or `.debug` files increases file sizes.
* Regardless of how you include provenance information, the package size will increase.
* Therefore, need to determine the most preferable format to distribute provenance information
  from a distributor's viewpoint.
* Also, need to define workflows and develop tools to utilize the distributed provenance
  information effectively.
* Since the current ESSTRA Core supports only gcc/g++, need to establish ways to identify
  provenance information for other compilers and languages (e.g., LLVM, Rust, Go, Python) and
  develop a unified provenance information format.
* Provenance information should make SBOM generation easier. Need to consider how to achieve
  this.
* The current ESSTRA Core generates provenance information from the absolute path of the build
  environment, which includes personal information such as `/home/<username>/`. Need to remove
  such information.
* Need to establish ways to apply the approach described in this document to other Linux
  distributions that are not Debian-based.

## Summary and Conclusion

In this document, we focused on Debian, one of the most popular Linux distributions, to
demonstrate the practical application of ESSTRA.
From the perspective of a Debian distributor, we illustrated a specific way to include
provenance information obtained with ESSTRA in Debian debug packages.

By modifying the `debian/rules` file of the source package to accomplish the following three
points, the goal can be achieved:

1. Add options to apply the ESSTRA Core to the options passed to gcc/g++.
2. Override `dh_strip` to generate `.yaml` files containing provenance information to include
   in the debug package using the ESSTRA Utility.
3. Remove unnecessary provenance information embedded in binary files and `.debug` files using
   the ESSTRA Utility.

While we used **unzip** as an example to explain the process step-by-step, we also showed
that this method is applicable to other software such as **bunzip2** and **openssl**.

Finally, based on this study, we listed points for future discussion and resolution.
