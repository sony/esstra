# ESSTRA Util's show Testing tool

## Installation

Before using these tests, you need to install pytest. This can be done in the following way:

```sh
$ pip install pytest
```

## Usage

> [!IMPORTANT]
> This tool requires root privileges. You can either:
>
> - Provide root privileges when prompted during execution of `pytest -v tests`
> - Or start a root shell first: `sudo -s` and then run the tests

### Run the tests

Run the tests from the top directory as below:

```sh
esstra$ pytest -v tests
```

## Example Output

```sh
esstra$ pytest -v tests
=============================================================================================== test session starts ===============================================================================================
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.10.0, pluggy-0.13.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/ubuntu/tmp/esstra/tests, configfile: pytest.ini
plugins: requests-mock-1.12.1
collected 8 items                                                                                                                                                                                                 

tests/test_util_show.py::test_show_basic [sudo] password for ubuntu: 
PASSED                                                                                                                                                             [ 12%]
tests/test_util_show.py::test_show_raw PASSED                                                                                                                                                               [ 25%]
tests/test_util_show.py::test_show_no_comments PASSED                                                                                                                                                       [ 37%]
tests/test_util_show.py::test_show_multiple_binaries PASSED                                                                                                                                                 [ 50%]
tests/test_util_show.py::test_show_non_existent_file PASSED                                                                                                                                                 [ 62%]
tests/test_util_show.py::test_show_without_metadata PASSED                                                                                                                                                  [ 75%]
tests/test_util_show.py::test_show_debug PASSED                                                                                                                                                             [ 87%]
tests/test_util_show.py::test_show_ignore_error PASSED
================================================================================================ 8 passed in 3.74s ================================================================================================
```

## Test Cases

The tool includes the following test cases:

- Basic license information display
- Raw license data display
- Display without comments
- Multiple binary testing
- Handling of non-existent files
- Display without metadata
- Debug mode testing
- Error handling with ignore option

> [!NOTE]
> The tests would be modified later on to include tests for esstra's core and esstra util's other features
