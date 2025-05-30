# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

PREFIX ?= /usr/local
INSTALLDIR := $(DESTDIR)/$(PREFIX)/bin
ESSTRAUTIL := esstra

.PHONY: all clean install

all clean:
	@echo do nothing for target: "$@"

install: $(ESSTRAUTIL).py
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRAUTIL).py $(INSTALLDIR)/$(ESSTRAUTIL)
