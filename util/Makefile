# SPDX-License-Identifier: MIT
# Copyright 2024 Sony Group Corporation

PREFIX ?= /usr/local
INSTALLDIR := $(PREFIX)/bin
ESSTRAUTIL := esstra.py

.PHONY: all clean install

all clean:
	@echo do nothing for target: "$@"

install: $(ESSTRAUTIL)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRAUTIL) $(INSTALLDIR)
