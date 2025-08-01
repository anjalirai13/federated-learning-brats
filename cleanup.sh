#!/usr/bin/bash
set -x

find . -name "__pycache__" -type d -exec rm -rf {} +
rm -rf workspace/generated_workspace
rm -rf metaflow_data/*
rm -rf Apollo/metaflow_data
rm -rf Sparsh/metaflow_data