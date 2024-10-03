# SPDX-License-Identifier: MIT
# Copyright 2024 Sony Group Corporation

CXX := g++
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -fno-rtti -O2

ESSTRACORE_SOURCE := esstracore.cpp
ESSTRACORE := $(ESSTRACORE_SOURCE:.cpp=.so)

PREFIX ?= /usr/local
INSTALLDIR := $(PREFIX)/share/esstra

.PHONY: all clean install

all: $(ESSTRACORE)

$(ESSTRACORE):
	$(CXX) -shared $(CXXFLAGS) $(ESSTRACORE_SOURCE) -o $@

install: $(ESSTRACORE)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRACORE) $(INSTALLDIR)

clean:
	rm -f *.so
