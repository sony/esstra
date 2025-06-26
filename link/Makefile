# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CC := gcc
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CFLAGS += -Wall -Wextra -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -O2
GCC_MAJOR_VERSION := $(shell $(CXX) -dumpversion)
GCC_ARCH := $(shell $(CXX) -dumpmachine)

ESSTRALINK_SRC := esstralink.c
ESSTRALINK := esstralink.so

PREFIX ?= /usr/local
INSTALLDIR := $(DESTDIR)/$(PREFIX)/lib/gcc/$(GCC_ARCH)/$(GCC_MAJOR_VERSION)/plugin
INSTALLDIR := $(subst //,/,$(INSTALLDIR))

SPECFILE := $(shell dirname `gcc -print-libgcc-file-name`)/specs

.PHONY: all clean install install-specs uninstall-specs

all: $(ESSTRACORE) $(ESSTRALINK)

$(ESSTRALINK): $(ESSTRALINK_SRC)
	$(CC) -shared $(CFLAGS) $^ -o $@

install: $(ESSTRACORE)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRALINK) $(INSTALLDIR)

clean:
	rm -f *.so

install-specs: $(INSTALLDIR)/$(ESSTRALINK)
	TEMPFILE=`mktemp` && \
	( [ -e $(SPECFILE) ] && \
	perl -pe 's@-plugin=(.*)$(ESSTRALINK)\s*@@' $(SPECFILE) || \
	gcc -dumpspecs ) > $$TEMPFILE && \
	perl -pe 's@^(\*link:\n)@\1-plugin=$(INSTALLDIR)/$(ESSTRALINK) \3@' $$TEMPFILE > $(SPECFILE) && \
	rm -f $$TEMPFILE

uninstall-specs:
	[ -e $(SPECFILE) ] && \
	( TEMPFILE=`mktemp` ; \
	perl -pe 's@-plugin=(.*)$(ESSTRALINK)\s*@@' $(SPECFILE) > $$TEMPFILE ; \
	gcc -dumpspecs | diff $$TEMPFILE - > /dev/null && \
	rm -f $(SPECFILE) || \
	cp $$TEMPFILE $(SPECFILE) ; \
	rm -f $$TEMPFILE ) || :
