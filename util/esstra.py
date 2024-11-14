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
import json
import yaml


COMMANDS = {
    'show': 'display information embedded by ESSTRA Core',
    'update': 'update embedded information (*not implemented yet*)',
}

SECTION_NAME = 'esstra_info'
TAG_INPUT_FILE_NAME = 'InputFileName'
TAG_SOURCE_PATH = 'SourcePath'


#
# basic helper functions
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
# helper functions for command 'show'
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
            assert rbracket >= 0, 'cannot find right bracket "]"'
            tag_value = line[rbracket+1:].strip()
            tag, value = map(str.strip, tag_value.split(':'))
            esstra_info.append((tag, value))
        else:
            error(f'Ignore unexpected line: {line!r}')

    return esstra_info


def _parse_esstra_info(esstra_info):
    parsed_info = []
    input_file_name = None
    source_path = None

    input_file_info = None
    source_info = None

    for tag, value in esstra_info:
        if tag == TAG_INPUT_FILE_NAME:
            input_file_name = value
            source_files_info = []
            input_file_info = {
                'inputFileName': input_file_name,
                'sourceFiles': source_files_info,
            }
            parsed_info.append(input_file_info)
        elif tag == TAG_SOURCE_PATH:
            assert input_file_name is not None
            assert source_files_info is not None
            source_path = value
            source_info = {
                'path': source_path,
            }
            source_files_info.append(source_info)
        else:
            assert input_file_name is not None
            assert source_info is not None
            source_info.update({
                tag: value,
            })

    return parsed_info


def _generate_data_for_binary(binary_file):
    path = Path(binary_file).resolve()

    if not path.exists():
        error(f'{binary_file!r}: not exist')
        return None

    if not Path(path).is_file():
        error(f'{binary_file!r}: not a file')
        return None

    esstra_info = _extract_esstra_info(path)
    if not esstra_info:
        error('{given_path!r}: cannot find esstra information')
        return None

    parsed_info = _parse_esstra_info(esstra_info)
    if not parsed_info:
        error('{given_path!r}: cannot parse esstra information')
        return None

    return {
        'binaryFile': binary_file,
        'path': str(path),
        'sourceFiles': parsed_info,
    }


def _print_esstra_info(esstra_info):
    import yaml
    print(yaml.safe_dump(esstra_info))


def _setup_show(parser):
    parser.add_argument(
        'binary', nargs='+',
        help='ESSTRA-built binary file to show embedded information')
    parser.add_argument(
        '-o', '--output-format',
        type=str.lower,
        choices=['j', 'y', 'r'],
        default='j',
        help='output format (j:json, y:yaml, r:raw)')


def _run_show(args):
    if args.output_format in ('j', 'y'):
        # gather embedded data into structured info
        result = []
        for given_path in args.binary:
            data = _generate_data_for_binary(given_path)
            if not data:
                error(f'{given_path!r}: cannot get embedded data')
                continue
            result.append(data)
        # show result in specified format
        if args.output_format == 'j':
            print(json.dumps(data, indent=4))
        elif args.output_format == 'y':
            print(yaml.safe_dump(data))
    else:
        assert args.output_format == 'r'
        result = []
        for given_path in args.binary:
            result.append('---')
            result.append(f'File: {given_path}')
            data = _extract_esstra_info(given_path)
            if not data:
                error(f'{given_path!r}: cannot get embedded data')
                continue
            result += [f'{tag}: {value}' for tag, value in data]
        print('\n'.join(result))

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
        [f'  {name:16}{description}' for name, description in COMMANDS.items()])

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=description)

    subparsers = parser.add_subparsers()

    for name, description in COMMANDS.items():
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
