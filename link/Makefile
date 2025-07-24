# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CC := gcc
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CFLAGS += -Wall -Wextra -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -O2

ESSTRALINK_SRC := esstralink.c
ESSTRALINK := esstralink.so

.PHONY: all clean

all: $(ESSTRALINK)

$(ESSTRALINK): $(ESSTRALINK_SRC)
	$(CC) -shared $(CFLAGS) $^ -o $@

clean:
	rm -f *.so
