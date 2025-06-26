# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation

PREFIX ?= /usr/local
SUBDIRS := core link util

.PHONY: all clean install install-specs uninstall-specs

all install-specs uninstall-specs:
	@make -C core PREFIX=$(PREFIX) $@
	@make -C link PREFIX=$(PREFIX) $@

install clean:
	@for dir in $(SUBDIRS); do \
	  $(MAKE) -C $$dir PREFIX=$(PREFIX) $@; \
	done
