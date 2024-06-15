
#!/bin/bash

set -e

THIS_DIR="$(dirname "$0")"
WORKING_ROOT="$(git -C ${THIS_DIR} rev-parse --show-toplevel)"

${THIS_DIR}/nuke.sh
(
    cd ${WORKING_ROOT}/picofs
    for f in $(find -L . -type d ! -name '.')
    do
        mpremote connect /dev/serial0 mkdir $f
    done
    for f in $(find -L . -name '*.py')
    do
        #mpremote connect /dev/serial0 mkdir $(dirname $f) >/dev/null || true
        mpremote connect /dev/serial0 cp $f :$f
    done
)
