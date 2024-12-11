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
import re
import tempfile

import yaml


DEBUG = False

COMMANDS = {
    'show': 'display information embedded by ESSTRA Core',
    'update': 'update embedded information with SPDX tag/value file',
    'shrink': 'shrink embedded information by removing duplication',
}

# keys in esstra_info
SECTION_NAME = 'esstra_info'
KEY_INPUT_FILE_NAME = 'InputFileName'
KEY_SOURCE_PATH = 'SourcePath'
KEY_SOURCE_FILES = 'SourceFiles'
KEY_SHA1 = 'SHA1'
KEY_LICENSE_INFO = 'LicenseInfo'
HASH_ALGORITHM = 'SHA1'

# keys for binary file paths
KEY_BINARY_FILE_NAME = 'BinaryFileName'
KEY_BINARY_PATH = 'BinaryPath'


#
# basic helper functions
#
DEBUG = False


def debug(msg):
    if DEBUG:
        print(f'[DEBUG] {msg}')


def message(msg):
    print(f'* {msg}')


def error(msg):
    print(f'[ERROR] {msg}', file=sys.stderr)


def call_function_by_name(function_name, *args):
    if function_name not in globals():
        raise NameError(f'Fatal: function {function_name!r} not found.')

    function = globals()[function_name]
    if not callable(function):
        raise TypeError(f'Fatal: name {function_name!r} is not callable.')

    return function(*args)


def get_resolved_file_path(tvfile):
    path = Path(tvfile).resolve()
    if not path.exists():
        error(f'{tvfile!r}: not exist')
        return None
    if not Path(path).is_file():
        error(f'{tvfile!r}: not a file')
        return None
    return str(path)


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
    lines = []
    offset = None
    for line in result.stdout.splitlines():
        line = line.strip()
        if len(line) == 0:
            continue
        elif line.startswith('String dump'):
            continue
        elif not offset:
            if not line.startswith('['):
                continue
            rbracket = line.find(']')
            assert rbracket >= 0, 'cannot find right bracket "]"'
            content = line[rbracket+1:].strip()
            offset = len(line) - len(content)
            lines.append(content)
        else:
            content = line[offset:].rstrip()
            lines.append(content)

    # parse esstra info that is in yaml format
    parsed_data = yaml.safe_load('\n'.join(lines))

    # return parsed data
    return parsed_data


#
# setup command line parser for 'show'
#
def _setup_show(parser):
    parser.add_argument(
        'binary', nargs='+',
        help='ESSTRA-built binary file to show embedded information')


#
# run 'show' command
#
def _run_show(args):
    # gather embedded data into structured info
    for given_path in args.binary:
        print('#')
        print(f'# {KEY_BINARY_FILE_NAME}: {given_path}')
        path = get_resolved_file_path(given_path)
        if not path:
            print('#')
            print('---')
            print(f'- Error: cannot resolve {given_path!r}')
            continue
        print(f'# {KEY_BINARY_PATH}: {path}')
        print('#')
        print('---')
        info = _extract_esstra_info(given_path)
        if not info:
            print('- Error: cannot extract metadata')
            continue
        print(yaml.safe_dump(info, sort_keys=False))

    return 0


#
# helper functions for command 'update'
#

RE_TAG_VALUE = re.compile(r'([a-z0-9-]+):\s*(.*)\s*$', re.I)

TAG_FILE_NAME = 'FileName'
TAG_FILE_CHECKSUM = 'FileChecksum'
TAG_LICENSE_INFO_IN_FILE = 'LicenseInfoInFile'


