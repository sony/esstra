# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation

PREFIX ?= /usr/local
SUBDIRS := core util

.PHONY: all clean install install-specs uninstall-specs uninstall-core uninstall

all install-specs uninstall-specs uninstall-core:
	@make -C core PREFIX=$(PREFIX) $@

install clean uninstall:
	@for dir in $(SUBDIRS); do \
	  $(MAKE) -C $$dir PREFIX=$(PREFIX) $@; \
	done
