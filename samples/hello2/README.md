# Sample "hello2"

This sample is essentially the same as [Sample "hello"](../hello/README.md),
but it demonstrates how to compile multiple source files into a single binary
using the ESSTRA Core.

Please note that this document assumes you have completed all the steps
outlined in [Sample "hello"](../hello/README.md).

## Source Code to be Compiled

In this sample, we use the [ESSTRA Core](/core/README.md) to compile
the two source files [`hello_main.c`](./hello_main.c) and [`hello_sub.c`](./hello_sub.c)
into a single binary named `hello2`.
The binary `hello2` is a program that, similar to [Sample "hello"](../hello/README.md),
simply prints `Hello, world!` to the standard output.

**`hello_main.c`**:
```c
#include "hello_sub.h"

int main(void)
{
    sub_puts("Hello, world!");
    return 0;
}
```

**`hello_sub.c`**:
```c
#include <stdio.h>

void sub_puts(const char *str)
{
    puts(str);
}
```

In this program, the function `sub_puts()` provided by
[`hello_sub.c`](./hello_sub.c) is called within the `main()` function in
[`hello_main.c`](./hello_main.c). Therefore, we have prepared a header file
[`hello_sub.h`](./hello_sub.h) to use the function defined in
[`hello_sub.c`](./hello_sub.c) externally:

**`hello_sub.h`**:
```c
#ifndef _HELLO_SUB_H_

extern void sub_puts(const char *);

#endif
```

Similar to [Sample "hello"](../hello/README.md), the license is specified at
the beginning of each file as follows:

**`hello_main.c`**:
```c
// SPDX-License-Identifier: MIT
```

**`hello_sub.c`**:
```c
// SPDX-License-Identifier: BSD-3-Clause
```

**`hello_sub.h`**:
```c
// SPDX-License-Identifier: LGPL-2.1-or-later
```

Please note that these licenses are only for verifying the operation of the
ESSTRA and do not represent the actual licenses of the source code. For the
actual source code licenses, please refer to the [LICENSE](../../LICENSE) file
in the top directory.

## Compiling with ESSTRA Core

We will compile the source files shown above to generate the binary
`hello2`. By using the
[ESSTRA Core](/core/README.md) during compilation,
metadata is embedded into `hello2`.
Since we are using GCC version 11 on an x86\_64 PC, the command line would be as follows:
>>>>>>> ed5e557 (update docs to reflect new path for esstracore.so)

```sh
$ gcc -fplugin=/usr/local/lib/gcc/x86_64-linux-gnu/11/plugin/esstracore.so hello_main.c hello_sub.c -o hello2
```

