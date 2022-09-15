SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR
rm -r $SCRIPT_DIR/results2
immune-ml $SCRIPT_DIR/yaml/spec.yaml $SCRIPT_DIR/results2
