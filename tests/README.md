# Functional tests for ESSTRA Core and ESSTRA Utility

## Installation

Before running these tests, you need to install pytest. This can be done in the following way:

```sh
$ pip install pytest
```

## Usage

> [!IMPORTANT]
> This test suite requires root privileges. You can either:
>
> - Provide root privileges when prompted during execution of `pytest -v tests`
> - Or start a root shell first: `sudo -s` and then run the tests


### Run test for all test cases

Run the tests from the top directory as below:

```sh
esstra$ pytest -v tests
```

#### Example Output

```sh
esstra$ pytest -v tests/
============================================================================================================ test session starts =============================================================================================================
platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.4.0 -- /home/ubuntu/test/bin/python3
cachedir: .pytest_cache
rootdir: /home/ubuntu/esstra/tests
configfile: pytest.ini
plugins: requests-mock-1.12.1
collected 46 items                                                                                                                                                                                                                           

tests/test_core.py::test_core_plugin_installed [sudo] password for ubuntu: 
PASSED                                                                                                                                                                                  [  2%]
tests/test_core.py::test_core_section_exists_with_plugin PASSED                                                                                                                                                                        [  4%]
tests/test_core.py::test_core_section_not_exists_without_plugin PASSED                                                                                                                                                                 [  6%]
tests/test_core.py::test_esstra_section_content PASSED                                                                                                                                                                                 [  8%]
tests/test_core.py::test_multi_file_compilation PASSED                                                                                                                                                                                 [ 10%]
tests/test_core.py::test_multi_source_files PASSED                                                                                                                                                                                     [ 13%]
tests/test_core.py::test_with_spec_installed PASSED                                                                                                                                                                                    [ 15%]
tests/test_core.py::test_with_spec_uninstalled PASSED                                                                                                                                                                                  [ 17%]
tests/test_util_rm.py::test_remove_basic PASSED                                                                                                                                                                                        [ 19%]
tests/test_util_rm.py::test_remove_with_verbose PASSED                                                                                                                                                                                 [ 21%]
tests/test_util_rm.py::test_remove_with_backup PASSED                                                                                                                                                                                  [ 23%]
tests/test_util_rm.py::test_remove_with_backup_suffix PASSED                                                                                                                                                                           [ 26%]
tests/test_util_rm.py::test_remove_with_backup_overwrite PASSED                                                                                                                                                                        [ 28%]
tests/test_util_rm.py::test_remove_with_multiple_binaries PASSED                                                                                                                                                                       [ 30%]
tests/test_util_rm.py::test_remove_non_existent_file PASSED                                                                                                                                                                            [ 32%]
tests/test_util_rm.py::test_remove_without_metadata PASSED                                                                                                                                                                             [ 34%]
tests/test_util_rm.py::test_remove_with_ignore_errors PASSED                                                                                                                                                                           [ 36%]
tests/test_util_show.py::test_show_basic PASSED                                                                                                                                                                                        [ 39%]
tests/test_util_show.py::test_show_raw SKIPPED (Feature not implemented yet)                                                                                                                                                           [ 41%]
tests/test_util_show.py::test_show_multiple_binaries PASSED                                                                                                                                                                            [ 43%]
tests/test_util_show.py::test_show_non_existent_file PASSED                                                                                                                                                                            [ 45%]
tests/test_util_show.py::test_show_silent_option PASSED                                                                                                                                                                                [ 47%]
tests/test_util_show.py::test_show_show_error_option PASSED                                                                                                                                                                            [ 50%]
tests/test_util_show.py::test_show_without_metadata PASSED                                                                                                                                                                             [ 52%]
tests/test_util_show.py::test_show_debug PASSED                                                                                                                                                                                        [ 54%]
tests/test_util_show.py::test_show_ignore_error PASSED                                                                                                                                                                                 [ 56%]
tests/test_util_shrink.py::test_shrink_basic PASSED                                                                                                                                                                                    [ 58%]
tests/test_util_shrink.py::test_shrink_with_verbose PASSED                                                                                                                                                                             [ 60%]
tests/test_util_shrink.py::test_shrink_with_backup PASSED                                                                                                                                                                              [ 63%]
tests/test_util_shrink.py::test_shrink_with_backup_suffix PASSED                                                                                                                                                                       [ 65%]
tests/test_util_shrink.py::test_shrink_with_backup_overwrite PASSED                                                                                                                                                                    [ 67%]
tests/test_util_shrink.py::test_shrink_with_multiple_binaries PASSED                                                                                                                                                                   [ 69%]
tests/test_util_shrink.py::test_shrink_non_existent_file PASSED                                                                                                                                                                        [ 71%]
tests/test_util_shrink.py::test_shrink_without_metadata PASSED                                                                                                                                                                         [ 73%]
tests/test_util_shrink.py::test_shrink_with_ignore_errors PASSED                                                                                                                                                                       [ 76%]
tests/test_util_update.py::test_update_basic PASSED                                                                                                                                                                                    [ 78%]
tests/test_util_update.py::test_update_multiple_binaries PASSED                                                                                                                                                                        [ 80%]
tests/test_util_update.py::test_update_invalid_info_file PASSED                                                                                                                                                                        [ 82%]
tests/test_util_update.py::test_update_non_existent_binary PASSED                                                                                                                                                                      [ 84%]
tests/test_util_update.py::test_update_silent_option PASSED                                                                                                                                                                            [ 86%]
tests/test_util_update.py::test_update_show_error_option PASSED                                                                                                                                                                        [ 89%]
tests/test_util_update.py::test_update_without_metadata PASSED                                                                                                                                                                         [ 91%]
tests/test_util_update.py::test_update_ignore_errors PASSED                                                                                                                                                                            [ 93%]
tests/test_util_update.py::test_update_backup PASSED                                                                                                                                                                                   [ 95%]
tests/test_util_update.py::test_shrink_with_backup_suffix PASSED                                                                                                                                                                       [ 97%]
tests/test_util_update.py::test_update_with_backup_overwrite PASSED                                                                                                                                                                    [100%]

======================================================================================================= 45 passed, 1 skipped in 11.67s =======================================================================================================

```

