SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR
rm -r $SCRIPT_DIR/results
PYTHONPATH=$SCRIPT_DIR python $SCRIPT_DIR/immuneML/app/ImmuneMLApp.py $SCRIPT_DIR/yaml/spec.yaml $SCRIPT_DIR/results
