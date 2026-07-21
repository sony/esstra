# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

import pytest

from pathlib import Path

from conftest import run_command

ESSTRA_CORE = 'esstracore.so'
TEST_DIR = 'test_binaries'
ESSTRA_UTIL = 'util/esstra'


@pytest.mark.shrink_test(serial="01")
def test_shrink_basic(setup_test_files):
    '''Verify basic show command

    Command:
        $ python3 esstra.py shrink binary
        $ python3 esstra.py show binary

    Expected Behavior:
        YAML output should have 'SourceFiles' and 'SHA1'.
    '''
    binary = setup_test_files['with_metadata']
    cmd = (f'{ESSTRA_UTIL} shrink {binary} && {ESSTRA_UTIL} show {binary}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout

@pytest.mark.shrink_test(serial="02")
def test_shrink_with_verbose(setup_test_files):
    '''Verify basic show command

    Command:
        $ python3 esstra.py shrink -v binary
        $ python3 esstra.py show binary

    Expected Behavior:
        Phrase 'shrinking metadata of' and '* done.' should be in stdout.
        YAML output should have 'SourceFiles' and 'SHA1'.
    '''
    binary = setup_test_files['with_metadata']
    cmd = (f'{ESSTRA_UTIL} shrink -v {binary} && {ESSTRA_UTIL} show {binary}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'shrinking metadata of' in stderr
    assert '* done.' in stderr
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout

@pytest.mark.shrink_test(serial="03")
def test_shrink_with_backup(setup_test_files):
    '''Verify 'esstra shrink' with backup option

    Command:
        $ python3 esstra.py shrink -b binary

    Expected Behavior:
        Backup file created with original metadata using `.bak` extension.
    '''
    binary = setup_test_files['with_metadata']
    cmd = (f'{ESSTRA_UTIL} shrink -b {binary} && {ESSTRA_UTIL} '
           f' show {binary}.bak')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout

    # Remove the backup file
    Path(f'{binary}.bak').unlink()


@pytest.mark.shrink_test(serial="04")
def test_shrink_with_backup_suffix(setup_test_files):
    '''Verify 'esstra shrink' with backup suffix option

    Command:
        $ python3 esstra.py shrink -b -s .backup binary

    Expected Behavior:
        Backup file created with original metadata using `.backup` extension.
    '''
    binary = setup_test_files['with_metadata']
    backup_extension = '.backup'
    cmd = (f'{ESSTRA_UTIL} shrink -b --backup-suffix {backup_extension}'
           f' {binary} && {ESSTRA_UTIL} show {binary}{backup_extension}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout

    # Not Removing the backup file for next backup overwrite test


@pytest.mark.shrink_test(serial="05")
def test_shrink_with_backup_overwrite(setup_test_files):
    '''Verify 'esstra shrink' with backup overwrite option

    Command:
        $ python3 esstra.py shrink -b --backup-suffix .backup -O binary

    Expected Behavior:
        Backup file created with original metadata using `.backup` extension.
    '''
    binary = setup_test_files['with_metadata']
    backup_extension = '.backup'
    cmd = (f'{ESSTRA_UTIL} shrink -b --backup-suffix {backup_extension} -O {binary} && '
           f'{ESSTRA_UTIL} show {binary}{backup_extension}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout

    # Remove the backup file
    Path(f'{binary}{backup_extension}').unlink()


@pytest.mark.shrink_test(serial="06")
def test_shrink_with_multiple_binaries(setup_test_files):
    '''Verify 'esstra shrink' with multiple binaries

    Command:
        $ python3 esstra.py shrink bin1 bin2
        $ python3 esstra.py show bin1 bin2

    Expected Behavior:
        All binaries shrunk successfully.
        Exit code should be Zero.
        All binaries names should be in stdout.

    '''
    binaries = setup_test_files['with_multiple_metadata']
    binaries_list = binaries.split()
    cmd = (f'{ESSTRA_UTIL} shrink {binaries} && '
           f'{ESSTRA_UTIL} show {binaries}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert stdout.count('Headers:') == len(binaries_list)
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout
    for binary in binaries_list:
        assert binary in stdout


@pytest.mark.shrink_test(serial="07")
def test_shrink_non_existent_file(setup_test_files):
    '''Test the `esstra shrink` command on a non-existent file.

    Command:
        $ python3 esstra.py shrink non_existent file

    Expected Behavior:
        Exit code should be 1.
        'not found' message displayed.

    '''
    cmd = f'{ESSTRA_UTIL} shrink non_existent_file'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1
    assert 'not found' in stderr


@pytest.mark.shrink_test(serial="08")
def test_shrink_without_metadata(setup_test_files):
    '''Test the `esstra shrink` command with a binary without esstra metadata.

    Command:
        $ python3 esstra.py shrink binary_without_metadata

    Expected Behaviour:
        Error message indicating section not found
        Exit code should be 1.
    '''
    binary = setup_test_files['without_plugin']
    cmd = f'{ESSTRA_UTIL} shrink {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1
    assert "failed to update metadata: section not found: '.esstra'" in stderr


@pytest.mark.shrink_test(serial="09")
def test_shrink_with_ignore_errors(setup_test_files):
    '''Test the `esstra shrink` command with ignore errors option

    Command:
        $ python3 esstra.py shrink -I binary_without_metadata

    Expected Behaviour:
        Error message displayed but exit code 0.
        "errors ignored" message in stdout.
    '''
    binary = setup_test_files['without_plugin']
    cmd = f'{ESSTRA_UTIL} shrink -I {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'failed to update metadata' in stderr
    assert 'errors ignored.' in stderr

