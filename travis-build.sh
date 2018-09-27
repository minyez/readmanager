#!/usr/bin/env bash

# readmanager directory
rmd=`pwd`
export READMANA_CONFIG="$rmd/config.json"
mkdir JSON note
export PATH="$rmd:$PYTHONPATH"
echo "{\n  \"dbJSON\": \"-/\",\n  \"dbNote\": \"-/\"\n}" > $READMANA_CONFIG
cd test/
python test.py
cd ..
python readmana -c
