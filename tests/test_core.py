import pytest
from pathlib import Path

from conftest import run_command

ESSTRA_SECTION_NAME = '.esstra'
ESSTRA_EXTRACTED_DATA_FILE = 'extracted_info.txt'
ESSTRA_EXTRACTED_MULTI_DATA_FILE = 'extracted_multi_info.txt'


def check_esstra_section_exists(binary_file, section_name):
    '''Check if esstra section exists in the generated binary file'''
    cmd = f'readelf -S {binary_file} | fgrep -q \'{section_name}\''
    _, _, return_code = run_command(cmd)
    return return_code == 0


@pytest.mark.core_test(serial='01')
def test_core_plugin_installed(get_esstra_so_link_paths):
    '''Test to verify if plugin is installed

    Test Steps:
        1) Check if `esstra_installed_path` exists.

    Expected Behaviour:
        `assert Path(esstra_installed_path).exists()` should return True
    '''
    esstra_installed_path, esstra_installed_link = get_esstra_so_link_paths
    # Verify plugin exists
    assert Path(esstra_installed_path).exists(
    ), f'Plugin not found at {esstra_installed_path}'


@pytest.mark.core_test(serial='02')
def test_core_section_exists_with_plugin(setup_test_files):
    '''Test to verify if the `ESSTRA_SECTION_NAME` exists in the binary

    Test Steps:
        Use readelf to get binary details and check if it has
        `ESSTRA_SECTION_NAME`.

    Expected Behaviour:
        Function `check_esstra_section_exists` should return True.
    '''
    binary = setup_test_files['with_metadata']

    # Check if section exists
    section_exists = check_esstra_section_exists(binary, ESSTRA_SECTION_NAME)
    assert section_exists, (f'Section {ESSTRA_SECTION_NAME} not found in '
                            'binary compiled with plugin')


@pytest.mark.core_test(serial='03')
def test_core_section_not_exists_without_plugin(setup_test_files):
    '''Test to verify section doesn't exist in the binary compiled
       without plugin.

    Test Steps:
        Use readelf to get binary details and check if it has
        `ESSTRA_SECTION_NAME`.

    Expected Behaviour:
        Function `check_esstra_section_exists` should return False.
    '''
    binary = setup_test_files['without_plugin']
    # Check if section exists (should not)
    section_exists = check_esstra_section_exists(binary, ESSTRA_SECTION_NAME)
    assert not section_exists, (f'Section {ESSTRA_SECTION_NAME} found in '
                                'binary compiled without plugin')


@pytest.mark.core_test(serial='04')
def test_esstra_section_content(setup_test_files, tmp_path):
    '''Test to examine the esstra section content

    Test Steps:
        1) Use objcopy to dump esstra section data in a txt file
        2) Check if esstra checksum algorithm(SHA1) exist in the txt file
        3) Check if expected source file exist in the txt file

    Expected Behaviour:
        Esstra checksum algorithm and expected source file present in txt file
    '''
    binary = setup_test_files['with_metadata']
    extracted_file = tmp_path / ESSTRA_EXTRACTED_DATA_FILE
    cmd = (f'objcopy --dump-section {ESSTRA_SECTION_NAME}='
           f'{extracted_file} {binary}')
    _, stderr, return_code = run_command(cmd)
    assert return_code == 0, 'Extraction of esstra section data failed'

    # Read the file content
    file_content = None
    with open(extracted_file, 'rb') as fd:
        file_content = fd.read()
    assert b'SHA1:' in file_content
    assert b'simple.c' in file_content


@pytest.mark.core_test(serial='05')
def test_multi_file_compilation(setup_test_files):
    '''Test to verify plugin works with multiple source files

    Test Steps:
        1) Compile multiple source files with esstra plugin
        2) Check if esstra section exists

    Expected Behaviour:
        Function `check_esstra_section_exists` should return True.
    '''

    # Check if section exists
    binary = setup_test_files['multi_source_binary_with_metadata']
    section_exists = check_esstra_section_exists(binary, ESSTRA_SECTION_NAME)
    assert section_exists, (f'Section {ESSTRA_SECTION_NAME} not found '
                            'in multi source binary')


@pytest.mark.core_test(serial='06')
def test_multi_source_files(setup_test_files, tmp_path):
    '''Test to verify if multiple source filenames exist in the binary
       generated using multiple source files

    Test Steps:
        1) Use objcopy to dump esstra section data in a txt file
        2) Check if expected source files exist in the txt file

    Expected Behaviour:
        Esstra expected source files present in txt file
    '''

    binary = setup_test_files['multi_source_binary_with_metadata']
    extracted_file = tmp_path / ESSTRA_EXTRACTED_MULTI_DATA_FILE
    cmd = (f'objcopy --dump-section {ESSTRA_SECTION_NAME}='
           f'{extracted_file} {binary}')
    _, stderr, return_code = run_command(cmd)
    assert return_code == 0, 'Extraction of esstra section data failed'

    # Read the file content
    file_content = None
    with open(extracted_file, 'rb') as fd:
        file_content = fd.read()
    # Test the file data
    assert b'main.c' in file_content
    assert b'helper.c' in file_content


@pytest.mark.core_test(serial='07')
def test_with_spec_installed(compile_fresh):
    '''Test with spec file installation, without explicitly specifying
       the plugin.

    Test Steps:
        1) Install the spec file
        2) Compile without explicitly specifying plugin
        3) Check if Esstra section exists in the generated binary

    Expected Behaviour:
        Esstra Section should exist in the binary
    '''
    # Install the spec file
    cmd = ('sudo make install-specs')
    _, stderr, return_code = run_command(cmd)
    assert return_code == 0, 'Installation of spec file failed!'

    # Compile fresh (without plugin flag - spec should handle it)
    source = 'test_binaries/simple.c'
    binary = 'test_binaries/binary_spec_test'
    _, stderr, return_code = compile_fresh(source, binary)
    assert return_code == 0, f'Compilation failed: {stderr}'

    # Check if section exists (it should)
    section_exists = check_esstra_section_exists(binary, ESSTRA_SECTION_NAME)
    assert section_exists, (f'Section {ESSTRA_SECTION_NAME} not found in '
                            'binary compiled without plugin')


@pytest.mark.core_test(serial='08')
def test_with_spec_uninstalled(compile_fresh):
    '''Test with spec uninstalled and without the plugin.

    Test Steps:
        1) Uninstall the spec file
        2) Compile without the plugin
        3) Check if Esstra section exists in the generated binary

    Expected Behaviour:
        Esstra Section should not exist in the binary
    '''
    # Uninstall the spec file
    cmd = ('sudo make uninstall-specs')
    _, stderr, return_code = run_command(cmd)
    assert return_code == 0, 'Uninstall of spec file failed!'

    # Compile fresh (without plugin flag)
    source = 'test_binaries/simple.c'
    binary = 'test_binaries/binary_without_spec_test'
    _, stderr, return_code = compile_fresh(source, binary)
    assert return_code == 0, f'Compilation failed: {stderr}'

    # Check if section exists (it should)
    section_exists = check_esstra_section_exists(binary, ESSTRA_SECTION_NAME)
    assert not section_exists, (f'Unexpected: Section {ESSTRA_SECTION_NAME} '
                                'found in binary compiled without plugin')
