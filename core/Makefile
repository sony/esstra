# SPDX-License-Identifier: MIT
# Copyright 2024 Sony Group Corporation

CXX := g++
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -fno-rtti -O2 -std=c++14

ESSTRACORE_SOURCES := esstracore.cpp
ESSTRACORE := $(ESSTRACORE_SOURCES:.cpp=.so)

# hash functions
ESSTRACORE_SOURCES += lib/WjCryptLib_Md5.c lib/WjCryptLib_Sha1.c lib/WjCryptLib_Sha256.c

PREFIX ?= /usr/local
INSTALLDIR := $(PREFIX)/share/esstra

.PHONY: all clean install

all: $(ESSTRACORE)

$(ESSTRACORE): $(ESSTRACORE_SOURCES)
	$(CXX) -shared $(CXXFLAGS) $^ -o $@

install: $(ESSTRACORE)
	install -m 755 -d $(INSTALLDIR)
	install -m 755 $(ESSTRACORE) $(INSTALLDIR)

clean:
	rm -f *.so