If you have already installed the [Spec File](/README.md#installing-spec-file), the
[ESSTRA Core](/core/README.md) will intervene in the compilation
without needing to specify the `-fplugin=` option, yielding the same result as above:

```sh
$ gcc hello_main.c hello_sub.c -o hello2
```

The output of the generated binary `hello2` is shown below:

```sh
$ ./hello2
Hello, world!
```

## Verifying Metadata in the Binary

Use the `show` command of the [ESSTRA utility](/util/README.md) to verify
the metadata within `hello2`:

```sh
$ esstra.py show hello2
```

And you will get a result as follows:

```yaml
#
# BinaryFileName: hello2
# BinaryPath: /home/snagao/esstra/samples/hello2/hello2
#
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.2.0
  DataFormatVersion: 0.1.0
  InputFileNames:
  - hello_main.c
  - hello_sub.c
SourceFiles:
- Directory: /home/snagao/esstra/samples/hello2
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
    SHA1: 57c3c8093c3af70e5851f6d498600e2f6e24fdeb
  - File: features.h
    SHA1: d8725bb98129d6d70ddcbf010021c2841db783f7
  - File: stdc-predef.h
    SHA1: 2fef05d80514ca0be77efec90bda051cf87d771f
  - File: stdio.h
    SHA1: c7181b48c4194cd122024971527aab4056baf600
- Directory: /usr/include/x86_64-linux-gnu/bits
  Files:
  - File: floatn-common.h
    SHA1: 3f37104123a2e6180621331c1da87125808e47bd
  - File: floatn.h
    SHA1: 806b759ab6894a09a3b3a422eec5f2414ba7dab7
  - File: libc-header-start.h
    SHA1: e0a400c194cd3962a342a6504a441920163b799c
  - File: long-double.h
    SHA1: 4e3f5928e816ad29079d1c7d75f3a510a0939ffb
  - File: stdio.h
    SHA1: 521d7cd0f6572f70122386784120cc55d84899bc
  - File: stdio2.h
    SHA1: 6c3ee923db9679a79941a688de72e114a794fc54
  - File: stdio_lim.h
    SHA1: 6210c8ae410ee0f39a6096b0adb9fa86febd3517
  - File: time64.h
    SHA1: ab2017da21608498b58eea37b2aa6a3387ee978c
  - File: timesize.h
    SHA1: f1dd8d62a4d75288654626933edfc82ccf2394a7
  - File: types.h
    SHA1: e5893a9c4c523615c73a51feb9680279608027c6
  - File: typesizes.h
    SHA1: ee94b5a60d007c23bdda9e5c46c8ba40f4eb402c
  - File: wordsize.h
    SHA1: 281ddd3c93f1e8653e809a45b606574c9b691092
- Directory: /usr/include/x86_64-linux-gnu/bits/types
  Files:
  - File: FILE.h
    SHA1: 497924e329d53517631713ae52acb73e870d7d65
  - File: __FILE.h
    SHA1: 274242343e85d1c06e7f5ccc5abf15e120f6e957
  - File: __fpos64_t.h
    SHA1: ac38e294b004f6e2bf18f1c55e03dc80f48d6830
  - File: __fpos_t.h
    SHA1: 760ef77769ac1921f4b1f908cbf06863e2506775
  - File: __mbstate_t.h
    SHA1: e3a4f2ee55e635520db0b4610d2b361e9ce41de7
  - File: struct_FILE.h
    SHA1: 1dbf8bac589cb09e09aa4c1d36913e549a57bcf0
- Directory: /usr/include/x86_64-linux-gnu/gnu
  Files:
  - File: stubs-64.h
    SHA1: f7603fa3908b56e9d1b33c91590db3252e13a799
  - File: stubs.h
    SHA1: be168037b7503a82b1cf694cdbac8c063bb6e476
- Directory: /usr/include/x86_64-linux-gnu/sys
  Files:
  - File: cdefs.h
    SHA1: a419a6372029d89ba38ada0811d34f51df8d09b7
- Directory: /usr/lib/gcc/x86_64-linux-gnu/11/include
  Files:
  - File: stdarg.h
    SHA1: fa23f49da8a0a5068b781dff7182f1a1c363dc30
  - File: stddef.h
    SHA1: 0de70008ffa3f198baf55c7b3f3d03b4ca11c21f
```

You can see that the metadata includes the source files specified during
compilation: [`hello_main.c`](./hello_main.c), [`hello_sub.c`](./hello_sub.c),
and [`hello_sub.h`](./hello_sub.h).
Additionally, similar to [Sample "hello"](../hello/README.md),
it also includes information about all header files that are explicitly or
implicitly `#include`'d.

## Adding License Information to Metadata

Here, similar to
[Sample "hello"](../hello/README.md#adding-license-information-to-metadata),
we will use the license information file
[`SPDX2TV_esstra.spdx`](../output-examples/SPDX2TV_esstra.spdx)
that has already been prepared.
Next, you can add license information to the metadata in the binary
`hello2` using the following command:

```sh
$ esstra.py update hello2 -i SPDX2TV_esstra.spdx
* processing 'hello2'...
* done.
```

To display the metadata content of the binary `hello2`, use the following command:

```sh
$ esstra.py show hello2
```

You will get the result shown below:

```yaml
#
# BinaryFileName: hello2
# BinaryPath: /home/snagao/esstra/samples/hello2/hello2
#
Headers:
  ToolName: ESSTRA Core
  ToolVersion: 0.2.0
  DataFormatVersion: 0.1.0
  InputFileNames:
  - hello_main.c
  - hello_sub.c
SourceFiles:
- Directory: /home/snagao/esstra/samples/hello2
  Files:
  - File: hello_main.c
    SHA1: f7f5c447d68fd9685594a31cb10c8d8b1dd5ebd6
    LicenseInfo:
    - MIT
  - File: hello_sub.c
    SHA1: cfb72998ae0242237fa42c8bcf61ee5887137392
    LicenseInfo:
    - BSD-3-Clause
  - File: hello_sub.h
    SHA1: 3e5b3ed1aed966c0e0c183eac8fe6ea02dfa62a0
    LicenseInfo:
    - LGPL-2.1-or-later
- Directory: /usr/include
  Files:
  - File: features-time64.h
    SHA1: 57c3c8093c3af70e5851f6d498600e2f6e24fdeb

       :

```

From the above result, you can see that the `LicenseInfo` tags have been added
to the metadata for the files
[`hello_main.c`](./hello_main.c),
[`hello_sub.c`](./hello_sub.c), and
[`hello_sub.h`](./hello_sub.h),
with the values `MIT`, `BSD-3-Clause`, and `LGPL-2.1-or-later`, respectively.

## Summary

In this sample, we confirmed that by using the
[ESSTRA Core](/core/README.md) during the compilation of multiple
source files into a single binary, the metadata includes information on
all the source files involved in the compilation and
all the header files they `#include`.

Additionally, by using the [ESSTRA Utility](/util/README.md) to add license
information to the metadata,
we updated the metadata in the binary `hello2` and confirmed that the license
information declared in each source file was added to the metadata.
