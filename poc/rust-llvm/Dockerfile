FROM debian:trixie-slim

WORKDIR /build
# install rustc and cargo from apt
# we use rustup later, but we would like to obtain rustc version
# which can be installed from apt
RUN apt-get update && \
    apt-get install -y build-essential pkg-config libssl-dev llvm-dev clang rustc cargo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# install ESSTRA test utilities
RUN cd esstra-test-utils && \
    cargo install --path . --root /usr

# build and install ESSTRA LLVM Plugin and rustc-esstra
RUN esstra-test-utils install

# use /app as working directory, and remove build artifacts
RUN cargo clean
WORKDIR /app

# set environment variable for cargo use
ENV RUSTC="esstra-rustc"
# rustc-esstra reads ESSTRA_LLVM_PLUGIN_PATH environment variable
ENV ESSTRA_LLVM_PLUGIN_PATH="/usr/lib/libesstra_llvm_plugin.so"
