# Demo of ESSTRA Usage on OpenSSL Package

In this demo, we will explain how to use ESSTRA with a popular open-source package
"OpenSSL". This document is structured as a step-by-step guide, allowing you to easily
understand the basic operations of ESSTRA by following each step in order.

First, we will build the OpenSSL package using the ESSTRA Core to generate the ELF
files. These ELF files include metadata containing information about all the source files
involved in the compilation, such as absolute paths and checksums. We will verify this using
ESSTRA Utility.

Next, we will demonstrate how to use the feature of ESSTRA Utility that adds
license information of source files to the metadata. In this demo, we will
use the following open-source software license analysis tools to scan the source code for licenses and generate a license information
file.
* [FOSSology](https://github.com/fossology/fossology)
* [ScanCode toolkit](https://github.com/aboutcode-org/scancode-toolkit)

We will then update the metadata using ESSTRA Utility based on this
information and verify that the license information has been correctly added to 
the metadata.

The operational procedures for the above mentioned license analysis tools are also explained in this
guide.

Finally, we calculate the effectiveness of ESSTRA in license analysis activities.

## ESSTRA Build Instructions

### Build and Install ESSTRA

Before building ESSTRA Core (`esstracore.so`) GCC plugin, you need to install a package on your
system. For Debian/Ubuntu, first check the version of GCC:

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

and `esstracore.so` will be installed in `/usr/local/lib/gcc/<gcc-arch>/<gcc-major-version>/plugin/`.

### Install a Spec File

```sh
$ sudo make install-specs
```

This command installs a
[GCC spec file](https://gcc.gnu.org/onlinedocs/gcc/Spec-Files.html)
on your system which enables the option:

* `-fplugin=/usr/local/lib/gcc/<gcc-arch>/<gcc-major-version>/plugin/esstracore.so`

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
A `BuildID` is a unique identifier assigned to a specific build of a binary, embedded within
the ELF file itself.

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

Since ESSTRA Utility depends on the [PyYAML](https://pyyaml.org/) module to handle YAML data,
you may need to install it by typing:

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
$ du -sh ../openssl-3.4.1/apps/openssl
2.6M    ../openssl-3.4.1/apps/openssl

$ esstra shrink ../openssl-3.4.1/apps/openssl
* processing '../openssl-3.4.1/apps/openssl'...
* done.

$ du -sh ../openssl-3.4.1/apps/openssl
1.3M    ../openssl-3.4.1/apps/openssl
```

Next, display the information embedded by ESSTRA:

```sh
$ esstra show ../openssl-3.4.1/apps/openssl
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
> You can provide multiple ELF files as arguments to ESSTRA Utility.

The complete output in YAML format can be found in
[yaml-report](./output-examples/openssl/esstra_scan_on_openssl_elf.yaml).

## License Analysis

ESSTRA Utility includes a feature that adds license information to the metadata of each file.
Below are the steps to add the license information of the OpenSSL source files to the metadata
of the binaries/ELFs (generated during build) using this feature.

This can be done by any tool that can scan the source code and generate a spdx file. Here, we demostrate using FOSSology and ScanCode toolkit.

### Using FOSSology

As a preliminary step, you need to create a document in the
[SPDX 2.3 tag-value format](https://spdx.github.io/spdx-spec/v2.3/)
that includes the license information of the source files.
Here, we will demonstrate how to use the open-source software license analysis tool
[FOSSology](https://github.com/fossology/fossology) to achieve this.

#### Starting the FOSSology Server

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

#### Analyzing Source Code

Refer to
[this guide](https://github.com/sony/esstra/blob/main/samples/hello/README_FOSSOLOGY.md)
for a step-by-step manual approach to analyze the source code with FOSSology and generate a
report.

Here, we will use another approach to analyze the source code with FOSSology and generate a
report using the tool [FOSSology.REST.shell](https://github.com/fossology/FOSSology.REST.shell)

#### Download FOSSology.REST.shell and Install its Prerequisites

```sh
$ git clone https://github.com/fossology/FOSSology.REST.shell.git
$ sudo apt install -y jq curl
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
Downloaded file: /home/FOSSology.REST.shell/SPDX2TV_openssl-3.4.1.tar.gz_fossology.spdx

======================================
=== End
======================================
```

Below is a portion of the downloaded file
[`SPDX2TV_openssl-3.4.1.tar.gz_fossology.spdx`](./output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz_fossology.spdx):

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

### Using ScanCode toolkit

Here, we will demonstrate how to use the open-source software license analysis tool
[ScanCode toolkit](https://github.com/aboutcode-org/scancode-toolkit) to generate a document in the
[SPDX 2.2 tag-value format](https://spdx.github.io/spdx-spec/v2.2.2/)
that includes the license information of the source files.

#### ScanCode toolkit setup

We will install the tool using the source code from the [official repository](https://github.com/aboutcode-org/scancode-toolkit).

ScanCode toolkit requires a Python version between 3.9 to 3.13 to work properly.

```sh
$ sudo apt update
$ sudo apt install python3 python3-pip
```

We will be using version [v32.4.1](https://github.com/aboutcode-org/scancode-toolkit/releases/tag/v32.4.1) for this demo.

Clone the repo with the following command:

```sh
$ git clone https://github.com/aboutcode-org/scancode-toolkit.git -b v32.4.1
```

Once the repo is successfully cloned, execute the following commands to install the tool.

```sh
$ cd scancode-toolkit
$ ./configure
$ source venv/bin/activate
```

This will install it for local and development usage.

#### Analyzing Source Code with ScanCode toolkit

Once ScanCode toolkit is installed, we can start a scan with the following steps.

Since the tool doesn't support archives yet, we have to untar the files to be scanned.

Here we are using a fresh copy of OpenSSL package to get started with.

```sh
$ wget https://github.com/openssl/openssl/releases/download/openssl-3.4.1/openssl-3.4.1.tar.gz
$ tar -xf openssl-3.4.1.tar.gz
```
After the untar has been completed, use the following command to scan and generate the SPDX report.

```sh
$ scancode -clpeui --spdx-tv SPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx openssl-3.4.1
```
Following is a sample output of the above command.

```sh
Setup plugins...
Collect file inventory...
Scan files for: info, packages, licenses, copyrights, emails, urls with 19 process(es)...
[####################] 10796                                                     
Scanning done.
Summary:        info, packages, licenses, copyrights, emails, urls with 19 process(es)
Errors count:   0
Scan Speed:     20.83 files/sec. 248.46 KB/sec.
Initial counts: 5681 resource(s): 5398 file(s) and 283 directorie(s) 
Final counts:   5681 resource(s): 5398 file(s) and 283 directorie(s) for 62.89 MB
Timings:
  scan_start: 2025-10-06T125159.852780
  scan_end:   2025-10-06T125621.466463
  setup_scan:licenses: 1.73s
  setup: 1.73s
  inventory: 0.33s
  scan:packages: 0.26s
  scan:licenses: 0.24s
  scan: 259.21s
  output:spdx-tv: 1.28s
  output: 1.28s
  total: 262.97s
Removing temporary files...done.
```

Refer to
[this guide](https://scancode-toolkit.readthedocs.io/en/stable/tutorials/how_to_run_a_scan.html)
for a step-by-step manual approach to analyze the source code with ScanCode toolkit and generate a
report.


#### Getting the Scan Report

Since we have already defined the report name and path while starting the scan, the same will be available at the defined location once the scan is complete.

Below is a portion of the downloaded file
[`SPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx`](./output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx):

```yaml
## Document Information
SPDXVersion: SPDX-2.2
DataLicense: CC0-1.0
SPDXID: SPDXRef-DOCUMENT
DocumentName: SPDX Document created by ScanCode Toolkit
DocumentNamespace: http://spdx.org/spdxdocs/project-bd64978c-c6c5-4d01-ad39-5a573360edda
DocumentComment: <text>Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied. No content created from
ScanCode should be considered or used as legal advice. Consult an Attorney
for any legal advice.
ScanCode is a free software code scanning tool from nexB Inc. and others.
Visit https://github.com/nexB/scancode-toolkit/ for support and download.
SPDX License List: 3.27</text>

## Creation Information
LicenseListVersion: 3.27
Creator: Tool: scancode-toolkit 32.4.1
Created: 2025-09-24T08:58:09Z

  :
(snip)
  :
```

### Adding License Information to Metadata

To add license information to the metadata in the binary using ESSTRA Utility with the generated spdx files from FOSSology or ScanCode toolkit, run the following command:

```sh
$ esstra update ../openssl-3.4.1/apps/openssl -i ${SPDX_FILE}
* processing '../openssl-3.4.1/apps/openssl'...
* done. 
```

Where `${SPDX_FILE}` is one of the following:
 * [`SPDX2TV_openssl-3.4.1.tar.gz_fossology.spdx`](./output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz_fossology.spdx)
 * [`SPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx`](./output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx)

If no errors occur, the process is successful. To display the metadata content
of the ELF `openssl-3.4.1/apps/openssl`, run:

```sh
$ esstra show ../openssl-3.4.1/apps/openssl
```

The results will be as follows:

<table>
 <tr>
 <td> FOSSology </td> <td> ScanCode toolkit </td>
 </tr>
 <tr>
 <td>
 
 ```yaml
 #
 # BinaryFileName: ../openssl-3.4.1/apps/openssl
 # BinaryPath: /esstra/openssl-3.4.1/apps/openssl
 #
 Headers:
   ToolName: ESSTRA Core
   ToolVersion: 0.4.0
   DataFormatVersion: 0.1.0
   InputFileNames:
   - apps/lib/cmp_mock_srv.c
   - apps/asn1parse.c
   - apps/ca.c
   - apps/ciphers.c
   - apps/cmp.c
   - apps/cms.c
   - apps/crl.c
   - apps/crl2pkcs7.c
   - apps/dgst.c
   - apps/dhparam.c
   :
 (snip)
   :
 SourceFiles:
 - Directory: /esstra/openssl-3.4.1/apps
   Files:
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
 



  (snip)
 
 ```
 
 
 </td>
 <td>
 
 ```yaml
  #
  # BinaryFileName: openssl-3.4.1/apps/openssl
  # BinaryPath: /openssl/openssl-3.4.1/apps/openssl
  #
  Headers:
    ToolName: ESSTRA Core
    ToolVersion: 0.4.0
    DataFormatVersion: 0.1.0
    InputFileNames:
    - apps/lib/cmp_mock_srv.c
    - apps/asn1parse.c
    - apps/ca.c
    - apps/ciphers.c
    - apps/cmp.c
    - apps/cms.c
    - apps/crl.c
    - apps/crl2pkcs7.c
    - apps/dgst.c
    - apps/dhparam.c
    :
  (snip)
    :
  SourceFiles:
  - Directory: /openssl/openssl-3.4.1/apps
    Files:
    - File: info.c
      SHA1: 51aa1d9f96d789cd3fe178fd67ca758c4ab877ee
      LicenseInfo:
      - MIT
      - Apache-2.0
      - OpenSSL
    - File: kdf.c
      SHA1: 49ba6552b654317b940599cfb964e7c0397c7121
      LicenseInfo:
      - MIT
      - Apache-2.0
      - OpenSSL
    - File: list.c
      SHA1: 13ec3cdb556dfd35d723bd460c3253718f5358d4
      LicenseInfo:
      - Apache-2.0
      - OpenSSL
    - File: mac.c
      SHA1: c295c80b647ff6a6667caa603f89ad436c29fd93
      LicenseInfo:
      - MIT
      - Apache-2.0
      - OpenSSL
    
    (snip)
  ```
 
 </td>
 </tr>
 </table>

> [!NOTE]
> It can be observed that ScanCode toolkit has detected some extra licenses for some of the source files.

The complete output of ESSTRA Utility, including license information, can be found below

<table>
<tr>
<td>FOSSology</td> <td>ScanCode toolkit</td>
</tr>
<tr>
<td> <a href="./output-examples/openssl/esstra_show_openssl_fossology.yaml"> esstra_show_openssl_fossology </a> </td> <td> <a href='./output-examples/openssl/esstra_show_openssl_scancode.yaml'> esstra_show_openssl_scancode </a></td>
</tr>
</table>

Please note that the SPDX files generated previously by ScanCode toolkit and FOSSology contain only license information
for the files present in the
[OpenSSL repository](https://github.com/openssl/openssl).
Therefore, license information will not be assigned to files
other than OpenSSL source files in the metadata of the ELF `./openssl-3.4.1/apps/openssl`.

To add license information for those files, you can use ScanCode toolkit or FOSSology or similar tools to identify their licenses and generate an SPDX tag-value format file.
By passing the file to ESSTRA Utility, you can add license information to the metadata in the binary.

## Analyze Effectiveness of ESSTRA for OpenSSL

One way to measure effectiveness is to consider the reduction in the number of files that
require manual review. This reduction not only saves time but also enhances quality by reducing
human error.

### Get All Files in the Source Directory

```sh
openssl-3.4.1$ find ./ -type f | wc -l
9625
```

### Calculate Unique Source Files Given by ESSTRA

Run ESSTRA Utility on all the generated ELF files and redirect output to a file.

```sh
openssl-3.4.1$ esstra show $(find ./ -type f -exec sh -c "file '{}' | grep -q 'BuildID'" \; -print) >../esstra_scan_result.yaml
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

In this demo, we first compiled the OpenSSL source files using ESSTRA Core 
to generate the ELFs and confirmed that the metadata in the generated ELF includes information about all the files involved in the compilation.

Next, we used ESSTRA Utility to add license information to the metadata of the generated ELF.
To generate the license information, we demonstrated how to use the following open-source license analysis tools to scan the licenses of all the files in the
[OpenSSL repository](https://github.com/openssl/openssl)
and generate SPDX tag-value format files:
* [FOSSology](https://github.com/fossology/fossology)
* [ScanCode toolkit](https://github.com/aboutcode-org/scancode-toolkit)

Finally, we analyzed the effectiveness of ESSTRA in the license analysis of the ELFs.