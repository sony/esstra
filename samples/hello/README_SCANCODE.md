# License Analysis Using ScanCode toolkit

This document explains how to generate a license information file in the
[SPDX 2.2 tag-value format](https://spdx.github.io/spdx-spec/v2.2.2/)
using the open-source software license analysis tool
[ScanCode toolkit](https://github.com/aboutcode-org/scancode-toolkit).

Specifically, it details the analysis of the
[entire ESSTRA repository](https://github.com/sony/esstra)
with ScanCode toolkit, resulting in the generation of an SPDX 2.2 tag-value format file,
[`SPDX2TV_esstra_SCANCODE.spdx`](../output-examples/SPDX2TV_esstra_scancode.spdx).

By providing this file to the
[ESSTRA Utility](/util/README.md),
you can associate license information with each file's information in the
metadata embedded in the binary.

## Setup the ScanCode toolkit

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

## Analyzing Source Code with ScanCode toolkit

The reason for explaining how to use ScanCode toolkit in this document is to identify
the licenses of some files included in the samples. However, for simplicity, we
will scan the entire [ESSTRA GitHub repository](https://github.com/sony/esstra)
and generate a single license information file that can be used for all samples.

First, we need to download the ESSTRA source code. Here we'll be downloading the latest version of ESSTRA.

```sh
$ wget https://github.com/sony/esstra/archive/refs/heads/main.zip -O esstra-main.zip
```

Since the tool doesn't support archives yet, we have to untar the files to be scanned.

```sh
$ unzip esstra-main.zip
```

After the untar has been completed, use the following command to scan and generate the SPDX report.

```sh
$ scancode -clpeui --spdx-tv SSPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx esstra-main
```

Here is a breakdown of the scan options used in the above command.

* **-c** for --copyright 
* **-l** for --license
* **-p** for --package
* **-e** for --email
* **-u** for --url
* **-i** for --info
* **--spdx-tv** for SPDX/tag-value file name
* **esstra-main** is the directory to be scanned here

If required these options can be modified. Additional information is present in [here](https://scancode-toolkit.readthedocs.io/en/stable/cli-reference/list-options.html#all-basic-scan-options).

Here is the sample stdlog of the scan command.

```sh
$ scancode -clpeui --spdx-tv SPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx esstra-main

Setup plugins...
Collect file inventory...
Scan files for: info, packages, licenses, copyrights, emails, urls with 19 process(es)...
[####################] 110
Scanning done.
Some files failed to scan properly:
Path: esstra-0.4.0/doc/case-study/output-examples/openssl/SPDX2TV_openssl-3.4.1.tar.gz_scancode.spdx
Summary:        info, packages, licenses, copyrights, emails, urls with 19 process(es)
Errors count:   1
Scan Speed:     0.42 files/sec. 39.83 KB/sec.
Initial counts: 76 resource(s): 55 file(s) and 21 directorie(s)
(snip)
.
.
.
Removing temporary files...done.
```

## Getting the ScanCode toolkit Scan Results

Once the scan is complete, the report can be obtained in the same location as provided in the scan command.

Here we have the report as a SPDX tag-value format file named
[`SPDX2TV_esstra_SCANCODE.spdx`](../output-examples/SPDX2TV_esstra_scancode.spdx).

Below is a portion of the downloaded file `SPDX2TV_esstra_SCANCODE.spdx`:

```yaml
## Document Information
SPDXVersion: SPDX-2.2
DataLicense: CC0-1.0
SPDXID: SPDXRef-DOCUMENT
DocumentName: SPDX Document created by ScanCode Toolkit
DocumentNamespace: http://spdx.org/spdxdocs/esstra_0_4_0-457736b2-db33-4206-9068-e23752f8a513
DocumentComment: <text>Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied. No content created from
ScanCode should be considered or used as legal advice. Consult an Attorney
for any legal advice.
ScanCode is a free software code scanning tool from nexB Inc. and others.
Visit https://github.com/nexB/scancode-toolkit/ for support and download.
SPDX License List: 3.27</text>

## Creation Information
LicenseListVersion: 3.27
Creator: Tool: scancode-toolkit v32.4.1-16-g93a2d69943
Created: 2025-10-27T10:23:36Z


## File Information
FileName: ./esstra-0.4.0/samples/hello/hello.c
SPDXID: SPDXRef-50
FileChecksum: SHA1: 4bbee85215cbcb6a4f1625e4851cca19b0d3f6e2
LicenseConcluded: NOASSERTION
LicenseInfoInFile: MIT
FileCopyrightText: <text>Copyright 2024-2025 Sony Group Corporation
.
.
(snip)

```

This file contains various pieces of information, however, you can see that the
information of the file `hello.c` includes a line `LicenseInfoInFile: MIT`.

## Summary

This document has demonstrated how to analyze the entire repository using the
license analysis tool
[ScanCode toolkit](https://github.com/aboutcode-org/scancode-toolkit)
and generate a file in the SPDX 2.2 tag-value format as a result, named
[`SPDX2TV_esstra_SCANCODE.spdx`](../output-examples/SPDX2TV_esstra_scancode.spdx).