### Run individual tests

Tests for a single subcommand can be executed in two ways:

1. Using markers defined in pytest.ini: `pytest -v -m show_test tests/`
1. Using the test file directly: `pytest -v tests/test_util_show.py`


## Test Cases

### Esstra Core

The following test cases are included for Esstra Core:

1. Plugin installation verification
1. Esstra section exists in binary compiled with plugin
1. Esstra section absent in binary compiled without plugin
1. Esstra section content validation (SHA1 checksum and source filename)
1. Multi-file compilation with plugin
1. Multiple source filenames present in esstra section
1. Compilation with spec file installed (implicit plugin usage)
1. Compilation with spec file uninstalled (no plugin)

### Esstra Utility

#### Esstra show

The following test cases are included for `esstra show`:

1. Basic show command output verification
1. Raw license data display (skipped - feature not implemented yet)
1. Multiple binary file metadata display
1. Handling of non-existent files
1. Silent option suppressing error messages
1. Show-error option overriding silent mode
1. Display of binary without esstra metadata
1. Debug mode testing
1. Error handling with ignore-errors option

#### Esstra shrink

The following test cases are included for `esstra shrink`:

1. Basic shrink command output verification
1. Shrink with verbose option
1. Shrink with backup file creation
1. Shrink with custom backup suffix
1. Shrink with backup overwrite option
1. Shrink with multiple binaries
1. Handling of non-existent files
1. Shrink on binary without esstra metadata
1. Error handling with ignore-errors option


#### Esstra update

The following test cases are included for `esstra update`:

1. Basic update command with info file
1. Update with multiple binaries and info files
1. Handling of invalid/non-existent info file
1. Handling of non-existent binary
1. Silent option suppressing error messages
1. Show-error option overriding silent mode
1. Update on binary without esstra metadata
1. Error handling with ignore-errors option
1. Update with backup file creation
1. Update with custom backup suffix
1. Update with backup overwrite option


#### Esstra rm

The following test cases are included for `esstra rm`:

1. Basic remove command verification
1. Remove with verbose option
1. Remove with backup file creation
1. Remove with custom backup suffix
1. Remove with backup overwrite option
1. Remove with multiple binaries
1. Handling of non-existent files
1. Remove on binary without esstra metadata
1. Error handling with ignore-errors option

