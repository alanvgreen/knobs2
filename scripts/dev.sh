#!/bin/bash

set -e

THIS_DIR="$(dirname "$0")"
WORKING_ROOT="$(git -C ${THIS_DIR} rev-parse --show-toplevel)"

(
    cd ${WORKING_ROOT}/picofs
    mpremote mount --unsafe-links . "$@"
)
