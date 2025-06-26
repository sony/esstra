# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CXX := g++
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -Wall -Wextra -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -fno-rtti -O2 -std=c++17
GCC_MAJOR_VERSION := $(shell $(CXX) -dumpversion)
GCC_ARCH := $(shell $(CXX) -dumpmachine)

ESSTRACORE_SRC := esstracore.cpp
ESSTRACORE := esstracore.so

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

all: $(ESSTRACORE)

$(WJCRYPTLIB_FILES):
	(cd $(THIRD_PARTY_DIR) && git submodule init && git submodule update)

$(ESSTRACORE): $(ESSTRACORE_SRC)
	$(CXX) -shared $(CXXFLAGS) $^ -o $@

install: $(ESSTRACORE)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRACORE) $(INSTALLDIR)

clean:
	rm -f *.so

install-specs: $(INSTALLDIR)/$(ESSTRACORE)
	TMPFILE=`mktemp` ; \
	([ -e $(SPECFILE) ] && \
	perl -pe 's@-fplugin=(.*)$(ESSTRACORE)\s*@@' $(SPECFILE) || gcc -dumpspecs) > $$TMPFILE ; \
	perl -pe 's@^(\*cc1:\n)@\1-fplugin=$(INSTALLDIR)/$(ESSTRACORE) \3@' $$TMPFILE > $(SPECFILE) ; \
	rm -f $$TMPFILE

uninstall-specs:
	[ -e $(SPECFILE) ] && \
	( TEMPFILE=`mktemp` ; \
	perl -pe 's@-fplugin=(.*)$(ESSTRACORE)\s*@@' $(SPECFILE) > $$TEMPFILE ; \
	gcc -dumpspecs | diff $$TEMPFILE - > /dev/null && \
	rm -f $(SPECFILE) || \
	cp $$TEMPFILE $(SPECFILE) ; \
	rm -f $$TEMPFILE ) || :
