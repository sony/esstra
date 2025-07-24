# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CC := gcc
GCC_MAJOR_VERSION := $(shell $(CXX) -dumpversion)
GCC_ARCH := $(shell $(CXX) -dumpmachine)

PREFIX ?= /usr/local
GCC_PLUGIN_DIR := $(DESTDIR)/$(PREFIX)/lib/gcc/$(GCC_ARCH)/$(GCC_MAJOR_VERSION)/plugin
GCC_PLUGIN_DIR := $(subst //,/,$(GCC_PLUGIN_DIR))
ESSTRACORE ?= $(GCC_PLUGIN_DIR)/esstracore.so
ESSTRALINK ?= $(GCC_PLUGIN_DIR)/esstralink.so

ifdef DEBUG
DEBUGFLAG := -fplugin-arg-esstracore-debug=$(DEBUG)
endif

CFLAGS += -O2 -Wall
CFLAGS += -fplugin=$(ESSTRACORE) $(DEBUGFLAG)
CFLAGS += -Wl,-plugin=$(ESSTRALINK)

.PHONY: all clean

all: hello

hello: hello.c
	$(CC) $(CFLAGS) $< -o hello

clean:
	rm -f hello *.bak
