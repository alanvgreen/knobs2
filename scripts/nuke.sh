#!/bin/bash

set -e

THIS_DIR="$(dirname "$0")"
WORKING_ROOT="$(git -C ${THIS_DIR} rev-parse --show-toplevel)"

(
    cd ${THIS_DIR}
    mpremote connect /dev/serial0 cp ./nuke.py :nuke.py
    mpremote connect /dev/serial0 exec "import nuke;nuke.nuke()"
)
