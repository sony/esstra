# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

import subprocess
import pytest
import shutil

from pathlib import Path

ESSTRA_CORE = 'esstracore.so'
TEST_DIR = 'test_binaries'
ESSTRA_UTIL = 'util/esstra.py'


def run_command(command):
    '''Run a shell command and return the result and return code'''
    process = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process.stdout, process.stderr, process.returncode


def get_esstra_installed_path():
    '''Fetch esstra installed path'''
    cmd = """
    CXX=$(which g++) &&
    GCC_ARCH=$($CXX -dumpmachine) &&
    GCC_MAJOR_VERSION=$($CXX -dumpversion) &&
    PREFIX='/usr/local' &&
    INSTALLDIR="${PREFIX}/lib/gcc/${GCC_ARCH}/${GCC_MAJOR_VERSION}/plugin" &&
    echo $INSTALLDIR
    """
    stdout, stderr, return_code = run_command(cmd)
    return stdout.strip()


def compile_with_plugin(source_file, output_file):
    '''Compile a source file with the ESSTRA plugin'''
    esstra_install_dir = get_esstra_installed_path()
    esstra_plugin_path = f'{esstra_install_dir}/{ESSTRA_CORE}'
    cmd = f'gcc -fplugin={esstra_plugin_path} {source_file} -o {output_file}'

    return run_command(cmd)


def compile_without_plugin(source_file, output_file):
    '''Compile a source file without the ESSTRA plugin'''
    cmd = f'gcc {source_file} -o {output_file}'
    return run_command(cmd)


@pytest.fixture(scope='session', autouse=True)
def test_initial_setup():
    '''Prepare a clean envionment by removing and reinstalling files'''
    # Remove built esstra.so and it's installation
    clean_cmd = ('make -C ../ clean && sudo make -C ../ uninstall')
    stdout, stderr, return_code = run_command(clean_cmd)

    # Re-build esstra and install it
    cmd = 'make -C ../ && sudo make -C ../ install'
    stdout, stderr, return_code = run_command(cmd)

    # Yield to allow tests to run
    yield

    # Clean the environment again after all tests have run
    stdout, stderr, return_code = run_command(clean_cmd)


@pytest.fixture(scope='module')
def generate_test_files():
    '''Setup test environment - create test files and directories'''
    # Create a test directory as a Path object once
    test_dir = Path(TEST_DIR)
    test_dir.mkdir(exist_ok=True)

    # Use the Path object for file operations
    simple_c = test_dir / 'simple.c'
    helper_c = test_dir / 'helper.c'

    # Create a simple C file for testing
    with open(simple_c, 'w') as f:
        f.write('''
        #include <stdio.h>
        int main() {
            printf('Hello, ESSTRA!\\n');
            return 0;
        }
        ''')

    with open(helper_c, 'w') as f:
        f.write('''
        #include <stdio.h>
        void main() {
            printf('Helper function\\n');
        }
        ''')

    # Generate binaries
    binary_with_metadata = test_dir / 'binary_with_metadata'
    another_binary = test_dir / 'another_binary_with_metadata'
    binary_without_metadata = test_dir / 'binary_without_metadata'

    compile_with_plugin(str(simple_c), str(binary_with_metadata))
    compile_with_plugin(str(helper_c), str(another_binary))
    compile_without_plugin(str(simple_c), str(binary_without_metadata))

    # Yield to allow tests to run
    yield

    # Clean up the above created test directory after tests
    shutil.rmtree(test_dir)


@pytest.fixture
def setup_test_files(generate_test_files):
    '''Test fixture to create test binary files'''
    # Create test binary files with metadata
    test_dir = Path('./test_binaries')
    binary_with_metadata = test_dir / 'binary_with_metadata'
    binary_without_metadata = test_dir / 'binary_without_metadata'
    another_binary_with_metadata = test_dir / 'another_binary_with_metadata'

    # Ensure test files exist
    assert binary_with_metadata.exists(), 'Test binary with metadata not found'
    assert binary_without_metadata.exists(), ('Test binary without'
                                              'metadata not found')
    assert another_binary_with_metadata.exists(), ('Test binary with another'
                                                   ' metadata not found')

    return {
        'with_metadata': str(binary_with_metadata),
        'without_metadata': str(binary_without_metadata),
        'with_multiple_metadata': (f'{str(binary_with_metadata)} '
                                   f'{str(another_binary_with_metadata)}')
    }


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
    assert '---' in stdout


@pytest.mark.show_test(serial="03")
def test_show_no_comments(setup_test_files):
    '''Test the `esstra show` command with no-comments option

    Command:
        $ esstra.py show -n binary_file

    Expected Behaviour:
        Metadata displayed without comment lines.
        It means no lines should start with # character
    '''
    binary = setup_test_files['with_metadata']
    cmd = f'{ESSTRA_UTIL} show -n {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert '# ' not in stdout


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
    assert 'not found' in stdout


@pytest.mark.show_test(serial="06")
def test_show_without_metadata(setup_test_files):
    '''Test the `esstra show` command with a binary without esstra metadata

    Command:
        $ esstra.py show binary_without_metadata

    Expected Behaviour:
        Error message indicating section not found
    '''
    binary = setup_test_files['without_metadata']
    cmd = f'{ESSTRA_UTIL} show {binary}'
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    assert 'Exeption: RuntimeError' in stdout
    assert 'section not found' in stdout


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
