import pytest
from conftest import run_command
import yaml
from pathlib import Path

ESSTRA_UTIL = "util/esstra"


def verify_license_info(metadata, expected_files, expected_license=['NOASSERTION']):
    """
    Verify license information for specified files in metadata.
    
    Args:
        metadata: Parsed YAML metadata dictionary
        expected_files: Set or list of filenames to verify
        expected_license: Expected license value (default: ['NOASSERTION'])
    
    Returns:
        set: Found files that matched
    
    Raises:
        AssertionError: If license doesn't match or files are missing
    """
    if isinstance(expected_files, str):
        expected_files = {expected_files}
    elif isinstance(expected_files, list):
        expected_files = set(expected_files)
    
    found_files = set()

    for directory in metadata.get("SourceFiles", []):
        for fileinfo in directory.get("Files", []):
            filename = fileinfo.get("File")
            if filename in expected_files:
                binary_license = fileinfo.get("LicenseInfo")
                assert binary_license == expected_license, \
                    f"File '{filename}': Expected {expected_license}, got {binary_license}"
                found_files.add(filename)

    # Verify all expected files were found
    missing_files = expected_files - found_files
    assert not missing_files, f"Missing files in metadata: {missing_files}"
    
    return found_files


@pytest.mark.update_test(serial="01")
def test_update_basic(setup_test_files):
    """
    Verify basic update command.

    Command:
    esstra update binary -i info_file

    Expected Behaviour:
    Metadata is updated successfully.
    """
    binary = setup_test_files["with_metadata"]
    info_file = setup_test_files["info_file"]

    cmd = f"{ESSTRA_UTIL} update {binary} -i {info_file} && {ESSTRA_UTIL} show {binary}"
    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 0, f"Command failed with return code {return_code}"

    metadata = yaml.safe_load(stdout)
    
    # Use the helper function
    verify_license_info(metadata, "simple.c")


@pytest.mark.update_test(serial="02")
def test_update_multiple_binaries(setup_test_files):
    """
    Verify update command with multiple binaries.
    """
    binaries = setup_test_files["with_multiple_metadata"]
    info_files = [
        setup_test_files["info_file2"],
        setup_test_files["info_file3"]
    ]

    # Run the update command
    cmd = f"{ESSTRA_UTIL} update {binaries} -i {' '.join(info_files)} && {ESSTRA_UTIL} show {binaries}"
    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 0, f"Command failed with return code {return_code}"

    metadata = yaml.safe_load(stdout)
    
    # Use the helper function with multiple files
    expected_files = ["main.c", "helper.c"]
    verify_license_info(metadata, expected_files)


@pytest.mark.update_test(serial="03")
def test_update_invalid_info_file(setup_test_files):
    """
    Verify update with invalid SPDX file.
    """
    binary = setup_test_files["with_metadata"]

    cmd = (
    f"{ESSTRA_UTIL} update "
    f"{binary} -i non_existent.spdx"
    )

    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 1
    assert "cannot read" in stderr.lower()


@pytest.mark.update_test(serial="04")
def test_update_non_existent_binary(setup_test_files):
    """
    Verify update with non-existent binary.
    """
    info_file = setup_test_files["info_file"]

    cmd = (
    f"{ESSTRA_UTIL} update "
    f"non_existent_binary -i {info_file}"
    )

    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 1
    assert 'not found' in stderr


@pytest.mark.update_test(serial="05")
def test_update_silent_option(setup_test_files):
    """
    Verify --silent suppresses errors.
    """
    info_file = setup_test_files["info_file"]

    cmd = (
    f"{ESSTRA_UTIL} update "
    f"--silent non_existent_binary -i {info_file}"
    )

    stdout, stderr, return_code = run_command(cmd)

    assert "failed to update" not in stderr.lower()


@pytest.mark.update_test(serial="06")
def test_update_show_error_option(setup_test_files):
    """
    Verify --show-error overrides --silent.
    """
    info_file = setup_test_files["info_file"]

    cmd = (
    f"{ESSTRA_UTIL} update "
    f"--silent --show-error "
    f"non_existent_binary -i {info_file}"
    )

    stdout, stderr, return_code = run_command(cmd)

    assert "failed to update" in stderr.lower()


@pytest.mark.update_test(serial="07")
def test_update_without_metadata(setup_test_files):
    """
    Verify update on binary without metadata.
    """
    binary = setup_test_files["without_plugin"]
    info_file = setup_test_files["info_file"]

    cmd = f"{ESSTRA_UTIL} update {binary} -i {info_file}"

    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 1
    assert "section not found" in stderr.lower()


@pytest.mark.update_test(serial="08")
def test_update_ignore_errors(setup_test_files):
    """
    Verify -I returns success even when errors occur.
    """
    binary = setup_test_files['without_plugin']
    info_file = setup_test_files["info_file"]

    cmd = (
    f"{ESSTRA_UTIL} update -I {binary}  -i {info_file}"
    )

    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 0
    assert 'failed to update' in stderr
    assert 'errors ignored.' in stderr


@pytest.mark.update_test(serial="09")
def test_update_backup(setup_test_files):
    """
    Verify update with backup option.
    """
    binary = setup_test_files["with_metadata"]
    info_file = setup_test_files["info_file"]

    cmd = (
    f"{ESSTRA_UTIL} update "
    f"{binary} -b -i {info_file}  && {ESSTRA_UTIL} "
    f" show {binary}.bak"
    )

    stdout, stderr, return_code = run_command(cmd)

    assert return_code == 0
    metadata = yaml.safe_load(stdout)
    
    # Use the helper function
    verify_license_info(metadata, "simple.c")

    # Remove the backup file
    Path(f'{binary}.bak').unlink()

@pytest.mark.update_test(serial="10")
def test_update_with_backup_suffix(setup_test_files):
    '''Verify 'esstra shrink' with backup suffix option

    Command:
        $ python3 esstra.py update -b -s .backup binary

    Expected Behavior:
        Backup file created with original metadata using `.backup` extension.
    '''
    binary = setup_test_files['with_metadata']
    info_file = setup_test_files["info_file"]
    backup_extension = '.backup'
    cmd = (f'{ESSTRA_UTIL} update -b --backup-suffix {backup_extension}'
           f' {binary} -i {info_file} && {ESSTRA_UTIL} show {binary}{backup_extension}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    metadata = yaml.safe_load(stdout)
    
    # Use the helper function
    verify_license_info(metadata, "simple.c")

    # Not Removing the backup file for next backup overwrite test


@pytest.mark.update_test(serial="11")
def test_update_with_backup_overwrite(setup_test_files):
    '''Verify 'esstra update' with backup overwrite option

    Command:
        $ python3 esstra.py update -b --backup-suffix .backup -O binary

    Expected Behavior:
        Backup file created with original metadata using `.backup` extension.
    '''
    binary = setup_test_files['with_metadata']
    info_file = setup_test_files["info_file"]
    backup_extension = '.backup'
    cmd = (f'{ESSTRA_UTIL} update -b --backup-suffix {backup_extension} -O {binary} -i {info_file} && '
           f'{ESSTRA_UTIL} show {binary}{backup_extension}')
    stdout, stderr, return_code = run_command(cmd)
    assert return_code == 0
    metadata = yaml.safe_load(stdout)
    # Use the helper function
    verify_license_info(metadata, "simple.c")

    # Remove the backup file
    Path(f'{binary}{backup_extension}').unlink()