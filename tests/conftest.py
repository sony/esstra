import pytest
import subprocess
import shutil

from pathlib import Path

TEST_DIR = 'test_binaries'
ESSTRA_FILE_NAME = 'esstracore.so'
ESSTRA_LINK_NAME = 'esstralink.so'


def run_command(cmd, step_name=None, fail_on_error=False):
    '''Run a shell command and return stdout, stderr, and return code.

    Args:
        cmd: The shell command to run.
        step_name: Optional name for the step (used in failure message).
        fail_on_error: If True, calls pytest.fail() on non-zero return code.
    '''
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if fail_on_error and result.returncode != 0:
        pytest.fail(
            f"{step_name or 'Command'} failed\n"
            f"Command: {cmd}\n"
            f"Return code: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return result.stdout, result.stderr, result.returncode


@pytest.fixture(scope='session')
def get_esstra_so_link_paths():
    '''Fetch esstra installed path'''
    cmd = """
    CXX=$(which g++) &&
    GCC_ARCH=$($CXX -dumpmachine) &&
    GCC_MAJOR_VERSION=$($CXX -dumpversion) &&
    PREFIX='/usr/local' &&
    INSTALLDIR="${PREFIX}/lib/gcc/${GCC_ARCH}/${GCC_MAJOR_VERSION}/plugin" &&
    echo $INSTALLDIR
    """
    stdout, _, _ = run_command(cmd,
                               step_name="Fetching ESSTRA install directory",
                               fail_on_error=True)

    install_dir = Path(stdout.strip())
    installed_file = install_dir / ESSTRA_FILE_NAME
    installed_link = install_dir / ESSTRA_LINK_NAME

    if not installed_file.exists():
        pytest.fail(f"ESSTRA plugin not found: {installed_file}")

    if not installed_link.exists():
        pytest.fail(f"ESSTRA linker plugin not found: {installed_link}")

    return str(installed_file), str(installed_link)


def compile_with_plugin(esstra_paths, source_file,
                        output_file,
                        fail_on_error=False):
    '''Compile a source file with the ESSTRA plugin'''
    esstra_installed_path, esstra_installed_link = esstra_paths
    cmd = (f'gcc -fplugin={esstra_installed_path}'
           f' -Wl,-plugin={esstra_installed_link}'
           f' {source_file} -o {output_file}')

    if fail_on_error:
        return run_command(cmd,
                           step_name=f"Compiling {source_file} with plugin",
                           fail_on_error=True)
    return run_command(cmd)


def compile_without_plugin(source_file, output_file, fail_on_error=False):
    '''Compile a source file without the ESSTRA plugin'''
    cmd = f'gcc {source_file} -o {output_file}'
    if fail_on_error:
        return run_command(cmd,
                           step_name=f"Compiling {source_file} without plugin",
                           fail_on_error=True)
    return run_command(cmd)


@pytest.fixture
def compile_fresh():
    '''Returns a function to compile fresh binaries'''
    def _compile(source_file, output_file, use_plugin=False,
                 esstra_paths=None):
        if use_plugin and esstra_paths:
            return compile_with_plugin(esstra_paths, source_file,
                                       output_file, fail_on_error=True)
        else:
            return compile_without_plugin(source_file, output_file,
                                          fail_on_error=True)
    return _compile


@pytest.fixture(scope='session', autouse=True)
def test_initial_setup():
    '''Prepare a clean envionment by removing and reinstalling files'''
    # Remove built esstra.so and it's installation
    clean_cmd = ('make clean && sudo make uninstall')
    build_cmd = 'make && sudo make install'
    run_command(clean_cmd, step_name="Initial cleanup",
                fail_on_error=True)
    run_command(build_cmd, step_name="Build/install",
                fail_on_error=True)

    # Yield to allow tests to run
    yield

    # Clean the environment again after all tests have run
    run_command(clean_cmd, step_name="Final cleanup",
                fail_on_error=True)


@pytest.fixture(scope='module')
def generate_test_files(get_esstra_so_link_paths):
    '''Setup test environment - create test files and directories'''
    # Create a test directory as a Path object once
    test_dir = Path(TEST_DIR)
    test_dir.mkdir(exist_ok=True)

    # Use the Path object for file operations
    simple_c = test_dir / 'simple.c'
    helper_c = test_dir / 'helper.c'
    main_c = test_dir / 'main.c'
    nolicense_c = test_dir / 'nolicense.c'
    simple_spdx = test_dir / 'simple.spdx'
    nolicense_spdx = test_dir / 'nolicense.spdx'
    main_spdx = test_dir / 'main.spdx'
    helper_spdx = test_dir / 'helper.spdx'


    # Create a simple C file for testing
    with open(simple_c, 'w') as f:
        f.write('''
        // SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
        // SPDX-License-Identifier: MIT
        // NOTICE: THE LICENSE STATEMENT ABOVE IS JUST FOR DEMONSTRATION.

        #include <stdio.h>
        int main() {
            printf("Hello, ESSTRA!\\n");
            return 0;
        }
        ''')

    with open(main_c, 'w') as f:
        f.write('''
        // SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
        // SPDX-License-Identifier: Apache-2.0
        // NOTICE: THE LICENSE STATEMENT ABOVE IS JUST FOR DEMONSTRATION.   

        #include <stdio.h>
        extern void helper_function();
        int main() {
            printf("Main function\\n");
            helper_function();
            return 0;
        }
        ''')

    with open(helper_c, 'w') as f:
        f.write('''
        // SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
        // SPDX-License-Identifier: Apache-2.0
        // NOTICE: THE LICENSE STATEMENT ABOVE IS JUST FOR DEMONSTRATION.   

        #include <stdio.h>
        void helper_function() {
            printf("Helper function\\n");
        }
        ''')

    with open(nolicense_c, 'w') as f:
        f.write('''

        #include <stdio.h>
        int main() {
            printf("Hello, ESSTRA!\\n");
            return 0;
        }
        ''')

    with open(nolicense_spdx, 'w') as f:
        f.write('''SPDXVersion: SPDX-2.3
##-------------------------
## Package Information
##-------------------------


PackageName: nolicense.c
PackageFileName: nolicense.c
SPDXID: SPDXRef-upload97
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: true
PackageVerificationCode: da39a3ee5e6b4b0d3255bfef95601890afd80709
PackageChecksum: SHA1: be4e3a6024a982e153d46965565779faf8d7851c
PackageChecksum: SHA256: 913e9d935c3315b68f51d6fbc25f4264b7d17d3b216ace1ee7e29ebb4b63ffa1
PackageChecksum: MD5: 221e380183e638de1868c78afadd2064
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageLicenseComments: <text> licenseInfoInFile determined by Scanners:
 - nomos ("4.5.1".9197d3)
 - monk ("4.5.1".9197d3)
 - ojo ("4.5.1".9197d3) </text>
PackageLicenseInfoFromFiles: NOASSERTION
PackageCopyrightText: NOASSERTION

Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-upload97


##--------------------------
## File Information
##--------------------------

##File

FileName: nolicense.c
SPDXID: SPDXRef-item963255
FileChecksum: SHA1: be4e3a6024a982e153d46965565779faf8d7851c
FileChecksum: SHA256: 913e9d935c3315b68f51d6fbc25f4264b7d17d3b216ace1ee7e29ebb4b63ffa1
FileChecksum: MD5: 221e380183e638de1868c78afadd2064
LicenseConcluded: NOASSERTION
LicenseInfoInFile: NOASSERTION
FileCopyrightText: NOASSERTION



##-------------------------
## License Information
##-------------------------
''')

    with open(simple_spdx, 'w') as f:
        f.write('''SPDXVersion: SPDX-2.3
PackageName: simple.c
PackageFileName: simple.c
SPDXID: SPDXRef-upload91
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: true
PackageVerificationCode: 3cf26fdbf3598ff70852d561e42b485dcd46a083
PackageChecksum: SHA1: c8a4dfa5aac5fe929f61d9a9f9b0b77aff5798a6
PackageChecksum: SHA256: 60cd085631a2b5d8b78ef3610bfe4ee686622387a632ec460bf36ccd314c1594
PackageChecksum: MD5: e1b21bc57d8a9c2103526982bf27243e
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageLicenseComments: <text> licenseInfoInFile determined by Scanners:
 - nomos ("4.5.1".9197d3)
 - monk ("4.5.1".9197d3)
 - ojo ("4.5.1".9197d3) </text>
PackageLicenseInfoFromFiles: NOASSERTION
PackageCopyrightText: NOASSERTION

Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-upload91


##--------------------------
## File Information
##--------------------------

##File

FileName: simple.c
SPDXID: SPDXRef-item963244
FileChecksum: SHA1: 0129aec9d2a42cfab11ddb7047826c8251e345af
FileChecksum: SHA256: d50970670ecd19dc8d0e63ada977b526206bbffe947fa4ddb994a6212131e068
FileChecksum: MD5: 8bbb37408d7931e064b20ff8e4a28db2
LicenseConcluded: MIT

LicenseInfoInFile: MIT
FileCopyrightText: <text> Copyright 2024-2025 Sony Group Corporation SPDX-License-Identifier: MIT NOTICE: THE LICENSE STATEMENT ABOVE IS JUST FOR DEMONSTRATION. </text>



##-------------------------
## License Information
##-------------------------
''')

    with open(main_spdx, 'w') as f:
        f.write('''SPDXVersion: SPDX-2.3
##-------------------------
## Package Information
##-------------------------


PackageName: main.c
PackageFileName: main.c
SPDXID: SPDXRef-upload96
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: true
PackageVerificationCode: da39a3ee5e6b4b0d3255bfef95601890afd80709
PackageChecksum: SHA1: ef48acfddeb3093228932471eb8b4ee196a1907f
PackageChecksum: SHA256: 0332844aaeef01a61200238afaf0a12fb133b54f1101da72bd4ea0f81d76fb8a
PackageChecksum: MD5: b18dd198ca0be355f1bf595e83525c3c
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageLicenseComments: <text> licenseInfoInFile determined by Scanners:
 - nomos ("4.5.1".9197d3)
 - monk ("4.5.1".9197d3)
 - ojo ("4.5.1".9197d3) </text>
PackageLicenseInfoFromFiles: NOASSERTION
PackageCopyrightText: NOASSERTION

Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-upload96


##--------------------------
## File Information
##--------------------------

##File

FileName: main.c
SPDXID: SPDXRef-item963254
FileChecksum: SHA1: ef48acfddeb3093228932471eb8b4ee196a1907f
FileChecksum: SHA256: 0332844aaeef01a61200238afaf0a12fb133b54f1101da72bd4ea0f81d76fb8a
FileChecksum: MD5: b18dd198ca0be355f1bf595e83525c3c
LicenseConcluded: Apache-2.0

LicenseInfoInFile: Apache-2.0
FileCopyrightText: <text> Copyright 2024-2025 Sony Group Corporation SPDX-License-Identifier: Apache-2.0 NOTICE: THE LICENSE STATEMENT ABOVE IS JUST FOR DEMONSTRATION. </text>



##-------------------------
## License Information
##-------------------------
''')

    with open(helper_spdx, 'w') as f:
        f.write('''SPDXVersion: SPDX-2.3
##-------------------------
## Package Information
##-------------------------


PackageName: helper.c
PackageFileName: helper.c
SPDXID: SPDXRef-upload94
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: true
PackageVerificationCode: da39a3ee5e6b4b0d3255bfef95601890afd80709
PackageChecksum: SHA1: b5a3ec06073c82df6aff252b5856c3734006093f
PackageChecksum: SHA256: f1b09093cb3bbc138ccc10669c1d6c0c890e01b0bc5ed59164d3f464bb4b48fa
PackageChecksum: MD5: 945bf576468e850f91738a41eab455df
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageLicenseComments: <text> licenseInfoInFile determined by Scanners:
 - nomos ("4.5.1".9197d3)
 - monk ("4.5.1".9197d3)
 - ojo ("4.5.1".9197d3) </text>
PackageLicenseInfoFromFiles: NOASSERTION
PackageCopyrightText: NOASSERTION

Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-upload94


##--------------------------
## File Information
##--------------------------

##File

FileName: helper.c
SPDXID: SPDXRef-item963247
FileChecksum: SHA1: b5a3ec06073c82df6aff252b5856c3734006093f
FileChecksum: SHA256: f1b09093cb3bbc138ccc10669c1d6c0c890e01b0bc5ed59164d3f464bb4b48fa
FileChecksum: MD5: 945bf576468e850f91738a41eab455df
LicenseConcluded: Apache-2.0

LicenseInfoInFile: Apache-2.0
FileCopyrightText: <text> Copyright 2024-2025 Sony Group Corporation SPDX-License-Identifier: Apache-2.0 NOTICE: THE LICENSE STATEMENT ABOVE IS JUST FOR DEMONSTRATION. </text>



##-------------------------
## License Information
##-------------------------

''')

    # Generate binaries
    binary_with_metadata = test_dir / 'binary_with_metadata'
    binary_with_metadata_no_license = test_dir / 'binary_with_metadata_no_license'
    multi_source_binary_with_metadata = (test_dir / 'multi_source_binary_'
                                         'with_metadata')
    binary_without_plugin = test_dir / 'binary_without_plugin'

    compile_with_plugin(get_esstra_so_link_paths, str(simple_c),
                        str(binary_with_metadata), fail_on_error=True)
    compile_with_plugin(get_esstra_so_link_paths, str(nolicense_c),
                            str(binary_with_metadata_no_license), fail_on_error=True)
    multiple_source_files = f'{str(main_c)} {str(helper_c)}'
    compile_with_plugin(get_esstra_so_link_paths, multiple_source_files,
                        str(multi_source_binary_with_metadata),
                        fail_on_error=True)
    compile_without_plugin(str(simple_c), str(binary_without_plugin),
                           fail_on_error=False)

    # Yield to allow tests to run
    yield

    # Clean up the above created test directory after tests
    shutil.rmtree(test_dir)


@pytest.fixture
def setup_test_files(generate_test_files):
    '''Test fixture to create test binary files'''
    # Create test binary files with metadata
    test_dir = Path(TEST_DIR)
    binary_with_metadata = test_dir / 'binary_with_metadata'
    binary_with_metadata_no_license = test_dir / 'binary_with_metadata_no_license'
    binary_without_plugin = test_dir / 'binary_without_plugin'
    multi_source_binary_with_metadata = (test_dir / 'multi_source_binary_'
                                         'with_metadata')
    info_file = (test_dir / 'simple.spdx')
    info_file2 = (test_dir / 'main.spdx')
    info_file3 = (test_dir / 'helper.spdx')
    info_file4 = (test_dir / 'nolicense.spdx')

    # Ensure test files exist
    assert binary_with_metadata.exists(), 'Test binary with metadata not found'
    assert binary_without_plugin.exists(), ('Test binary without'
                                            ' metadata not found')
    assert multi_source_binary_with_metadata.exists(), ('Test binary with'
                                                        ' multiple sources not'
                                                        ' found')
    assert info_file.exists(), ('Test spdx not found')

    return {
        'with_metadata': str(binary_with_metadata),
        'metadata_with_nolicense': str(binary_with_metadata_no_license),
        'without_plugin': str(binary_without_plugin),
        'with_multiple_metadata': (f'{str(binary_with_metadata)} '
                                   f'{str(multi_source_binary_with_metadata)}'
                                   ),
        'multi_source_binary_with_metadata': str(
            multi_source_binary_with_metadata),
        'info_file': str(info_file),
        'info_file2': str(info_file2),
        'info_file3': str(info_file3),
        'info_file4': str(info_file4)

    }
