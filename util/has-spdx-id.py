#!/usr/bin/env python3
# has-spdx-id.py - indicate whether the given file has an SPDX identifier line
#  in the first 20 lines of the file
#

import sys
import os

def usage():
    print("""Usage: has-spdx-id.sh [options] {filepath}"
  Show whether a file (or files) has an SPDX-License-Identifier line,
  in the first 20 lines of the file.

  If {filepath} is '-', then read a list of filepaths to check from stdin.

Shows:
  1 if filepath has an SPDX-License-Identifier
  0 otherwise

The return code of the program is 0 if the last filepath scanned has
an SPDX line, and 1 otherwise.  This means that if only one file is
scanned you can use the program return status to indicate whether the
filepath has and SPDX line or not.

Options:
  -h     Show this usage help
  -q     Don't show the filepath along with the result (q=quiet)
  -c     Show counts of files with and without SPDX lines
  -x     Show only files without an SPDX line
""")
    sys.exit(0)

def main():
    # parse command line arguments
    quiet = False
    show_count = False
    show_only_missing = False
    if "-h" in sys.argv:
        usage()
    if "-q" in sys.argv:
        quiet = True
        sys.argv.remove("-q")
    if "-c" in sys.argv:
        show_count = True
        sys.argv.remove("-c")
    if "-x" in sys.argv:
        show_only_missing = True
        sys.argv.remove("-x")

    if len(sys.argv)<1:
        print("Error: missing argument")
        usage()

    filepaths = sys.argv[1:]

    if "-" in filepaths:
        pos = filepaths.index("-")
        lines = sys.stdin.readlines()
        filepaths[pos:pos+1] = [line.strip() for line in lines]

    with_count = 0
    without_count = 0
    has_spdx = False

    for filepath in filepaths:
        if not os.path.isfile(filepath):
            print(f"Warning: {filepath} is not a file")
            continue

        # read the first 20 lines of the file
        lines = []
        cur_file = open(filepath, "r")
        try:
            for i in range(20):
                lines.append(cur_file.readline().strip())
        except:
            pass

        cur_file.close()

        has_spdx = False
        for line in lines:
            if "SPDX-License-Identifier:" in line:
                # check for valid prefixes here:
                if line[0:5] in ['//SPD','// SP', '/* SP']:
                    has_spdx = True
                    break

        prefix = ""
        if not quiet:
           prefix = filepath + " - "
        if has_spdx:
            with_count += 1
            if not show_only_missing:
                print(prefix + "1")
        else:
            without_count += 1
            print(prefix + "0")

    if show_count:
        print(f"Files with SPDX lines: {with_count}")
        print(f"Files without SPDX lines: {without_count}")

    if has_spdx:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
