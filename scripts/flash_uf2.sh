#!/bin/bash

set -e

THIS_DIR="$(dirname "$0")"
WORKING_ROOT="$(git -C ${THIS_DIR} rev-parse --show-toplevel)"
MP_DIR="${WORKING_ROOT}/micropython"
RP2_DIR="${MP_DIR}/ports/rp2"

cp "${RP2_DIR}/build-RPI_PICO/firmware.uf2" /media/alang/RPI-RP2
