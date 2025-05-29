#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

import os
import sys

CORE_PATH = os.path.realpath(os.environ["CORE"])
LINK_PATH = os.path.realpath(os.environ["LINK"])

spec_name = None
for line in sys.stdin:
    line = line.rstrip('\n')
    if line:
        if line[0] == '*':
            spec_name = line.rstrip()
        if spec_name == '*cc1:':
            print(spec_name)
            print(f'-fplugin={CORE_PATH} ', end='')
            spec_name = None
            continue
        if spec_name == '*link:':
            print(spec_name)
            print(f'-plugin={LINK_PATH} ', end='')
            spec_name = None
            continue
    print(line)
