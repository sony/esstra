# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

PREFIX ?= /usr/local
INSTALLDIR := $(DESTDIR)/$(PREFIX)/bin
INSTALLDIR := $(subst //,/,$(INSTALLDIR))
ESSTRAUTIL := esstra.py

.PHONY: all clean install uninstall

all clean:
	@echo do nothing for target: "$@"

install: $(ESSTRAUTIL)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRAUTIL) $(INSTALLDIR)

uninstall:
	rm -f $(INSTALLDIR)/$(ESSTRAUTIL)
