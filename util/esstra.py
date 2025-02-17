#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT
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

from abc import ABC, abstractmethod
import sys
import argparse
from pathlib import Path
import subprocess
import re
import tempfile
import yaml


DEBUG = False


def set_debug_flag(flag):
    global DEBUG
    DEBUG = flag


def debug(msg):
    if DEBUG:
        print(f'[DEBUG] {msg}')


def message(msg):
    print(f'* {msg}')


def error(msg):
    print(f'[ERROR] {msg}', file=sys.stderr)


class MetadataHandler:
    SECTION_NAME = 'esstra_info'
    KEY_SOURCE_FILES = 'SourceFiles'
    KEY_FILE = 'File'
    KEY_LICENSE_INFO = 'LicenseInfo'
    HASH_ALGORITHM = 'SHA1'

    def __init__(self, binary_path):
        if not Path(binary_path).exists():
            raise FileNotFoundError
        if not Path(binary_path).is_file():
            raise TypeError

        self._binary_path = binary_path
        self._raw_data = self.__extract_metadata(binary_path)
        self._parsed_data = self.__decode_metadata(self._raw_data)
        self._shrunk_data = self.__shrink_parsed_data(self._parsed_data)

    # public
    def get_raw_data(self):
        return self._raw_data

    def get_parsed_data(self):
        return self._parsed_data

    def get_shrunk_data(self):
        return self._shrunk_data

    def enumerate_files(self):
        assert self.KEY_SOURCE_FILES in self._shrunk_data
        source_files = self._shrunk_data[self.KEY_SOURCE_FILES]
        for directory, files in source_files.items():
            for fileinfo in files:
                abs_path = str(Path(directory) / fileinfo[self.KEY_FILE])
                checksum = fileinfo[self.HASH_ALGORITHM]
                yield abs_path, checksum, fileinfo

    def update_metadata(self, binary_path,
                        create_backup, backup_suffix, overwrite_backup):
        if create_backup:
            self.__create_backup_file(
                binary_path, backup_suffix, overwrite_backup)

        with tempfile.NamedTemporaryFile('wb') as fp:
            raw_data = self.__encode_metadata(self._shrunk_data)
            fp.write(raw_data)
            fp.flush()

            result = subprocess.run(
                ['objcopy',
                 binary_path,
                 '--update-section',
                 f'{self.SECTION_NAME}={fp.name}'],
                encoding='utf-8',
                check=False,
                capture_output=True)

            if result.returncode:
                raise TypeError(
                    f'objcopy returned code {result.returncode}'
                    f' with output {result.stderr!r}')

        return True

    def strip_metadata(self, binary_path,
                       create_backup, backup_suffix, overwrite_backup):
        if create_backup:
            self.__create_backup_file(
                binary_path, backup_suffix, overwrite_backup)

        result = subprocess.run(
            ['objcopy',
             f'-R{self.SECTION_NAME}',
             binary_path],
            encoding='utf-8',
            check=False,
            capture_output=True)

        if result.returncode:
            raise TypeError(
                f'objcopy returned code {result.returncode}'
                f' with output {result.stderr!r}')

        return True

    # private
    def __extract_metadata(self, binary_path):
        with tempfile.NamedTemporaryFile('wb', delete=False) as temp:
            result = subprocess.run(
                ['objcopy',
                 '--dump-section',
                 f'{self.SECTION_NAME}={temp.name}',
                 binary_path],
                encoding='utf-8',
                check=False,
                capture_output=True)

        if result.returncode:
            raise TypeError(f'objcopy returned code {result.returncode}'
                            f' with output {result.stderr!r}')

        with open(temp.name, 'rb') as fp:
            raw_data = fp.read()

        Path(temp.name).unlink()

        return raw_data

    @staticmethod
    def __decode_metadata(raw_data):
        yaml_lines = raw_data.replace(b'\0', b'\n').decode(encoding='utf-8')
        yaml_docs = list(yaml.safe_load_all(yaml_lines))
        return yaml_docs

    @staticmethod
    def __encode_metadata(data):
        raw_data = bytes(
            yaml.safe_dump(data, sort_keys=False)
            .replace('\n', '\0')
            .encode(encoding='utf-8')
        )
        return raw_data

    def __shrink_parsed_data(self, parsed_data):
        shrunk = {}
        path_found = set()
        for doc in parsed_data:
            assert self.KEY_SOURCE_FILES in doc
            for directory, fileinfo_list in doc[self.KEY_SOURCE_FILES].items():
                if directory not in shrunk:
                    shrunk[directory] = []
                for fileinfo in fileinfo_list:
                    assert self.KEY_FILE in fileinfo, fileinfo
                    assert self.HASH_ALGORITHM in fileinfo
                    filename = fileinfo[self.KEY_FILE]
                    path = Path(directory) / filename
                    if path not in path_found:
                        path_found.add(path)
                        shrunk[directory].append(fileinfo)

        for directory in shrunk:
            shrunk[directory] = sorted(
                shrunk[directory], key=lambda x: x[self.KEY_FILE])

        shrunk_data = {
            self.KEY_SOURCE_FILES: {
                directory: shrunk[directory]
                for directory in sorted(shrunk.keys())
            }
        }

        return shrunk_data

    def __create_backup_file(
            self, binary_path, backup_suffix, overwrite_backup):
        backup_path = binary_path + backup_suffix
        if not overwrite_backup and Path(backup_path).exists():
            error(f'{backup_path!r}: exists.')
            return False

        result = subprocess.run(
            ['cp', '-a', binary_path, backup_path],
            encoding='utf-8',
            check=False,
            capture_output=True)

        # check if it was ok or error
        if result.returncode:
            error(f'cp returned code {result.returncode}')
            error(result.stderr)
            return False


