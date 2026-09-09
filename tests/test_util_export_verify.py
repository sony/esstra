# SPDX-FileCopyrightText: Copyright 2026 ESSTRA Contributors
# SPDX-License-Identifier: MIT

import json
import subprocess
import unittest
from pathlib import Path

SAMPLE_BINARY = 'samples/output-examples/hello/hello.with_license_info'
SAMPLE_BINARY2 = 'samples/output-examples/hello2/hello2.with_license_info'
ESSTRA_UTIL = 'util/esstra'


class TestUtilNewFeatures(unittest.TestCase):

    def test_export_cyclonedx(self):
        cmd = [ESSTRA_UTIL, 'export', '--format', 'cyclonedx', SAMPLE_BINARY]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"export failed: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get('bomFormat'), 'CycloneDX')
        self.assertEqual(data.get('specVersion'), '1.5')
        self.assertTrue(len(data.get('components', [])) > 0)

    def test_export_spdx(self):
        cmd = [ESSTRA_UTIL, 'export', '--format', 'spdx', SAMPLE_BINARY]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"export failed: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get('spdxVersion'), 'SPDX-2.3')
        self.assertTrue(len(data.get('files', [])) > 0)

    def test_verify_command(self):
        cmd = [ESSTRA_UTIL, 'verify', SAMPLE_BINARY]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertIn('verified', res.stderr)

    def test_diff_command(self):
        cmd = [ESSTRA_UTIL, 'diff', SAMPLE_BINARY, SAMPLE_BINARY2]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)  # 1 indicates differences found
        self.assertIn('Summary:', res.stderr)

    def test_stats_command(self):
        cmd = [ESSTRA_UTIL, 'stats', SAMPLE_BINARY]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn('Total files:', res.stdout)
        self.assertIn('Unique licenses:', res.stdout)

    def test_check_license_pass(self):
        cmd = [ESSTRA_UTIL, 'check-license', '--deny', 'GPL-3.0', '--', SAMPLE_BINARY]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn('passed', res.stderr)

    def test_check_license_fail(self):
        cmd = [ESSTRA_UTIL, 'check-license', '--deny', 'MIT', '--', SAMPLE_BINARY]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn('DENIED', res.stderr)


if __name__ == '__main__':
    unittest.main()
