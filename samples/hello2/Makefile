# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CC := gcc
GCC_MAJOR_VERSION := $(shell $(CC) -dumpversion)
GCC_ARCH := $(shell $(CC) -dumpmachine)

PREFIX ?= /usr/local
GCC_PLUGIN_DIR := $(DESTDIR)/$(PREFIX)/lib/gcc/$(GCC_ARCH)/$(GCC_MAJOR_VERSION)/plugin
GCC_PLUGIN_DIR := $(subst //,/,$(GCC_PLUGIN_DIR))
ESSTRACORE ?= $(GCC_PLUGIN_DIR)/esstracore.so

ifdef DEBUG
DEBUGFLAG := -fplugin-arg-esstracore-debug=$(DEBUG)
endif

CFLAGS += -fplugin=$(ESSTRACORE) $(DEBUGFLAG) -O2 -Wall

SOURCES := hello_main.c hello_sub.c
TARGET := hello2

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $^ -o $@

clean:
	rm -f $(TARGET) *.o *.bak
