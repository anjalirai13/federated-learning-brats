#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

fx envoy start -n Sparsh -c "$SCRIPT_DIR/Sparsh_config.yaml" -rc cert/root_ca.crt -pk cert/Sparsh.key -oc cert/Sparsh.crt