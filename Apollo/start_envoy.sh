#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

fx envoy start -n Apollo -c "$SCRIPT_DIR/Apollo_config.yaml" -rc cert/root_ca.crt -pk cert/Apollo.key -oc cert/Apollo.crt