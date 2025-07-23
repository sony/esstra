# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation

PREFIX ?= /usr/local

ESSTRACORE := esstracore.so
ESSTRALINK := esstralink.so
ESSTRAUTIL := esstra.py

INSTALLDIR_BIN := $(DESTDIR)/$(PREFIX)/bin
INSTALLDIR_BIN := $(subst //,/,$(INSTALLDIR_BIN))

GCC_MAJOR_VERSION := $(shell $(CXX) -dumpversion)
GCC_ARCH := $(shell $(CXX) -dumpmachine)
INSTALLDIR_PLUGIN := $(DESTDIR)/$(PREFIX)/lib/gcc/$(GCC_ARCH)/$(GCC_MAJOR_VERSION)/plugin
INSTALLDIR_PLUGIN := $(subst //,/,$(INSTALLDIR_PLUGIN))

SPECFILE := $(shell dirname `gcc -print-libgcc-file-name`)/specs

.PHONY: all clean install install-specs uninstall-specs

all clean:
	$(MAKE) -C core PREFIX=$(PREFIX) $@
	$(MAKE) -C link PREFIX=$(PREFIX) $@

install: core/$(ESSTRACORE) link/$(ESSTRALINK) util/$(ESSTRAUTIL)
	install -m 0755 -D -t $(INSTALLDIR_PLUGIN) core/$(ESSTRACORE) link/$(ESSTRALINK)
	install -m 0755 -D -t $(INSTALLDIR_BIN) util/$(ESSTRAUTIL)

install-specs: $(ESSTRACORE) $(ESSTRALINK)
	@gcc -dumpspecs | \
	perl -pe 's@^(\*cc1:\n)@\1-fplugin=$(INSTALLDIR_PLUGIN)/$(ESSTRACORE) \3@' | \
	perl -pe 's@^(\*link:\n)@\1-plugin=$(INSTALLDIR_PLUGIN)/$(ESSTRALINK) \3@' > $(SPECFILE)
	@echo "* spec file installed successfully: '$(SPECFILE)'" ; \

uninstall: uninstall-specs
	rm -f $(INSTALLDIR_PLUGIN)/$(ESSTRACORE) $(INSTALLDIR_PLUGIN)/$(ESSTRALINK)
	rm -f $(INSTALLDIR_BIN)/$(ESSTRAUTIL)

uninstall-specs:
	@[ -e $(SPECFILE) ] && \
	(rm -f $(SPECFILE) && echo "* spec file removed successfully: '$(SPECFILE)'") || \
	(echo "* not found: '$(SPECFILE)'")
