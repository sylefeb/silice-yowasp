#!/bin/sh -ex

export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)

cd silice-src
git submodule init
git submodule update
cd ..

# sudo apt install cmake
# sudo apt install default-jdk

# Following https://github.com/YoWASP/nextpnr/blob/develop/build.sh

PYTHON=$(which ${PYTHON:-python3})

WASI_SDK=wasi-sdk-22.0
WASI_SDK_URL=https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-22/wasi-sdk-22.0-linux.tar.gz
if ! [ -d ${WASI_SDK} ]; then curl -L ${WASI_SDK_URL} | tar xzf -; fi
WASI_SDK_PATH=$(pwd)/${WASI_SDK}

WASI_TARGET="wasm32-wasi"
WASI_SYSROOT="--sysroot ${WASI_SDK_PATH}/share/wasi-sysroot"
WASI_CFLAGS="-flto"
WASI_LDFLAGS="-flto -Wl,--strip-all"

# ANTLR wants threads (for no good reason, could be fixed)
# WASI_TARGET="${WASI_TARGET}-threads"
# WASI_CFLAGS="${WASI_CFLAGS} -pthread"
# Lua needs signal
WASI_CFLAGS="${WASI_CFLAGS} -D_WASI_EMULATED_SIGNAL"
WASI_LDFLAGS="${WASI_LDFLAGS} -lwasi-emulated-signal"

cat >Toolchain-WASI.cmake <<END
cmake_minimum_required(VERSION 3.4...3.31)

set(WASI TRUE)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_VERSION 1)
set(CMAKE_SYSTEM_PROCESSOR wasm32)

set(CMAKE_C_COMPILER ${WASI_SDK_PATH}/bin/clang)
set(CMAKE_CXX_COMPILER ${WASI_SDK_PATH}/bin/clang++)
set(CMAKE_LINKER ${WASI_SDK_PATH}/bin/wasm-ld CACHE STRING "wasienv build")
set(CMAKE_AR ${WASI_SDK_PATH}/bin/ar CACHE STRING "wasienv build")
set(CMAKE_RANLIB ${WASI_SDK_PATH}/bin/ranlib CACHE STRING "wasienv build")

set(CMAKE_C_COMPILER_TARGET ${WASI_TARGET})
set(CMAKE_CXX_COMPILER_TARGET ${WASI_TARGET})
set(CMAKE_C_FLAGS "${WASI_SYSROOT} ${WASI_CFLAGS}" CACHE STRING "wasienv build")
set(CMAKE_CXX_FLAGS "${WASI_SYSROOT} ${WASI_CFLAGS}" CACHE STRING "wasienv build")
set(CMAKE_EXE_LINKER_FLAGS "${WASI_LDFLAGS}" CACHE STRING "wasienv build")
set(CMAKE_EXECUTABLE_SUFFIX,".wasm")

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

END

cmake -B silice-build -S silice-src \
  -DCMAKE_TOOLCHAIN_FILE=../Toolchain-WASI.cmake \
  -DCMAKE_INSTALL_PREFIX=$(pwd)/silice-prefix

make -C silice-build install -j8
