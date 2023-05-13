# ImmumeML with Ray

This repo is a fork from the [ImmuneML project](https://github.com/uio-bmi/immuneML) and modified to utilize mulitple machines in parallell using [Ray](https://github.com/ray-project/ray).

The goal of this project is to show that Ray can be used utilized on machine learning projects like ImmuneML with little to no changes to the original code.

# Running immuneML + Ray on a local machine

## Installation
I reccomend using a virtual environment for running this project to avoid any dependency issues. to create an virtual environment from file run the following command:
```bash
conda env create --file env.yml
```
This will create a new environment called `ray` with all the dependencies needed to run this project.

## Generate Data for training
To run any of the scripts in this project you need to generate data first. I have made a script that makes this easy. To generate data run the following command:
```bash
./generate_data.sh
```
This will makea new folder called `/immuneData` and use the the `dataset.yaml` specification file to to generate a dataset will be used for training.

## Setup an the Ray cluster
To run this project you need to setup a Ray cluster. This can be done by running the following command:
```bash
ray start --head 
```
This will create the head node of the cluster, and will be the machine that also hosts the dashboard. The defualt port for the dashboard is `8265`. To access the dashboard go to `localhost:8265` in your browser.

## Run the project

To run the project you need to run the following command:
```bash
./run_spec.sh
```

This will use the `spec.yaml` file inside `/yaml` to run the project. The `spec.yaml` file has been configured to use the the data from `/immuneData` and will run the project on the local machine. once the project is done running you will find the results in `/results`.

### Notes on the results generating process
There is a known issue that Generating HTML reports will not always fully complete and will raise an Exception inside `HPHTMLBuilder.py` sometimes.