class SpdxTagValueInfo:
    RE_TAG_VALUE = re.compile(r'([a-z0-9-]+):\s*(.*)\s*$', re.I)
    TAG_FILE_NAME = 'FileName'
    TAG_FILE_CHECKSUM = 'FileChecksum'
    TAG_LICENSE_INFO_IN_FILE = 'LicenseInfoInFile'
    TAG_LICENSE_ID = 'LicenseID'
    TAG_TEXT_BEGIN = '<text>'
    TAG_TEXT_END = '</text>'
    GROUP_HEADERS = (TAG_FILE_NAME, TAG_LICENSE_ID)
    HASH_ALGORITHM = 'SHA1'

    def __init__(self):
        self._fileinfos = {}

    def read(self, tvfile):
        with open(tvfile, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
        self.__update_fileinfos(lines)

    def get_fileinfo(self, path, checksum):
        if checksum not in self._fileinfos:
            debug(f'path {path!r} with sum {checksum!r} not found')
            return None

        for fileinfo in self._fileinfos[checksum]:
            filepath = fileinfo[self.TAG_FILE_NAME][0]
            if self.__check_filepath(path, filepath):
                debug(f'FOUND: {path!r} with sum {checksum!r}')
                return fileinfo

        debug(f'sum {checksum!r} found but path {path!r} not matched: {filepath!r}')
        return None

    # private
    def __update_fileinfos(self, lines):
        # make a list of file information
        fileinfo_list = []
        fileinfo = None
        for tag, value in self.__parse_tag_value_lines(lines):
            if tag in self.GROUP_HEADERS:
                fileinfo = {}
                if tag == self.TAG_FILE_NAME:
                    fileinfo_list.append(fileinfo)
            if fileinfo is not None:
                fileinfo.setdefault(tag, [])
                fileinfo[tag].append(value)

        # update self._fileinfo as a dict whose keys are checksums
        checksum = None
        for fileinfo in fileinfo_list:
            if self.TAG_FILE_CHECKSUM in fileinfo:
                for checksum_value in fileinfo[self.TAG_FILE_CHECKSUM]:
                    if checksum_value.startswith(self.HASH_ALGORITHM):
                        checksum = checksum_value.split()[1]
                        self._fileinfos.setdefault(checksum, [])
                        self._fileinfos[checksum].append(fileinfo)

    @staticmethod
    def __check_filepath(spdx_filename, path):
        # TODO: use more accurate comparison
        return Path(spdx_filename).name == Path(path).name

    @classmethod
    def __parse_tag_value_lines(cls, lines):
        def extract_multiline_text(tagged_text):
            assert tagged_text.startswith(cls.TAG_TEXT_BEGIN), tagged_text
            assert tagged_text.endswith(cls.TAG_TEXT_END), tagged_text
            return tagged_text.replace(cls.TAG_TEXT_BEGIN, '').replace(cls.TAG_TEXT_END, '').strip()

        tag = None
        value = None
        multiline = False

        for line in lines:
            if multiline:
                if line.rstrip().endswith(cls.TAG_TEXT_END):
                    multiline = False
                    value = extract_multiline_text(value + line.rstrip())
                    yield tag, value
                    tag, value = None, None
                else:
                    value += line
                continue
            match = cls.RE_TAG_VALUE.match(line)
            if match:
                tag, value = match[1], match[2]
                if value.startswith(cls.TAG_TEXT_BEGIN):
                    if value.endswith(cls.TAG_TEXT_END):
                        value = extract_multiline_text(value)
                    else:
                        multiline = True
                        value += '\n'
                        continue
                yield tag, value
                tag, value = None, None

        if tag:
            yield tag, value


class CommandBase(ABC):
    NAME = 'command_name'
    DESCRIPTION = 'description of this command'
    BACKUP_SUFFIX = '.bak'

    @abstractmethod
    def setup_parser(self, parser):
        pass

    @abstractmethod
    def run_command(self, args):
        pass


class CommandDispatcher:
    def __init__(self, *command_classes):
        self._command_table = {}

        description = ''
        for command_class in command_classes:
            if not issubclass(command_class, CommandBase):
                raise TypeError(
                    f'{command_class.__name__!r} not subclass of CommandBase')
            command = command_class()
            description += ('commands:\n' +
                            f'  {command.NAME:10}{command.DESCRIPTION}')
            self._command_table[command.NAME] = command

        self._parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description=description)
        self._parser.add_argument(
            '-D', '--debug',
            default=False,
            action='store_true',
            help='enable debug logs')

        subparsers = self._parser.add_subparsers()

        for name, command in self._command_table.items():
            subparser = subparsers.add_parser(
                name,
                description=command.DESCRIPTION,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            subparser.set_defaults(name=name)
            subparser.add_argument(
                '-D', '--debug',
                default=False,
                action='store_true',
                help='enable debug logs')
            command.setup_parser(subparser)

    def run_command(self):
        args = self._parser.parse_args()

        set_debug_flag(args.debug)

        if not hasattr(args, 'name'):
            print('no command specified. show help by "-h".')
            sys.exit(1)

        return (self._command_table[args.name]).run_command(args)


class CommandShow(CommandBase):
    NAME = 'show'
    DESCRIPTION = 'display information embedded by ESSTRA Core'
    KEY_BINARY_FILE_NAME = 'BinaryFileName'
    KEY_BINARY_PATH = 'BinaryPath'

    def setup_parser(self, parser):
        parser.add_argument(
            'binary', nargs='+',
            help='ESSTRA-built binary file to show embedded information')
        parser.add_argument(
            '-r', '--raw',
            action='store_true',
            help='display raw data')

    def run_command(self, args):
        for given_path in args.binary:
            print('#')
            print(f'# {self.KEY_BINARY_FILE_NAME}: {given_path}')
            try:
                path = str(Path(given_path).resolve())
                handler = MetadataHandler(path)
                string_to_display = self.__make_string_to_display(args, handler)
            except Exception as ex:
                print('#')
                print(f'Exeption: {ex!r}')
                print()
                continue
            print(f'# {self.KEY_BINARY_PATH}: {path}')
            print('#')
            print(string_to_display)

    # private
    def __make_string_to_display(self, args, handler):
        if args.raw:
            return handler.get_raw_data().decode(encoding='utf-8').replace('\0', '\n').rstrip()

        return yaml.safe_dump(handler.get_shrunk_data()).rstrip()


class CommandShrink(CommandBase):
    NAME = 'shrink'
    DESCRIPTION = 'shrink embedded information by removing duplication'

    def setup_parser(self, parser):
        parser.add_argument(
            'binary', nargs='+',
            help='ESSTRA-built binary file to shrink embedded information')
        parser.add_argument(
            '-n', '--no-backup',
            action='store_true',
            help='do not create backup of binary file')
        parser.add_argument(
            '-O', '--overwrite-backup',
            action='store_true',
            help='overwrite old backup file')
        parser.add_argument(
            '-b', '--backup-suffix',
            default=self.BACKUP_SUFFIX,
            help='suffix of backup file')

    def run_command(self, args):
        errors = 0
        for binary in args.binary:
            if binary.endswith(f'.{args.backup_suffix}'):
                message(f'skip backup file {binary!r}.')
                continue
            message(f'processing {binary!r}...')
            handler = MetadataHandler(binary)
            try:
                handler.update_metadata(
                    binary,
                    not args.no_backup,
                    args.backup_suffix,
                    args.overwrite_backup)
            except Exception as ex:
                error(f'failed to update metadata: {ex}')
                errors += 1

        if errors:
            message(f'done with {errors} error(s).')
            return 1

        message('done.')
        return 0


class CommandUpdate(CommandBase):
    NAME = 'update'
    DESCRIPTION = 'update embedded information with SPDX tag/value file'

    def setup_parser(self, parser):
        parser.add_argument(
            '-i', '--info-file', required=True,
            nargs='+',
            action='extend',
            help='spdx tag/value file containing license information')
        parser.add_argument(
            'binary', nargs='+',
            help='ESSTRA-built binary file to update embedded information')
        parser.add_argument(
            '-n', '--no-backup',
            action='store_true',
            help='do not create backup of binary file')
        parser.add_argument(
            '-O', '--overwrite-backup',
            action='store_true',
            help='overwrite old backup file')
        parser.add_argument(
            '-b', '--backup-suffix',
            default=self.BACKUP_SUFFIX,
            help='suffix of backup file')

    def run_command(self, args):
        errors = 0

        spdx_info = SpdxTagValueInfo()
        try:
            for info_file in args.info_file:
                spdx_info.read(info_file)
        except Exception as ex:
            error(f'cannot read {info_file!r}: {ex!r}')
            return False

        for binary in args.binary:
            if binary.endswith(f'.{args.backup_suffix}'):
                message(f'skip backup file {binary!r}.')
                continue
            message(f'processing {binary!r}...')

            handler = MetadataHandler(binary)
            for path, checksum, fileinfo in handler.enumerate_files():
                spdx_fileinfo = spdx_info.get_fileinfo(path, checksum)
                if not spdx_fileinfo:
                    continue
                license_info = spdx_fileinfo[
                    SpdxTagValueInfo.TAG_LICENSE_INFO_IN_FILE]
                fileinfo[MetadataHandler.KEY_LICENSE_INFO] = license_info

            try:
                handler.update_metadata(
                    binary,
                    not args.no_backup,
                    args.backup_suffix,
                    args.overwrite_backup)
            except Exception as ex:
                error(f'failed to update metadata: {ex}')
                errors += 1

        if errors:
            message(f'done with {errors} error(s).')
            return False

        message('done.')
        return True


class CommandStrip(CommandBase):
    NAME = 'strip'
    DESCRIPTION = 'discard metadata from binary files built with ESSTRA Core'

    def setup_parser(self, parser):
        parser.add_argument(
            'binary', nargs='+',
            help='ESSTRA-built binary file')
        parser.add_argument(
            '-n', '--no-backup',
            action='store_true',
            help='do not create backup of binary file')
        parser.add_argument(
            '-O', '--overwrite-backup',
            action='store_true',
            help='overwrite old backup file')
        parser.add_argument(
            '-b', '--backup-suffix',
            default=self.BACKUP_SUFFIX,
            help='suffix of backup file')

    def run_command(self, args):
        errors = 0
        for binary in args.binary:
            if binary.endswith(f'.{args.backup_suffix}'):
                message(f'skip backup file {binary!r}.')
                continue
            message(f'processing {binary!r}...')
            handler = MetadataHandler(binary)
            try:
                handler.strip_metadata(
                    binary,
                    not args.no_backup,
                    args.backup_suffix,
                    args.overwrite_backup)
            except Exception as ex:
                error(f'failed to update metadata: {ex}')
                errors += 1

        if errors:
            message(f'done with {errors} error(s).')
            return 1

        message('done.')
        return 0



def main():
    dispatcher = CommandDispatcher(
        CommandShow,
        CommandShrink,
        CommandUpdate,
        CommandStrip
    )
    return dispatcher.run_command()


#
# main
#
if __name__ == '__main__':
    sys.exit(main())
