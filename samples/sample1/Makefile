# SPDX-License-Identifier: MIT
# Copyright 2024 Sony Group Corporation

CC := gcc
PLUGIN_INCLUDE_DIR := $(shell $(CC) -print-file-name=plugin)/include

PREFIX ?= /usr/local
ESSTRACORE ?= $(PREFIX)/share/esstra/esstracore.so

CFLAGS += -fplugin=$(ESSTRACORE) -fplugin-arg-esstracore-debug=$(DEBUG) -O2 -Wall

.PHONY: all clean

all: hello

hello: hello_main.c hello_sub.c
	$(CC) $(CFLAGS) hello_main.c hello_sub.c -o hello

clean:
	rm -f hello
