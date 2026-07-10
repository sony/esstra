# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

import pytest

from conftest import run_command

ESSTRA_CORE = 'esstracore.so'
TEST_DIR = 'test_binaries'
ESSTRA_UTIL = 'util/esstra'


@pytest.mark.show_test(serial="01")
def test_show_basic(setup_test_files):
    '''Verify basic show command

    Command:
        $ esstra.py show binary

    Expected Behavior:
        YAML output should have 'SourceFiles' and 'SHA1'.
    '''
    binary = setup_test_files['with_metadata']
    cmd = f'{ESSTRA_UTIL} show {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout


@pytest.mark.show_test(serial="02")
@pytest.mark.skip(reason="Feature not implemented yet")
def test_show_raw(setup_test_files):
    '''Test the `esstra show` command with `--raw` option

    Command:
        $ esstra.py show -r binary

    Expected Behavior:
        YAML output should have a `---` formatting.
    '''
    binary = setup_test_files['with_metadata']
    cmd = f'{ESSTRA_UTIL} show -r {binary}'
    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 0
    # Raw output should have '---' YAML formatting
    # assert '---' in stdout


@pytest.mark.show_test(serial="04")
def test_show_multiple_binaries(setup_test_files):
    '''Test the `esstra show` command with multiple binary files

    Command:
        $ esstra.py show binary1 binary2

    Expected Behaviour:
        Metadata for each binary displayed, alongwith
        file paths and SHA1 checksums information.
    '''
    binaries = setup_test_files['with_multiple_metadata']
    cmd = f'{ESSTRA_UTIL} show  {binaries}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout
    for binary in binaries.split(' '):
        assert binary in stdout


@pytest.mark.show_test(serial="05")
def test_show_non_existent_file():
    '''Test the `esstra show` command with non-existent file

    Command:
        $ esstra.py show non_existent_file

    Expected Behaviour:
        Error message indicating file not found on standard output
    '''
    cmd = f'{ESSTRA_UTIL} show  non_existent_file'
    stdout, stderr, return_code = run_command(cmd)
    assert 'not found' in stderr

@pytest.mark.show_test(serial="06")
def test_show_silent_option():
    '''Test the `esstra show` command with --silent option

    Command:
        $ esstra.py show --silent non_existent_file

    Expected Behaviour:
        Error message won't be shown
    '''
    cmd = f'{ESSTRA_UTIL} show --silent non_existent_file'
    stdout, stderr, return_code = run_command(cmd)
    assert 'not found' not in stderr

@pytest.mark.show_test(serial="06")
def test_show_show_error_option():
    '''Test the `esstra show` command with both --silent option
       and --show-error option. The --show-error option takes
       higher precedence.

    Command:
        $ esstra.py show --silent --show-error non_existent_file

    Expected Behaviour:
        Error message won't be shown
    '''
    cmd = f'{ESSTRA_UTIL} show --silent --show-error non_existent_file'
    stdout, stderr, return_code = run_command(cmd)
    assert 'not found' in stderr

@pytest.mark.show_test(serial="06")
def test_show_without_metadata(setup_test_files):
    '''Test the `esstra show` command with a binary without esstra metadata

    Command:
        $ esstra.py show binary_without_metadata

    Expected Behaviour:
        Error message indicating section not found
    '''
    binary = setup_test_files['without_plugin']
    cmd = f'{ESSTRA_UTIL} show {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 1
    assert 'section not found' in stderr


@pytest.mark.show_test(serial="07")
def test_show_debug(setup_test_files):
    '''Test the `esstra show` command with debug flag

    Command:
        $ esstra.py show -D binary_file

    Expected Behaviour:
        Metadata displayed in YAML format with file paths and SHA1 checksums.
        Note:
        Debug code does not necessarily always provide debug log.
        So, it is enough to just test the expected results.
    '''
    binary = setup_test_files['with_metadata']
    cmd = f'{ESSTRA_UTIL} show -D {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'SourceFiles' in stdout
    assert 'SHA1' in stdout


@pytest.mark.show_test(serial="08")
def test_show_ignore_error():
    '''Test the `esstra show` command with ignore-errors flag

    Command:
        $ esstra.py show -I non_existent_file

    Expected Behaviour:
        The current '--ignore-errors' option forces the return of 0 as
        the exit code instead of an error code, even if some errors occur,
        with no changes to the console output
    '''
    cmd = f'{ESSTRA_UTIL} show -I non_existent_file'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
