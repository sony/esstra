# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CC := gcc
PLUGIN_INCLUDE_DIR := $(shell $(CC) -print-file-name=plugin)/include

PREFIX ?= /usr/local
ESSTRACORE ?= $(PREFIX)/share/esstra/esstracore.so

CFLAGS += -fplugin=$(ESSTRACORE) -fplugin-arg-esstracore-debug=$(DEBUG) -O2 -Wall

SOURCES := hello_main.c hello_sub.c
TARGET := hello2

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $^ -o $@

clean:
	rm -f $(TARGET) *.o *.bak