def _parse_spdx_tv(tvfile):
    def extract_multiline_text(tagged_text):
        assert tagged_text.startswith('<text>'), tagged_text
        assert tagged_text.endswith('</text>'), tagged_text
        return tagged_text.replace('<text>', '').replace('</text>', '').strip()

    with open(tvfile, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()

    tag_values = []

    tag = None
    value = None
    multiline = False

    for line in lines:
        if multiline:
            if line.rstrip().endswith('</text>'):
                value += line.rstrip()
                multiline = False
                tag_values.append((tag, extract_multiline_text(value)))
            else:
                value += line
            continue
        match = RE_TAG_VALUE.match(line)
        if match:
            tag = match[1]
            value = match[2]
            if value.startswith('<text>'):
                if not value.endswith('</text>'):
                    multiline = True
                    value += '\n'
                    continue
                value = extract_multiline_text(value)
            yield tag, value
            tag = None
            value = None

    if tag:
        yield tag, value


def _make_hash_map_from_spdx_tv(tvfile, algo):
    assert algo[-1] != ':'
    algo = algo.upper() + ':'

    result = {}
    filename = None
    filehash = None
    fileinfo = None

    def push(fhash, finfo):
        if fhash not in result.keys():
            result[fhash] = [finfo]
        else:
            result[fhash].append(finfo)

    for tag, value in _parse_spdx_tv(tvfile):
        if tag == TAG_FILE_NAME:
            # flush last item if any
            if filename:
                assert filehash
                push(filehash, fileinfo)
            # reset item elements
            filename = value
            filehash = None
            fileinfo = [(tag, value)]
        elif filename:
            fileinfo.append((tag, value))
            if tag == TAG_FILE_CHECKSUM:
                hash_value_list = value.split(algo)
                if len(hash_value_list) == 2:
                    # this is the hash you want
                    filehash = hash_value_list[-1].strip()
        else:
            debug(f'ignored: "{tag}: {value}"')

    # flush last item if any
    if filename:
        assert filehash
        push(filehash, fileinfo)

    return result


def _get_file_info_by_path(file_info_list, path):
    for file_info in file_info_list:
        for tag, value in file_info:
            if tag == TAG_FILE_NAME:
                if Path(value).name == Path(path).name:
                    return file_info
    return None


def _attach_license_info(esstra_info, hash_map):
    for input_file_elem in esstra_info:
        assert KEY_INPUT_FILE_NAME in input_file_elem
        assert KEY_SOURCE_FILES in input_file_elem
        for file_info in input_file_elem[KEY_SOURCE_FILES]:
            debug(file_info)
            path = file_info[KEY_SOURCE_PATH]
            sha1sum = file_info[KEY_SHA1]
            if sha1sum not in hash_map:
                continue

            spdx_file_info = _get_file_info_by_path(hash_map[sha1sum], path)
            assert spdx_file_info

            # attach license info
            license_info = [
                value for tag, value in spdx_file_info
                if tag == TAG_LICENSE_INFO_IN_FILE
            ]
            if license_info:
                file_info[KEY_LICENSE_INFO] = license_info
                debug(f'{path}: {license_info}')


def _update_esstra_info(binary, esstra_info):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8') as fp:
        esstra_info_string = yaml.safe_dump(esstra_info, sort_keys=False)
        for line in esstra_info_string.splitlines():
            fp.write(line)
            fp.write('\0')
        fp.flush()

        result = subprocess.run(
            ['objcopy', binary,
             '--update-section', f'{SECTION_NAME}={fp.name}'],
            encoding='utf-8',
            check=False,
            capture_output=True)

        # check if it was ok or error
        if result.returncode:
            error(f'objcopy returned code {result.returncode}')
            error(result.stderr)
            return False

    return True


def _create_backup_file(src, dst, overwrite):
    if not overwrite and Path(dst).exists():
        error(f'{dst!r}: exists.')
        return False

    result = subprocess.run(
        ['cp', '-a', src, dst],
        encoding='utf-8',
        check=False,
        capture_output=True)

    # check if it was ok or error
    if result.returncode:
        error(f'cp returned code {result.returncode}')
        error(result.stderr)
        return False

    return True


#
# setup command line parser for 'update'
#
def _setup_update(parser):
    parser.add_argument(
        '-i', '--info-file', required=True,
        nargs='+',
        action='extend',
        help='spdx tag/value file containing license information')
    parser.add_argument(
        'binary', nargs='+',
        help='ESSTRA-built binary file to update embedded information')
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='do not create backup of binary file')
    parser.add_argument(
        '--overwrite-backup',
        action='store_true',
        help='overwrite old backup file')
    parser.add_argument(
        '-s', '--suffix',
        default='bak',
        help='suffix of backup file')


#
# run 'update' command
#
def _run_update(args):
    errors = 0
    for binary in args.binary:
        if binary.endswith(f'.{args.suffix}'):
            message(f'skip backup file {binary!r}.')
        message(f'processing {binary!r}...')
        for spdx_tv_file in args.info_file:
            esstra_info = _extract_esstra_info(binary)
            hash_map = _make_hash_map_from_spdx_tv(spdx_tv_file, HASH_ALGORITHM)
            _attach_license_info(esstra_info, hash_map)
            debug(yaml.dump(esstra_info))

            if not args.no_backup:
                if not _create_backup_file(
                        binary, f'{binary}.{args.suffix}',
                        args.overwrite_backup):
                    error('cannot create backup. skip')
                    errors += 1
                    continue
            _update_esstra_info(binary, esstra_info)

    if errors:
        message(f'done with {errors} error(s).')
    else:
        message('done.')

    return 0


#
# helper functions for command 'shrink'
#
def _shrink_esstra_info(esstra_info):
    unique_file_info = {}
    for input_file_elem in esstra_info:
        assert KEY_INPUT_FILE_NAME in input_file_elem
        assert KEY_SOURCE_FILES in input_file_elem
        for file_info in input_file_elem[KEY_SOURCE_FILES]:
            path = file_info[KEY_SOURCE_PATH]
            if path not in file_info:
                unique_file_info[path] = file_info
            else:
                assert unique_file_info[path] == file_info

    return {
        KEY_SOURCE_FILES: [
            unique_file_info[path]
            for path in sorted(unique_file_info.keys())
        ]
    }


#
# setup command line parser for 'shrink'
#
def _setup_shrink(parser):
    parser.add_argument(
        'binary', nargs='+',
        help='ESSTRA-built binary file to shrink embedded information')
    parser.add_argument(
        '-n', '--no-backup',
        action='store_true',
        help='do not create backup of binary file')
    parser.add_argument(
        '-o', '--overwrite-backup',
        action='store_true',
        help='overwrite old backup file')
    parser.add_argument(
        '-s', '--suffix',
        default='bak',
        help='suffix of backup file')


#
# run 'shrink' command
#
def _run_shrink(args):
    errors = 0
    unique_file_info = {}
    for binary in args.binary:
        if binary.endswith(f'.{args.suffix}'):
            message(f'skip backup file {binary!r}.')
        message(f'processing {binary!r}...')
        esstra_info = _extract_esstra_info(binary)
        unique_file_info = _shrink_esstra_info(esstra_info)
        if not args.no_backup:
            if not _create_backup_file(
                    binary, f'{binary}.{args.suffix}',
                    args.overwrite_backup):
                error('cannot create backup. skip')
                errors += 1
        if not _update_esstra_info(binary, unique_file_info):
            error('failed to update metadata')
            errors += 1

    if errors:
        message(f'done with {errors} error(s).')
        return 1

    message('done.')
    return 0


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

    global DEBUG
    DEBUG = args.debug

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
