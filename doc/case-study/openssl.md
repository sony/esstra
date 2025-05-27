# Demo of ESSTRA Usage on OpenSSL Package

In this demo, we will explain how to use ESSTRA with a popular open-source package
"OpenSSL". This document is structured as a step-by-step guide, allowing you to easily
understand the basic operations of ESSTRA by following each step in order.

First, we will build the OpenSSL package using the ESSTRA Core to generate the ELF
files. These ELF files include metadata containing information about all the source files
involved in the compilation, such as absolute paths and checksums. We will verify this using
the ESSTRA Utility.

Next, we will demonstrate how to use the feature of the ESSTRA Utility that adds
license information of source files to the metadata. In this demo, we will
use the open-source software license analysis tool
[FOSSology](https://github.com/fossology/fossology)
to scan the source code for licenses and generate a license information
file. We will then update the metadata using the ESSTRA Utility based on this
information and verify that the license information has been correctly added to
the metadata.

The operational procedures for the license analysis tool FOSSology are also explained in this
guide.

Finally, we calculate the effectiveness of ESSTRA in license analysis activities.

## ESSTRA Build Instructions

### Build and Install ESSTRA

Before building the ESSTRA Core (`esstracore.so`) GCC plugin, you need to install a package on
your system. For Debian/Ubuntu, first check the version of GCC:

```sh
$ gcc --version
gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0
...
```

In this case, the major version is 11, so install the package `gcc-11-plugin-dev`:

```sh
$ sudo apt install gcc-11-plugin-dev
```

Next, run `make` in the top directory:

```sh
$ make
```

If there are no errors, the build is complete. Then, run:

```sh
$ sudo make install
```

and `esstracore.so` will be installed in `/usr/local/lib/gcc/x86_64-linux-gnu/<gcc-major-version>/plugin/`.

### Install a Spec File

```sh
$ sudo make install-specs
```

This command installs a
[GCC spec file](https://gcc.gnu.org/onlinedocs/gcc/Spec-Files.html)
on your system which enables the option:

* `-fplugin=/usr/local/lib/gcc/x86_64-linux-gnu/<gcc-major-version>/plugin/esstracore.so`

by default.

This enables `esstracore.so` to be invoked whenever `gcc/g++` is used.

To disable this, type:

```sh
$ sudo make uninstall-specs
```

to remove the spec file.

## Build OpenSSL Source with ESSTRA Core

### Download the Source

Download the source of OpenSSL from <https://github.com/openssl/openssl/releases/latest>.
The version, at the time of writing, is 3.4.1, which is used for the demo.

```bash
$ wget https://github.com/openssl/openssl/releases/download/openssl-3.4.1/openssl-3.4.1.tar.gz
$ tar -xf openssl-3.4.1.tar.gz
```

### Build OpenSSL

We will follow the
[official build instructions](https://github.com/openssl/openssl/blob/ddd7ecb04bcea5c13be3c73f3dc1a101087cdf24/INSTALL.md)
to build OpenSSL.

#### Install Prerequisites

For Debian/Ubuntu, the following command installs the required prerequisites mentioned in the
[documentation](https://github.com/openssl/openssl/blob/ddd7ecb04bcea5c13be3c73f3dc1a101087cdf24/INSTALL.md):

```sh
$ sudo apt install -y perl build-essential
```

#### Build OpenSSL

```sh
$ cd openssl-3.4.1
openssl-3.4.1$ ./Configure no-tests
openssl-3.4.1$ make
```

### Find ELF Files Generated During the Build

We will use `BuildID` to find the ELF files.
A `BuildID` is a unique identifier assigned to a specific build of a binary, embedded within the ELF file itself.

```sh
openssl-3.4.1$ find ./ -type f -exec sh -c "file '{}' | grep -q 'BuildID'" \; -print
./libssl.so.3
./libcrypto.so.3
./util/quicserver
./engines/ossltest.so
./engines/padlock.so
./engines/loader_attic.so
./engines/afalg.so
./engines/capi.so
./engines/dasync.so
./apps/openssl
./providers/legacy.so

```

### Run ESSTRA Util Script to Get Source Files Used in the ELF

#### Prerequisite

Since the ESSTRA Utility depends on the [PyYAML](https://pyyaml.org/)
module to handle YAML data, you may need to install it by typing:

```sh
$ pip install pyyaml
or
$ sudo apt install python3-yaml
```

#### Run Util Script on the Generated ELF Files.

For the demonstration, we will use a single ELF file `openssl-3.4.1/apps/openssl` for
simplicity.

The information embedded by ESSTRA increases the size of the ELF files. We can reduce the size
of ELF files by eliminating duplication in the embedded information as below:

```sh
esstra$ du -sh ../openssl-3.4.1/apps/openssl
2.6M    ../openssl-3.4.1/apps/openssl

esstra$ esstra.py shrink ../openssl-3.4.1/apps/openssl
* processing '../openssl-3.4.1/apps/openssl'...
* done.

esstra$ du -sh ../openssl-3.4.1/apps/openssl
1.3M    ../openssl-3.4.1/apps/openssl
```

Next, display the information embedded by ESSTRA:

```sh
esstra$ esstra.py show ../openssl-3.4.1/apps/openssl
```

This will give an output as follows:

```yaml
#
# BinaryFileName: ../openssl-3.4.1/apps/openssl
# BinaryPath: /home/openssl-3.4.1/apps/openssl
#
SourceFiles:
  /home/openssl-3.4.1/apps:
  - File: info.c
    SHA1: 51aa1d9f96d789cd3fe178fd67ca758c4ab877ee
  - File: kdf.c
    SHA1: 49ba6552b654317b940599cfb964e7c0397c7121
  - File: list.c
    SHA1: 13ec3cdb556dfd35d723bd460c3253718f5358d4
  - File: mac.c
    SHA1: c295c80b647ff6a6667caa603f89ad436c29fd93
  - File: nseq.c
    SHA1: e4b69588cb1ebba0d084ea3f44bc2cd3ff9ff0a5
  - File: ocsp.c
    SHA1: 097dd05d023351fa1a418bf2988b544de77225f3
  - File: openssl.c
    SHA1: def2983007e42be1f31ebb31df23f3f51266ce71
  - File: passwd.c
    SHA1: 06bfce3822d37ec832f3eb35f4caa7f8e72cd2de
  - File: pkcs12.c
    SHA1: 0caa984c8de334109570a7a8c9bf927ba5386077
  - File: pkcs7.c
    SHA1: 5b6f326f2b8e53a0a6a20b6e37f69453a9cea3ce
  - File: pkcs8.c
    SHA1: 3c394e3f4567b67bd5b1c469d5ef14b7e00dab8b
  - File: pkey.c
    SHA1: 7e0fa21b1ee1d8e4e64e78ab91393a77c048f305
        :
      (snip)
        :
```

> [!NOTE]
> You can provide multiple ELF files as arguments to the ESSTRA Utility.

The complete output in YAML format can be found in
[yaml-report](./output-examples/openssl/esstra_scan_on_openssl_elf.yaml).

## License Analysis Using FOSSology

The ESSTRA Utility includes a feature that adds license information to the metadata of each
file.
Below are the steps to add the license information of the OpenSSL source files to the metadata
of the binaries/ELFs (generated during build) using this feature.

As a preliminary step, you need to create a document in the
[SPDX 2.3 tag-value format](https://spdx.github.io/spdx-spec/v2.3/)
that includes the license information of the source files.
Here, we will demonstrate how to use the open-source software license analysis tool
[FOSSology](https://github.com/fossology/fossology) to achieve this.

### Starting the FOSSology Server

We will use the FOSSology container image provided on
[Docker Hub](https://hub.docker.com/).

We will be using version 4.1.0 for this demo.

Pull the FOSSology container image with the following command:

```sh
$ docker pull fossology/fossology:4.1.0
```

Once the image is successful pulled, start the FOSSology server with the following command:

```sh
$ docker run -p 8081:80 fossology/fossology:4.1.0
```

This will allow you to access the FOSSology server via port 8081 on the
host. Open a web browser and go to:

* `http://<host_ip_addr>:8081/repo`

When accessing FOSSology, make sure to append `/repo` to the URL.

Then the FOSSology startup screen will appear in your browser.

### Analyzing Source Code with FOSSology

Refer to
[this guide](https://github.com/sony/esstra/blob/main/samples/hello/README_FOSSOLOGY.md)
for a step-by-step manual approach to analyze the source code with FOSSology and generate a
report.

Here, we will use another approach to analyze the source code with FOSSology and generate a
report using the tool [FOSSology.REST.shell](https://github.com/fossology/FOSSology.REST.shell)

#### Download FOSSology.REST.shell and Install its Prerequisites

```sh
$ git clone https://github.com/fossology/FOSSology.REST.shell.git
$ apt install -y jq curl
```

#### Upload and Scan the OpenSSL Source Files

```sh
FOSSology.REST.shell$ ./upload-rest.sh -n fossy -p fossy -r http://localhost:8081/repo/api/v1 -i ../openssl-3.4.1.tar.gz
Rest Client: Version 1.3
  :
(snip)
  :
Upload file: ../openssl-3.4.1.tar.gz

- Upload ID: 2
- Job ID   : 5
- Group ID : 3
- Job ETA  : 0

Unpack job: started
  :
(snip)
  :
```

We will use the Upload ID provided in the log to download the report.

#### Download the Scan Report

```sh
FOSSology.REST.shell$ ./download-rest.sh -F spdx2tv -r http://localhost:8081/repo/api/v1  -u 2 -n fossy -p fossy
  :
(snip)
  :
======================================
=== Download report
======================================

Output directory: /home/FOSSology.REST.shell
Downloading file
Downloaded file: /home/FOSSology.REST.shell/SPDX2TV_openssl-3.4.1.tar.gz.spdx

======================================
=== End
======================================
```

Below is a portion of the downloaded file
[`SPDX2TV_openssl-3.4.1.tar.gz.spdx`](./output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz.spdx):

```yaml
SPDXVersion: SPDX-2.2
DataLicense: CC0-1.0

##-------------------------
## Document Information
##-------------------------

DocumentNamespace: http://1f9d9e80ed71/repo/SPDX2TV_openssl-3.4.1.tar.gz.spdx
DocumentName: /srv/fossology/repository/report
SPDXID: SPDXRef-DOCUMENT

##-------------------------
## Creation Information
##-------------------------

Creator: Tool: spdx2
Creator: Person: fossy (y)
CreatorComment: <text>
This document was created using license information and a generator from Fossology.
</text>
Created: 2025-03-05T08:31:25Z
LicenseListVersion: 2.6

##-------------------------
## Package Information
##-------------------------


PackageName: openssl-3.4.1.tar.gz
PackageFileName: openssl-3.4.1.tar.gz

  :
(snip)
  :
```

## Adding License Information to Metadata

To add license information to the metadata in the binary using the ESSTRA Utility
with the
[`SPDX2TV_openssl-3.4.1.tar.gz.spdx`](./output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz.spdx)
file downloaded from FOSSology, run the following command:

```sh
esstra$ esstra.py update ../openssl-3.4.1/apps/openssl -i SPDX2TV_openssl-3.4.1.tar.gz.spdx
* processing '../openssl-3.4.1/apps/openssl'...
* done.
```

If no errors occur, the process is successful. To display the metadata content
of the ELF `openssl-3.4.1/apps/openssl`, run:

```sh
esstra$ esstra.py show ../openssl-3.4.1/apps/openssl
```

The result will be as follows:

```yaml
#
# BinaryFileName: ../openssl-3.4.1/apps/openssl
# BinaryPath: /home/openssl-3.4.1/apps/openssl
#
SourceFiles:
  /home/openssl-3.4.1/apps:
  - File: info.c
    LicenseInfo:
    - OpenSSL
    - Apache-2.0
    SHA1: 51aa1d9f96d789cd3fe178fd67ca758c4ab877ee
  - File: kdf.c
    LicenseInfo:
    - Apache-2.0
    - OpenSSL
    SHA1: 49ba6552b654317b940599cfb964e7c0397c7121
  - File: list.c
    LicenseInfo:
    - OpenSSL
    - Apache-2.0
    SHA1: 13ec3cdb556dfd35d723bd460c3253718f5358d4
  - File: mac.c
    LicenseInfo:
    - OpenSSL
    - Apache-2.0
    SHA1: c295c80b647ff6a6667caa603f89ad436c29fd93
  - File: nseq.c
    LicenseInfo:
    - Apache-2.0
    - OpenSSL
```

The complete output of the ESSTRA Utility, including license information, can be found
[here](./output-examples/openssl/esstra_show_openssl_result_with_license_info.yaml).

Please note that the file
[`SPDX2TV_openssl-3.4.1.tar.gz.spdx`](./output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz.spdx),
generated previously by FOSSology, only contains license information
for the files present in the
[OpenSSL repository](https://github.com/openssl/openssl).
Therefore, license information will not be assigned to files
other than OpenSSL source files in the metadata of the ELF `./openssl-3.4.1/apps/openssl`.

To add license information for those files, you can use FOSSology or similar tools to identify
their licenses and generate an SPDX tag-value format file.
By passing the file to the ESSTRA Utility, you can add license information to the metadata in
the binary.

## Analyze Effectiveness of ESSTRA for OpenSSL

One way to measure effectiveness is to consider the reduction in the number of files that
require manual review. This reduction not only saves time but also enhances quality by reducing
human error.

### Get All Files in the Source Directory

```sh
openssl-3.4.1$ find ./ -type f | wc -l
9625
```

### Calculate Unique Source Files Given by the ESSTRA

Run the ESSTRA Utility on all the generated ELF files and redirect output to a file.

```sh
openssl-3.4.1$ esstra.py show $(find ./ -type f -exec sh -c "file '{}' | grep -q 'BuildID'" \; -print) >../esstra_scan_result.yaml
```

The generated output above contains the details of all the source files used during the build,
including the system files.
To find the unique OpenSSL source files used during the build, we exclude all non-OpenSSL
source files.

Below, we split the details of all ELFs in `esstra_scan_result.yaml` into separate YAML files
for each ELF and count the 'SHA1' under the OpenSSL source directory to get unique source files
used in all the ELFs.

```sh
$ awk '/^SourceFiles:/{
        if(output) close(output);
        output = "elf_output_" ++i ".yaml"
   }
   output {
        print > output
 }' esstra_scan_result.yaml

$ ls elf_output_*
elf_output_1.yaml   elf_output_11.yaml  elf_output_2.yaml  elf_output_4.yaml  elf_output_6.yaml  elf_output_8.yaml
elf_output_10.yaml  elf_output_12.yaml  elf_output_3.yaml  elf_output_5.yaml  elf_output_7.yaml  elf_output_9.yaml

$ yq '(.SourceFiles | to_entries | map(select(.key == "/home/openssl-3.4.1/*") | .value) | flatten | unique_by(.SHA1) | .[].SHA1)' elf_output_* | sort -u | wc -l
1606
```

Thus, `1606` unique OpenSSL source files were used during the build to generate the ELF files.

### Calculating Effectiveness of ESSTRA

**The percentage of source files reported by ESSTRA can be calculated as follows:**

```math
\frac{\text{count of unique source files}}{\text{count of all source files}} \times 100
= (1606 / 9625) * 100
= 16.685 %
```

This means that out of all the files, only **16.685%** were used in the generated ELFs.

## Summary

In this demo, we first compiled the OpenSSL source files using the ESSTRA Core
to generate the ELFs and confirmed that the metadata in the generated ELF
includes information about all the files involved in the compilation.

Next, we used the ESSTRA Utility to add license information to the metadata of the generated ELF.
To generate the license information, we demonstrated how to use the
open-source license analysis tool
[FOSSology](https://github.com/fossology/fossology)
to scan the licenses of all the files in the
[OpenSSL repository](https://github.com/openssl/openssl)
and generate an SPDX 2.3 tag-value format file.

Finally, we analyzed the effectiveness of ESSTRA in the license analysis of the ELFs.
