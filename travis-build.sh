# readmanager directory
rmd=`pwd`
export READMANA_CONFIG="$rmd/config.json"
mkdir -p JSON note
export PYTHONPATH="$rmd:$PYTHONPATH"
echo "{\"dbJSON\": \"-/\", \"dbNote\": \"-/\"}" > $READMANA_CONFIG
cd test/
python test.py
cd ..
cat $READMANA_CONFIG
python readmana -c
