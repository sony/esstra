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
    simple_spdx = test_dir / 'simple.spdx'
    main_spdx = test_dir / 'main.spdx'
    helper_spdx = test_dir / 'helper.spdx'


    # Create a simple C file for testing
    with open(simple_c, 'w') as f:
        f.write('''
        #include <stdio.h>
        int main() {
            printf("Hello, ESSTRA!\\n");
            return 0;
        }
        ''')

    with open(main_c, 'w') as f:
        f.write('''
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
        #include <stdio.h>
        void helper_function() {
            printf("Helper function\\n");
        }
        ''')

    with open(simple_spdx, 'w') as f:
        f.write('''SPDXVersion: SPDX-2.3
##-------------------------
## Package Information
##-------------------------


PackageName: simple.c
PackageFileName: simple.c
SPDXID: SPDXRef-upload10
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: true
PackageVerificationCode: da39a3ee5e6b4b0d3255bfef95601890afd80709
PackageChecksum: SHA1: fd625aa98c9c6bb46eec471756aa6695370739fe
PackageChecksum: SHA256: f17f59bfb808758246e8d493ef1161fa5938b1dbe6c969b1d03e1edc2cdafa7a
PackageChecksum: MD5: 356a486f81ceae00bea28b8696f3c3d9
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageLicenseComments: <text> licenseInfoInFile determined by Scanners:
 - nomos ("4.5.1".9197d3)
 - monk ("4.5.1".9197d3)
 - ojo ("4.5.1".9197d3) </text>
PackageLicenseInfoFromFiles: NOASSERTION
PackageCopyrightText: NOASSERTION

Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-upload10

##--------------------------
## File Information
##--------------------------

##File

FileName: simple.c
SPDXID: SPDXRef-item231002
FileChecksum: SHA1: fd625aa98c9c6bb46eec471756aa6695370739fe
FileChecksum: SHA256: f17f59bfb808758246e8d493ef1161fa5938b1dbe6c969b1d03e1edc2cdafa7a
FileChecksum: MD5: 356a486f81ceae00bea28b8696f3c3d9
LicenseConcluded: NOASSERTION
LicenseInfoInFile: NOASSERTION
FileCopyrightText: NOASSERTION



##-------------------------
## License Information
##-------------------------
''')

    with open(main_spdx, 'w') as f:
        f.write('''SPDXVersion: SPDX-2.3
DataLicense: CC0-1.0

##-------------------------
## Document Information
##-------------------------

DocumentNamespace: http://ea44739a46f5/repo/SPDX2TV_main.c.spdx
DocumentName: /srv/fossology/repository/report
SPDXID: SPDXRef-DOCUMENT

##-------------------------
## Creation Information
##-------------------------

Creator: Tool: fossology-4.5.1
Creator: Person: fossy (y)
CreatorComment: <text>
This document was created using license information and a generator from Fossology.
</text>
Created: 2026-06-16T15:42:36Z
LicenseListVersion: 3.22

##-------------------------
## Package Information
##-------------------------


PackageName: main.c
PackageFileName: main.c
SPDXID: SPDXRef-upload11
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: true
PackageVerificationCode: da39a3ee5e6b4b0d3255bfef95601890afd80709
PackageChecksum: SHA1: ee7b1dce06e15b37613711b52efa454d00d1c710
PackageChecksum: SHA256: 37d7c75e9792a6515a3eab6aba2b4d2d7c455916169c474a569cdb8824503e3a
PackageChecksum: MD5: 5e7569d1aaa15eb06d0883337db76f41
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageLicenseComments: <text> licenseInfoInFile determined by Scanners:
 - nomos ("4.5.1".9197d3)
 - monk ("4.5.1".9197d3)
 - ojo ("4.5.1".9197d3) </text>
PackageLicenseInfoFromFiles: NOASSERTION
PackageCopyrightText: NOASSERTION

Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-upload11


##--------------------------
## File Information
##--------------------------

##File

FileName: main.c
SPDXID: SPDXRef-item231003
FileChecksum: SHA1: ee7b1dce06e15b37613711b52efa454d00d1c710
FileChecksum: SHA256: 37d7c75e9792a6515a3eab6aba2b4d2d7c455916169c474a569cdb8824503e3a
FileChecksum: MD5: 5e7569d1aaa15eb06d0883337db76f41
LicenseConcluded: NOASSERTION
LicenseInfoInFile: NOASSERTION
FileCopyrightText: NOASSERTION



##-------------------------
## License Information
##-------------------------
''')

    with open(helper_spdx, 'w') as f:
        f.write('''SPDXVersion: SPDX-2.3
DataLicense: CC0-1.0

##-------------------------
## Document Information
##-------------------------

DocumentNamespace: http://ea44739a46f5/repo/SPDX2TV_helper.c.spdx
DocumentName: /srv/fossology/repository/report
SPDXID: SPDXRef-DOCUMENT

##-------------------------
## Creation Information
##-------------------------

Creator: Tool: fossology-4.5.1
Creator: Person: fossy (y)
CreatorComment: <text>
This document was created using license information and a generator from Fossology.
</text>
Created: 2026-06-16T15:42:56Z
LicenseListVersion: 3.22

##-------------------------
## Package Information
##-------------------------


PackageName: helper.c
PackageFileName: helper.c
SPDXID: SPDXRef-upload12
PackageDownloadLocation: NOASSERTION
FilesAnalyzed: true
PackageVerificationCode: da39a3ee5e6b4b0d3255bfef95601890afd80709
PackageChecksum: SHA1: e75bf3d67a4e6cf6deabed831f8b1d38d6b287e2
PackageChecksum: SHA256: fffba1968c8704f690a214cf92ac8dd0b8afecd73b565edf6ec3e07763146cc9
PackageChecksum: MD5: 6d6469b093e630173717b1cb2a90bdf7
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
PackageLicenseComments: <text> licenseInfoInFile determined by Scanners:
 - nomos ("4.5.1".9197d3)
 - monk ("4.5.1".9197d3)
 - ojo ("4.5.1".9197d3) </text>
PackageLicenseInfoFromFiles: NOASSERTION
PackageCopyrightText: NOASSERTION

Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-upload12


##--------------------------
## File Information
##--------------------------

##File

FileName: helper.c
SPDXID: SPDXRef-item231004
FileChecksum: SHA1: e75bf3d67a4e6cf6deabed831f8b1d38d6b287e2
FileChecksum: SHA256: fffba1968c8704f690a214cf92ac8dd0b8afecd73b565edf6ec3e07763146cc9
FileChecksum: MD5: 6d6469b093e630173717b1cb2a90bdf7
LicenseConcluded: NOASSERTION
LicenseInfoInFile: NOASSERTION
FileCopyrightText: NOASSERTION



##-------------------------
## License Information
##-------------------------

''')

    # Generate binaries
    binary_with_metadata = test_dir / 'binary_with_metadata'
    multi_source_binary_with_metadata = (test_dir / 'multi_source_binary_'
                                         'with_metadata')
    binary_without_plugin = test_dir / 'binary_without_plugin'

    compile_with_plugin(get_esstra_so_link_paths, str(simple_c),
                        str(binary_with_metadata), fail_on_error=True)
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
    binary_without_plugin = test_dir / 'binary_without_plugin'
    multi_source_binary_with_metadata = (test_dir / 'multi_source_binary_'
                                         'with_metadata')
    info_file = (test_dir / 'simple.spdx')
    info_file2 = (test_dir / 'main.spdx')
    info_file3 = (test_dir / 'helper.spdx')

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
        'without_plugin': str(binary_without_plugin),
        'with_multiple_metadata': (f'{str(binary_with_metadata)} '
                                   f'{str(multi_source_binary_with_metadata)}'
                                   ),
        'multi_source_binary_with_metadata': str(
            multi_source_binary_with_metadata),
        'info_file': str(info_file),
        'info_file2': str(info_file2),
        'info_file3': str(info_file3)

    }
