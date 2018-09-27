#!/usr/bin/env bash

# readmanager directory
rmd=`pwd`
export READMANA_CONFIG="$rmd/config.json"
mkdir JSON note
export PATH="$rmd:$PATH"
cat "{\n  \"dbJSON\": \"$rmd/JSON\",\n  \"dbNote\": \"$rmd/note\n}\"" > $READMANA_CONFIG
cd test/
python3 test.py
cd ..
python3 readmana -c
