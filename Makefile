# SPDX-License-Identifier: MIT
# Copyright 2024 Sony Group Corporation

PREFIX ?= /usr/local
SUBDIRS := core util

.PHONY: all clean install install-specs uninstall-specs

all install-specs uninstall-specs:
	@make -C core PREFIX=$(PREFIX) $@

install clean:
	@for dir in $(SUBDIRS); do \
	  $(MAKE) -C $$dir PREFIX=$(PREFIX) $@; \
	done
