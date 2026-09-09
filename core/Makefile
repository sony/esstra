# SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
# SPDX-License-Identifier: MIT

CXX := g++
PLUGIN_INCLUDE_DIR := $(shell $(CXX) -print-file-name=plugin)
CXXFLAGS += -Wall -Wextra -I$(PLUGIN_INCLUDE_DIR)/include -fPIC -fno-rtti -O2 -std=c++17

ESSTRACORE_SRC := esstracore.cpp
ESSTRACORE := esstracore.so
ESSTRACLANG := esstraclang.so

# hash functions
THIRD_PARTY_DIR = ../third-party
WJCRYPTLIB_DIR := $(THIRD_PARTY_DIR)/WjCryptLib/lib
WJCRYPTLIB_FILES := \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Md5.c \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Sha1.c \
	$(WJCRYPTLIB_DIR)/WjCryptLib_Sha256.c
ESSTRACORE_SRC += $(WJCRYPTLIB_FILES)
CXXFLAGS += -I $(WJCRYPTLIB_DIR)

CLANG_CXXFLAGS := $(shell llvm-config --cxxflags 2>/dev/null)
CLANG_LDFLAGS := $(shell llvm-config --ldflags --libs 2>/dev/null)

.PHONY: all clean clang

all: $(ESSTRACORE)

clang: $(ESSTRACLANG)

$(WJCRYPTLIB_FILES):
	(cd $(THIRD_PARTY_DIR) && git submodule init && git submodule update)

$(ESSTRACORE): $(ESSTRACORE_SRC)
	$(CXX) -shared $(CXXFLAGS) $(CPPFLAGS) $(LDFLAGS) $^ -o $@

$(ESSTRACLANG): esstraclang.cpp
	clang++ -shared -fPIC $(CLANG_CXXFLAGS) $(CLANG_LDFLAGS) $^ -o $@

clean:
	rm -f *.so
