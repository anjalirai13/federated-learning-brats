#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

fx director start -c "$SCRIPT_DIR/director_config.yaml" -rc cert/root_ca.crt -pk cert/localhost.key -oc cert/localhost.crt

