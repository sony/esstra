#!/bin/sh
# esstra-to-spdx-list.sh - convert esstra output into an spdx list
#   usage: esstra-to-spdx-list.sh <filename>
#

usage() {
    cat <<HERE
Usage: esstra-to-spdx-list.sh [-b {binary_filename}] [-e {esstra_filename}] [-x]

Scan the files listed in either the esstra data in the binary file specified
(or list in the estra data file listed), and show whether they have
SPDX-License-Identifier headers - indicating the license for that file.

Options:
  -h         Show this usage help
  -b {file}  Specify a binary file to extract esstra data from to use
  -e {file}  Specify an esstra data file to use for SPDX scanning
  -x         Show only files missing an SPDX header
HERE
}

if [ "$1" = "-h" ] ; then
    usage
    exit 0
fi

if [ "$1" = "-b" ] ; then
    shift
    binary_file="$1"
    shift
fi
if [ "$1" = "-e" ] ; then
    shift
    esstra_file="$1"
    shift
fi

if [ "$1" = "-x" ] ; then
    X_ARG="-x"
    shift
fi

#esstra show -r $binary_file | grep InputFileName | sed "s/  InputFileName: //" | has-spdx-id.py -c -
#cat $input_file | grep InputFileName | sed "s/InputFileName: //" | has-spdx-id.sh -c -
#

if [ -n "$binary_file" ] ; then
    # grab and sort all File: entries
    esstra show -r $binary_file | esstra-full-paths | grep Path: | sed "s/- Path: //" | sort | uniq | has-spdx-id.py -c -
fi

if [ -n "$esstra_file" ] ; then
    cat $esstra_file | esstra-full-paths | grep Path: | sed "s/- Path: //" | sort | uniq | has-spdx-id.py -c $X_ARG -
fi
