SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
rm -r $SCRIPT_DIR/ImmuneData
immune-ml $SCRIPT_DIR/yaml/dataset.yaml $SCRIPT_DIR/ImmuneData
