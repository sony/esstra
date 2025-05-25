# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CXX := g++
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -Wall -Wextra
CXXFLAGS += -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -fno-rtti -O2 -std=c++14

ESSTRACORE_SOURCES := esstracore.cpp
ESSTRACORE := $(ESSTRACORE_SOURCES:.cpp=.so)

# hash functions
THIRD_PARTY_DIR = ../third-party
WJCRYPTLIB_DIR := $(THIRD_PARTY_DIR)/WjCryptLib/lib
WJCRYPTLIB_FILES := \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Md5.c \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Sha1.c \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Sha256.c
ESSTRACORE_SOURCES += $(WJCRYPTLIB_FILES)
CXXFLAGS += -I $(WJCRYPTLIB_DIR)

PREFIX ?= /usr/local
INSTALLDIR := $(DESTDIR)/$(PREFIX)/share/esstra

SPECFILE := $(shell dirname `gcc -print-libgcc-file-name`)/specs

.PHONY: all clean install install-specs uninstall-specs

all: $(ESSTRACORE)

$(WJCRYPTLIB_FILES):
	(cd $(THIRD_PARTY_DIR) && git submodule init && git submodule update)

$(ESSTRACORE): $(ESSTRACORE_SOURCES)
	$(CXX) -shared $(CXXFLAGS) $^ -o $@

install: $(ESSTRACORE)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRACORE) $(INSTALLDIR)

clean:
	rm -f *.so

install-specs: $(INSTALLDIR)/$(ESSTRACORE)
	gcc -dumpspecs | \
	sed -E "N;s|\*cc1:\n(.+)$$|*cc1:\n\1 %{!fplugin:-fplugin=$(INSTALLDIR)/$(ESSTRACORE)}|" \
	> $(SPECFILE)

uninstall-specs: $(SPECFILE)
	rm -f $(SPECFILE)
