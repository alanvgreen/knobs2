#!/bin/bash

set -e

THIS_DIR="$(dirname "$0")"
WORKING_ROOT="$(git -C ${THIS_DIR} rev-parse --show-toplevel)"
MP_DIR="${WORKING_ROOT}/micropython"
RP2_DIR="${MP_DIR}/ports/rp2"


if [[ "$1" == "clean" ]]
then
    make -C "${MP_DIR}/mpy-cross"
    make -C "${RP2_DIR}" clean
    make -C "${RP2_DIR}" submodules
fi
make -C "${RP2_DIR}" FROZEN_MANIFEST="${WORKING_ROOT}/manifest.py"
