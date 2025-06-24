# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CXX := g++
CC := gcc
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -Wall -Wextra -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -fno-rtti -O2 -std=c++17
CFLAGS += -Wall -Wextra -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -O2
GCC_MAJOR_VERSION := $(shell $(CXX) -dumpversion)
GCC_ARCH := $(shell $(CXX) -dumpmachine)

ESSTRACORE_SRC := esstracore.cpp
ESSTRACORE := esstracore.so
ESSTRALINK_SRC := esstralink.c
ESSTRALINK := esstralink.so

# hash functions
THIRD_PARTY_DIR = ../third-party
WJCRYPTLIB_DIR := $(THIRD_PARTY_DIR)/WjCryptLib/lib
WJCRYPTLIB_FILES := \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Md5.c \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Sha1.c \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Sha256.c
ESSTRACORE_SRC += $(WJCRYPTLIB_FILES)
CXXFLAGS += -I $(WJCRYPTLIB_DIR)

PREFIX ?= /usr/local
INSTALLDIR := $(DESTDIR)/$(PREFIX)/lib/gcc/$(GCC_ARCH)/$(GCC_MAJOR_VERSION)/plugin
INSTALLDIR := $(subst //,/,$(INSTALLDIR))

SPECFILE := $(shell dirname `gcc -print-libgcc-file-name`)/specs

.PHONY: all clean install install-specs uninstall-specs

all: $(ESSTRACORE) $(ESSTRALINK)

$(WJCRYPTLIB_FILES):
	(cd $(THIRD_PARTY_DIR) && git submodule init && git submodule update)

$(ESSTRACORE): $(ESSTRACORE_SRC)
	$(CXX) -shared $(CXXFLAGS) $^ -o $@

$(ESSTRALINK): $(ESSTRALINK_SRC)
	$(CC) -shared $(CFLAGS) $^ -o $@

install: $(ESSTRACORE)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRACORE) $(ESSTRALINK) $(INSTALLDIR)

clean:
	rm -f *.so

install-specs: $(INSTALLDIR)/$(ESSTRACORE) $(INSTALLDIR)/$(ESSTRALINK)
	gcc -dumpspecs | \
	CORE=$(INSTALLDIR)/$(ESSTRACORE) LINK=$(INSTALLDIR)/$(ESSTRALINK) \
	./modify_specs.py > $(SPECFILE)

uninstall-specs: $(SPECFILE)
	rm -f $(SPECFILE)
