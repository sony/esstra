# Integrating ESSTRA in the Linux Kernel and Analyzing the Impact of SPDX-License-Identifier

## 1. Overview

This document provides a comprehensive guide for building the Linux kernel with integrated **ESSTRA** metadata. It covers the entire workflow, from setting up the environment and modifying the kernel source to performing the build and integrating [`SPDX-License-Identifier`](https://spdx.dev/learn/handling-license-info/) information. Finally, it analyzes the impact of `SPDX-License-Identifier` on improving the accuracy of license detection.


## 2. Prerequisites

### Build Environment

* **Operating System**: **Ubuntu 22.04.5 LTS**

### Source Files

* **Linux Kernel**: Version `6.8.0-79-generic`
  * Please note that an updated report using the latest stable version will be provided in the future.

* **ESSTRA**: Version `0.4.0`

### FOSSology Analysis (SPDX Files)

The SPDX files can be generated from a [**FOSSology**](https://github.com/fossology/fossology) scan of the kernel source. In this document, we use the results from the following two analysis patterns. Refer [section 5.3](#53-generating-an-spdx-file-with-fossology) for more details.

* Only [**Ojo**](https://fossology.github.io/d9/d3c/ojo.html) agent:
  * This agent uses regular expressions to find out `SPDX-License-Identifier` from a file.

  * For example, refer to top of the file `linux-hwe-6.8-6.8.0/drivers/amba/bus.c`

    ```sh
    linux-hwe-6.8-6.8.0$ head -5 drivers/amba/bus.c
    // SPDX-License-Identifier: GPL-2.0-only
    /*
     *  linux/arch/arm/common/amba.c
     *
     *  Copyright (C) 2003 Deep Blue Solutions Ltd, All Rights Reserved.
    ```

    **Ojo** agent detects the license as `GPL-2.0-only`.

* Only [**Monk**](https://github.com/fossology/fossology/wiki/Monk) and [**Nomos**](https://fossology.github.io/d1/d42/nomos.html) agents:
  * **Monk** is a full text license scanner.
  * **Nomos** uses short phases and heuristics for license identification.

## 3. Source Code Modifications

To enable **ESSTRA** integration, the kernel source files require the following modifications:

* A diff file containing all necessary modifications is available in [enable_esstra_in_kernel.diff](./output-examples/enable_esstra_in_kernel.diff) .

* Summary of the patch file is as follows:
  * Added `CONFIG_ESSTRA` option to `arch/x86/Kconfig`.
  * Updated build scripts to support **ESSTRA** plugin integration.
  * Modified build flags to include the path to `esstracore.so` when **ESSTRA** is enabled.
  * Implemented error handling for missing **ESSTRA** plugin during build.
  * Provided all necessary changes in a single patch file for easy application.

* The `CONFIG_ESSTRA` flag created in `arch/x86/Kconfig`, disabled by default, controls the **ESSTRA** build process and the inclusion of the **ESSTRA** section in the final binaries.

* When `CONFIG_ESSTRA` is enabled, the compiler flags are updated with the installation path of `esstracore.so`. If the **ESSTRA** plugin is not found at the expected location, the kernel build will fail with the following error:

    ```sh
    *** ESSTRA plugin not found at /usr/local/lib/gcc/x86_64-linux-gnu/11/plugin/esstracore.so. Please install esstra plugin..  Stop.
    ```
> [!note]
> Currently, as described in [README.md](https://github.com/sony/esstra/blob/main/README.md), **ESSTRA** collects source file information during the build process using a GCC plugin, so it does not support files that require other compilers. For Rust/LLVM, a proof of concept (PoC) is being conducted at https://github.com/sony/esstra/tree/poc/rust-llvm/poc. The above modifications to the Kernel were made for the x86 architecture.

## 4. Build Process

Follow these steps to build the kernel with **ESSTRA** enabled.

### Step 1: Set Up ESSTRA

> [!note]
> The build instructions differ slightly (`sudo make install-specs` not required) from the full build instructions mentioned [here](../../core/README.md#how-to-build-and-install) . Find the relevant instructions below:

First, build and install the **ESSTRA** GCC plugin.

Clone the **ESSTRA** repository

```sh
$ git clone --branch v0.4.0 https://github.com/sony/esstra.git
```

Install the GCC plugin development package

```sh
$ sudo apt install -y gcc-11-plugin-dev
```

Build and install **ESSTRA**

```sh
$ cd esstra/
$ make
$ sudo make install
```

### Step 2: Obtain and Prepare Kernel Source

Download the kernel source and install its build dependencies.

```sh
$ apt source linux-headers-6.8.0-79-generic
$ cd linux-hwe-6.8-6.8.0/
$ sudo apt build-dep linux-headers-6.8.0-79-generic
```

### Step 3: Apply ESSTRA Modifications

Apply the prepared patch file to the kernel source tree.

From the top-level kernel source directory (e.g., `linux-hwe-6.8-6.8.0/`)

```sh
$ git apply ../enable_esstra_in_kernel.diff
```

### Step 4: Configure and Build the Kernel

Finally, configure the kernel to enable **ESSTRA** and start the build.

Create a default configuration

```sh
$ make defconfig
```

Enable the `CONFIG_ESSTRA` flag

```sh
$ ./scripts/config --enable CONFIG_ESSTRA
```

Update the configuration

```sh
$ make olddefconfig
```

Build the kernel using all available processor cores

```sh
$ make -j$(nproc)
```

## 5. Post-Build Verification and License Integration

After a successful build, you can verify the **ESSTRA** integration and update the binary with license data.

### 5.1. Finding Generated Binaries

To locate all `ELF` binaries generated during the build, use the `find` command to search for files with a `BuildID`. This method is more accurate than searching for `ELF`, which can match non-binary files.

```sh
$ find ./ -type f -exec sh -c "file '{}' | grep -q 'BuildID'" \; -print
```

Example output:

```sh
./vmlinux
./scripts/sorttable
./.tmp_vmlinux2
./usr/gen_init_cpio
```

### 5.2. Fetching Initial ESSTRA Metadata

Use the `esstra show` command to display the embedded **ESSTRA** metadata from a binary, such as `vmlinux`. The initial output will contain toolchain information and a list of source files with their SHA1 hashes.

```sh
$ esstra show ./vmlinux
```

Example output:

```yaml
# BinaryFileName: ./vmlinux
# BinaryPath: /home/linux-hwe-6.8-6.8.0/vmlinux
#
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.4.0
  DataFormatVersion: 0.1.0
  (SNIP)
SourceFiles:
- Directory: /home/linux-hwe-6.8-6.8.0/arch/x86/entry
  Files:
  - File: common.c
    SHA1: 971740e1b21a072cbadfbc80d0e22e16c1201769
  - File: syscall_32.c
    SHA1: 4bbadaca318274655cb8c65789fbe30c0f628249
  - File: syscall_64.c
    SHA1: ba44792020277774d8ce5d9f09cbeb4ade3ea57f
```

### 5.3. Generating an SPDX File with FOSSology

Scan the Linux kernel source files using **FOSSology** to generate an SPDX file in tag-value format. The SPDX file contains the license information for the source files.

Refer to
[this guide](https://github.com/sony/esstra/blob/main/samples/hello/README_FOSSOLOGY.md)
for a step-by-step manual approach to analyze the source files with **FOSSology** and generate a
report.

Follow the below steps for only license scan on **FOSSology**:

* Create a tar archive for the fresh Kernel source downloaded via apt

    ```sh
    $ tar -czf linux-hwe-6.8-6.8.0.tgz linux-hwe-6.8-6.8.0
    ```

* To get license details only from license declarations made using an `SPDX-License-Identifier` tag, run a scan with only the **Ojo** agent. SPDX file generated using this agent can be found in [SPDX2TV_linux-headers-6.8.0-79-generic.tar_ojo.spdx](./output-examples/SPDX2TV_linux-headers-6.8.0-79-generic.tar_ojo.spdx)

* To perform a more exhaustive scan (including text-based matching), run a scan with the **Monk** and **Nomos** agents. SPDX file generated using these agents can be found in [SPDX2TV_linux-headers-6.8.0-79-generic.tar_monk_nomos.spdx](./output-examples/SPDX2TV_linux-headers-6.8.0-79-generic.tar_monk_nomos.spdx)

### 5.4. Updating Binary with License Metadata

Use the `esstra update` command to embed the license information from the generated SPDX file into the binary.

> [!note]
> In **ESSTRA** version 0.4.0, the `update` command permanently appends metadata to a binary, and this action cannot be undone. Once metadata from one source (e.g., `_ojo.spdx`) is added, it is not possible to remove it and replace it with data from another source (e.g., `_monk_nomos.spdx`). To prevent irreversible changes, it is highly recommended that you back up the original binary before running an update.

```sh
$ esstra update ./vmlinux -i SPDX2TV_linux-headers-6.8.0-79-generic.tar_ojo.spdx
```

Output:

```sh
* updating metadata of './vmlinux'...
* done.
```

### 5.5. Verifying Updated ESSTRA Metadata

Display the metadata again to confirm that the license information has been added.

```sh
$ esstra show ./vmlinux
```

The output will now include a `LicenseInfo` field for files where a license was identified.

Example output:

```yaml
# BinaryFileName: ./vmlinux
# BinaryPath: /home/linux-hwe-6.8-6.8.0/vmlinux
#
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.4.0
  DataFormatVersion: 0.1.0
  (SNIP)
SourceFiles:
- Directory: /home/linux-hwe-6.8-6.8.0/arch/x86/entry
  Files:
  - File: common.c
    SHA1: 971740e1b21a072cbadfbc80d0e22e16c1201769
    LicenseInfo:
    - GPL-2.0-only
  - File: syscall_32.c
    SHA1: 4bbadaca318274655cb8c65789fbe30c0f628249
    LicenseInfo:
    - GPL-2.0-only
  - File: syscall_64.c
    SHA1: ba44792020277774d8ce5d9f09cbeb4ade3ea57f
    LicenseInfo:
    - GPL-2.0-only
```

For more details on the **ESSTRA Utility**, refer [here](https://github.com/sony/esstra/tree/main/util).

## 6. Analysis: The Importance of SPDX-License-Identifier tags

### Background

According to the Linux kernel's official  [documentation](https://docs.kernel.org/process/license-rules.html), every source file should contain an `SPDX-License-Identifier` tag to declare its license unambiguously. The following analysis demonstrates how this practice significantly improves the accuracy of automated license detection.

### Analysis A: Coverage of `SPDX-License-Identifier` for `vmlinux` and `scripts/sorttable` Source Files

This analysis calculates the percentage of source files used to build the `vmlinux` and `scripts/sorttable` contain `SPDX-License-Identifier` tags.

#### Step 1: Store the ESSTRA Metadata from the License-Updated Binaries

```sh
$ esstra show ./vmlinux > esstra_output_for_vmlinux.yaml

$ esstra show ./scripts/sorttable > esstra_output_for_scripts_sortable.yaml
```

#### Step 2: Extract the List of Source Files from the Metadata

```sh
$ yq '.SourceFiles[] | select(.Directory | test("^/home/linux-hwe-6.8-6.8.0")) | .Directory + "/" + .Files[].File' esstra_output_for_vmlinux.yaml > source_details_of_vmlinux.txt

$ yq '.SourceFiles[] | select(.Directory | test("^/home/linux-hwe-6.8-6.8.0")) | .Directory + "/" + .Files[].File' esstra_output_for_scripts_sortable.yaml > source_details_of_scripts_sortable.txt
```

> [!note]
> Source license mapping for `vmlinux` can be found in [source_details_of_vmlinux.txt](./output-examples/source_details_of_vmlinux.txt) and for `scripts/sortable` in [source_details_of_scripts_sortable.txt](./output-examples/source_details_of_scripts_sortable.txt) .

#### Step 3: Count the Total Number of Source Files

```sh
$ cat source_details_of_vmlinux.txt | wc -l
6467

$ cat source_details_of_scripts_sortable.txt | wc -l
11
```

Number of source files used:

* `vmlinux`: 6,467
* `scripts/sortable`: 11

#### Step 4: Count How Many of These Source Files Contain the SPDX-License-Identifier Tag

```sh
$ while IFS= read -r file; do
    if grep -q -i "SPDX-License-Identifier:" "$file"; then
        echo "$file"
    fi
done < source_details_of_vmlinux.txt | wc -l
5805

$ while IFS= read -r file; do
    if grep -q -i "SPDX-License-Identifier:" "$file"; then
        echo "$file"
    fi
done < source_details_of_scripts_sortable.txt | wc -l
11
```

Number of source files containing `SPDX-License-Identifier`:

* `vmlinux`: 5,805
* `scripts/sortable`: 11

#### Conclusion

Percentage of source files with `SPDX-License-Identifier`:

* For `vmlinux`: (5,805 / 6,467) * 100 = **89.76%**
* For `scripts/sortable`: (11 / 11) * 100 = **100%**

> [!note]
> Besides `vmlinux` and `scripts/sorttable`, 37 other binaries are generated. Overall coverage is about 90%. There are also 7 binaries with 100% coverage, but each of these is a small binary built from fewer than 10 source files.

### Analysis B: Investigating Generated Files Amongst Files Without SPDX-License-Identifier

Analysis A revealed that approximately 10% of the source files used to build `vmlinux` lack an `SPDX-License-Identifier` tag. Some of these files are auto-generated files by the build system (e.g., temporary assembly files, configuration headers), not original source code written by developers but are instead generated automatically during the kernel build process.

#### Methodology

To verify this, a three-step process was used to isolate and identify files that are generated during the build:

##### Step 1: Identify All Source Files Lacking an SPDX-License-Identifier

First, we filtered the complete list of `vmlinux` source files (`source_details_of_vmlinux.txt`) to create a new list containing only those files that do not have an `SPDX-License-Identifier` tag.

```sh
$ while IFS= read -r file; do \
    if grep -q -i "SPDX-License-Identifier:" "$file"; then :; \
    else echo "$file"; fi; \
  done < ./source_details_of_vmlinux.txt > non_spdx_license_identifier.txt
```

##### Step 2: Isolate Generated Files

Next, we compared the list of files without `SPDX-License-Identifier` tags against a fresh, un-built kernel source tree. Any file from the list that does not exist in the original source tree is, thus, a file generated during the build process.

In a fresh, un-built kernel source directory

```sh
$ while IFS= read -r file; do \
    if test -f "$file"; then :; \
    else echo "$file"; fi; \
  done < ../non_spdx_license_identifier.txt > ../generated_files.txt
```

##### Step 3: Collect Generated Files for Inspection

Finally, the identified generated files were copied from the built kernel directory into a separate `generated_files/` directory for further examination.

In the built kernel source directory,
```sh
$ mkdir -p generated_files
$ while IFS= read -r file; do \
    if test -f "$file"; then cp --parents "$file" ./generated_files/; fi; \
  done < ../generated_files.txt
```

#### Findings

* The manual investigation confirms that these auto-generated files are not only missing `SPDX-License-Identifier` but also missing other license-related text.
* This highlights an area for improvement in the build toolchain itself, not just in developer practice.

#### Conclusion

The build tools should explicitly add `SPDX-License-Identifier` for the auto-generated files to smoothen license compliance.

### Analysis C: License Detection Comparison for vmlinux Binary (Ojo vs. Monk & Nomos)

This analysis compares the number of unique license IDs detected by **FOSSology**'s **Ojo** agent (which relies solely on `SPDX-License-Identifier` tags) versus the **Monk** and **Nomos** agents (which use text-based scanning and heuristics).

#### Step 1: Perform FOSSology Scans and Generate Reports

> [!note]
> See [section 5.3 'Generating an SPDX File with FOSSology'](#53-generating-an-spdx-file-with-fossology) for detailed instructions.

* **Scan 1**: Run a scan on the kernel source with only the **Ojo** agent enabled. Generate an SPDX tag-value report.
* **Scan 2**: Run a second scan with only the **Monk** and **Nomos** agents enabled. Generate another SPDX tag-value report.

#### Step 2: Update Binaries with License Data

To compare the results, create two copies of the `vmlinux` binary and update each one with a different SPDX report.

Create copies of the original binary

```sh
$ cp ./vmlinux ./vmlinux_ojo
$ cp ./vmlinux ./vmlinux_monknomos
```

Update each binary with its corresponding SPDX file

```sh
$ esstra update ./vmlinux_ojo -i SPDX2TV_linux-headers-6.8.0-79-generic.tar_ojo.spdx
$ esstra update ./vmlinux_monknomos -i SPDX2TV_linux-headers-6.8.0-79-generic.tar_monk_nomos.spdx
```

#### Step 3: Count Unique Licenses Detected by the Ojo Agent

Extract the license information from the Ojo-updated binary and count the number of unique license identifiers found.

```sh
$ esstra show ./vmlinux_ojo > esstra_output_for_vmlinux_with_ojo.yaml

$ yq '.SourceFiles[].Files[].LicenseInfo[]' esstra_output_for_vmlinux_with_ojo.yaml | \
  sort | uniq
```

Result:

```sh
BSD-2-Clause
BSD-3-Clause
GPL-1.0-or-later
GPL-2.0-only
GPL-2.0-or-later
ISC
LGPL-2.0-or-later
LGPL-2.1-only
LGPL-2.1-or-later
LicenseRef-fossology-Dual-license
Linux-OpenIB
Linux-syscall-note
MIT
```

Total number of License IDs detected = 13

#### Step 4: Count Unique Licenses Detected by Monk and Nomos Agents

Repeat the process for the binary updated with the **Monk** and **Nomos** scan results.

```sh
$ esstra show ./vmlinux_monknomos > esstra_output_for_vmlinux_with_monknomos.yaml

$ yq '.SourceFiles[].Files[].LicenseInfo[]' esstra_output_for_vmlinux_with_monknomos.yaml | \
  sort | uniq
```

Result:

```sh
0BSD
BSD-2-Clause
BSD-3-Clause
BSD-3-Clause-HP
BSD-3-Clause-No-Military-License
Brian-Gladman-3-Clause
GPL-1.0-or-later
GPL-2.0-only
GPL-2.0-or-later
HPND-export-US
HPND-export-US-modify
HPND-sell-variant
ISC
LGPL-2.0-only
LGPL-2.0-or-later
LGPL-2.1-only
LGPL-2.1-or-later
LGPL-3.0-or-later
LicenseRef-fossology-BSD
LicenseRef-fossology-BSD-style
LicenseRef-fossology-Cryptogams
LicenseRef-fossology-Dual-license
LicenseRef-fossology-GPL
LicenseRef-fossology-GPL-possibility
LicenseRef-fossology-LGPL
LicenseRef-fossology-MIT-CMU-style
LicenseRef-fossology-MIT-style
LicenseRef-fossology-MPL
LicenseRef-fossology-Public-domain
LicenseRef-fossology-RedHat
LicenseRef-fossology-See-file.COPYING
LicenseRef-fossology-U-Michigan
LicenseRef-fossology-WebM
LicenseRef-fossology-XFree86
LicenseRef-fossology-Zlib-possibility
Linux-OpenIB
Linux-syscall-note
MIT
MIT-0
MPL-1.1
NOASSERTION
NTP
X11
X11-distribute-modifications-variant
Zlib
```

Total number of License IDs detected = 45

#### Step 5: Compare the Results

The analysis shows that the tag-based **Ojo** scan identified **13** unique licenses, while the text-based **Monk** and **Nomos** scan identified **45** unique licenses.

* **Ratio of Ojo-detected licenses**: `(13 / 45) * 100` ≈ **28.88%**

This over-detection by **Monk** and **Nomos** significantly complicates license compliance efforts by:

* Requiring extensive manual review to distinguish actual licenses from references
* Increasing legal review costs and timelines
* Creating uncertainty in compliance decisions
* Potentially flagging license conflicts that don't actually exist

For automated compliance workflows, the precision of `SPDX-License-Identifier` based detection is critical to maintaining both accuracy and efficiency.

#### Conclusion

* This result highlights that `SPDX-License-Identifier` based detection (as used by **Ojo**) provides a precise, developer-intended set of licenses.
* Text-based scanning approaches (such as those used by **Monk** and **Nomos**) perform broader matching, which can result in a larger, but potentially less precise, set of license findings.

## 7. Conclusion

* **`SPDX-License-Identifier` offers superior accuracy:**

    Analysis C confirms that relying on `SPDX-License-Identifier` tags (via the **Ojo** agent) yields the most accurate licensing data, directly reflecting the developers' intent and minimizing the false positives common with other scanning methods.

* **To improve compliance and transparency, every open-source file should include an `SPDX-License-Identifier`:**

    While 90% `SPDX-License-Identifier` coverage is impressive, the remaining 10% gap prevents full automation and forces the use of other scanners that introduce false positives and require manual review. Therefore, the most effective path to achieving complete software supply chain transparency is to mandate the inclusion of an `SPDX-License-Identifier` in every source file.

    This single step would ensure accuracy and empower automated tools like **ESSTRA** to produce fully compliant and verifiable binaries.
