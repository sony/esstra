# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

import pytest
import shutil
from pathlib import Path
from conftest import run_command

ESSTRA_UTIL = 'util/esstra'

def create_test_copy(setup_test_files, key='with_metadata', suffix='_test_copy'):
    org_binary = setup_test_files[key]
    binary = org_binary + suffix
    shutil.copy(org_binary, binary)
    return binary


@pytest.mark.rm_test(serial="01")
def test_remove_basic(setup_test_files):
    '''Verify basic show command

    Command:
        $ python3 esstra.py rm binary
        $ python3 esstra.py show binary

    Expected Behavior:
        stdout output should have 'section not found: '.esstra''
    '''
    binary = create_test_copy(setup_test_files)
    cmd = (f'{ESSTRA_UTIL} rm {binary}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    cmd_show = (f'{ESSTRA_UTIL} show {binary}')
    show_stdout, show_stderr, show_return_code = run_command(cmd_show)
    assert show_return_code == 1 and "section not found: '.esstra'" in show_stderr

@pytest.mark.rm_test(serial="02")
def test_remove_with_verbose(setup_test_files):
    '''Verify basic show command

    Command:
        $ python3 esstra.py rm -v binary
        $ python3 esstra.py show binary

    Expected Behavior:
        show_stderr output should have 'section not found: '.esstra''
    '''
    binary = create_test_copy(setup_test_files)
    
    cmd = f'{ESSTRA_UTIL} rm -v {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0 and "* removing metadata from" and "* done." in stderr
    cmd_show = (f'{ESSTRA_UTIL} show {binary}')
    show_stdout, show_stderr, show_return_code = run_command(cmd_show)
    assert show_return_code == 1 and "section not found: '.esstra'" in show_stderr

@pytest.mark.rm_test(serial="03")
def test_remove_with_backup(setup_test_files):
    '''Verify 'esstra rm' with backup option

    Command:
        $ python3 esstra.py rm -b binary

    Expected Behavior:
        Backup file created with original metadata using `.bak` extension.
    '''
    binary = create_test_copy(setup_test_files)
    cmd = (f'{ESSTRA_UTIL} rm -b {binary} && {ESSTRA_UTIL} show {binary}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1 and "section not found: '.esstra'" in stderr
    cmd_show = (f'{ESSTRA_UTIL} show {binary}.bak')
    show_stdout, show_stderr, show_return_code = run_command(cmd_show)
    assert show_return_code == 0 and 'SourceFiles' and 'SHA1' in show_stdout

    # Remove the backup file
    Path(f'{binary}.bak').unlink()


@pytest.mark.rm_test(serial="04")
def test_remove_with_backup_suffix(setup_test_files):
    '''Verify 'esstra rm' with backup suffix option

    Command:
        $ python3 esstra.py rm -b -s .backup binary

    Expected Behavior:
        Backup file created with original metadata.
    '''
    binary = create_test_copy(setup_test_files)
    backup_extension = '.backup'
    cmd = (f'{ESSTRA_UTIL} rm -b --backup-suffix {backup_extension} {binary} && {ESSTRA_UTIL} show {binary}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1 and "section not found: '.esstra'" in stderr
    cmd_show =(f'{ESSTRA_UTIL} show {binary}{backup_extension}')
    show_stdout, show_stderr, show_return_code = run_command(cmd_show)
    assert show_return_code == 0 and 'SourceFiles' and 'SHA1' in show_stdout

    # Not Removing the backup file for next backup overwrite test


@pytest.mark.rm_test(serial="05")
def test_remove_with_backup_overwrite(setup_test_files):
    '''Verify 'esstra rm' with backup overwrite option

    Command:
        $ python3 esstra.py rm -b --backup-suffix .backup -O binary

    Expected Behavior:
        Backup file created with original metadata using `.backup` extension.
    '''
    binary = create_test_copy(setup_test_files)
    backup_extension = '.bak'
    cmd = (f'{ESSTRA_UTIL} rm -b --backup-suffix {backup_extension} -O {binary}.backup && {ESSTRA_UTIL} show {binary}.backup')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1 and "section not found: '.esstra'" in stderr
    cmd_show = (f'{ESSTRA_UTIL} show {binary}.backup.bak')
    show_stdout, show_stderr, show_return_code = run_command(cmd_show)
    assert show_return_code == 0 and 'SourceFiles' and 'SHA1' in show_stdout

    # Remove the backup file
    Path(f'{binary}.backup').unlink()
    Path(f'{binary}.backup.bak').unlink()


@pytest.mark.rm_test(serial="06")
def test_remove_with_multiple_binaries(setup_test_files):
    '''Verify 'esstra rm' with multiple binaries

    Command:
        $ python3 esstra.py rm bin1 bin2
        $ python3 esstra.py show bin1 bin2

    Expected Behavior:
        show_stderr output should have 'section not found: '.esstra''

    '''
    
    binaries = create_test_copy(setup_test_files, key='multi_source_binary_with_metadata')
    cmd = (f'{ESSTRA_UTIL} rm {binaries}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    cmd_show = (f'{ESSTRA_UTIL} show {binaries}')
    show_stdout, show_stderr, show_return_code = run_command(cmd_show)
    assert show_return_code == 1 and "section not found: '.esstra'" in show_stderr


@pytest.mark.rm_test(serial="07")
def test_remove_non_existent_file():
    '''Test the `esstra rm` command on a non-existent file.

    Command:
        $ python3 esstra.py rm non_existent file

    Expected Behavior:
        Exit code should be 1.
        'not found' message displayed.

    '''
    cmd = f'{ESSTRA_UTIL} rm non_existent_file'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1 and 'not found' in stderr


@pytest.mark.rm_test(serial="08")
def test_remove_without_metadata(setup_test_files):
    '''Test the `esstra rm` command with a binary without esstra metadata.

    Command:
        $ python3 esstra.py rm binary_without_metadata

    Expected Behaviour:
        Error message indicating section not found
        Exit code should be 1.
    '''
    binary = create_test_copy(setup_test_files, key='without_plugin')
    cmd = f'{ESSTRA_UTIL} rm {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1 and "failed to remove metadata" and "section not found" in stderr.lower()


@pytest.mark.rm_test(serial="09")
def test_remove_with_ignore_errors(setup_test_files):
    '''Test the `esstra rm` command with ignore errors option

    Command:
        $ python3 esstra.py rm -I binary_without_metadata

    Expected Behaviour:
        Error message displayed but exit code 0.
        "errors ignored" message in stdout.
    '''
    binary = create_test_copy(setup_test_files, key='without_plugin')
    cmd = f'{ESSTRA_UTIL} rm -I {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0 and 'failed to remove metadata' and 'errors ignored.' in stderr

