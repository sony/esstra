#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT
#
# Copyright 2024 Sony Group Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
import argparse
from pathlib import Path
import subprocess


COMMANDS = (
    ('show', 'display information embedded by ESSTRA Core'),
    ('update', 'update embedded information (*not implemented yet*)'),
)

SECTION_NAME = 'esstra_info'


#
# helper functions
#
def error(msg):
    print(f'[ERROR] {msg}', file=sys.stderr)


def call_function_by_name(function_name, *args):
    if function_name not in globals():
        raise NameError(f'Fatal: function {function_name!r} not found.')

    function = globals()[function_name]
    if not callable(function):
        raise TypeError(f'Fatal: name {function_name!r} is not callable.')

    return function(*args)


#
# functions for command 'show'
#
def _extract_esstra_info(path):
    result = subprocess.run(
        ['readelf', '--string-dump', SECTION_NAME, path],
        encoding='utf-8',
        check=False,
        capture_output=True)

    # check if it was ok or error
    if result.returncode:
        error(f'readelf returned code {result.returncode}')
        error(result.stderr)
        return None

    # if ok, parse the output
    esstra_info = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if len(line) == 0:
            pass
        elif line.startswith('String dump'):
            pass
        elif line.startswith('['):
            rbracket = line.find(']')
            element = line[rbracket+1:].strip()
            esstra_info.append(element)
        else:
            error(f'Ignore unexpected line: {line!r}')

    return esstra_info


def _print_esstra_info(esstra_info):
    print('Information:')
    for element in esstra_info:
        print(f'- {element}')


def _setup_show(parser):
    parser.add_argument(
        'file', nargs='+',
        help='ESSTRA-built binary to show embedded information by ESSTRA Core')


def _run_show(args):
    for given_path in args.file:
        print('---')
        print(f'File: {given_path}')
        path = Path(given_path).resolve()
        if not path.exists():
            print('Error: path not exist')
        elif not Path(path).is_file():
            print('Error: not a file')
        else:
            esstra_info = _extract_esstra_info(path)
            if not esstra_info:
                print('Error: ESSTRA information not found')
            else:
                _print_esstra_info(esstra_info)
        print()

    return 0


#
# functions for command 'update'
#
def _setup_update(parser):
    # not implemented yet
    pass


def _run_update(args):
    error('not implemented yet')
    return 1


#
# main function
#
def main():
    description = '\n'.join(
        ['commands:'] +
        [f'  {name:16}{description}' for name, description in COMMANDS])

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=description)

    subparsers = parser.add_subparsers()

    for name, description in COMMANDS:
        subparser = subparsers.add_parser(
            name,
            description=description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        subparser.set_defaults(name=name)
        subparser.add_argument(
            '-D', '--debug',
            default=False,
            action='store_true',
            help='enable debug logs')

        call_function_by_name(f'_setup_{name}', subparser)

    args = parser.parse_args()

    if not hasattr(args, 'name'):
        print('no command specified. show help by "-h".')
        sys.exit(1)

    ret = call_function_by_name(f'_run_{args.name}', args)

    return ret


#
# main
#
if __name__ == '__main__':
    sys.exit(main())
