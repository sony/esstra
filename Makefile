# SPDX-License-Identifier: MIT
# Copyright 2024 Sony Group Corporation

PREFIX ?= /usr/local
SUBDIRS := core util

.PHONY: all clean install

all install clean:
	@for dir in $(SUBDIRS); do \
	  $(MAKE) -C $$dir PREFIX=$(PREFIX) $@; \
	done
