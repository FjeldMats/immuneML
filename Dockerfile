FROM python:3.8

# Copy files
COPY . immuneML

RUN pip install -r immuneML/requirements.txt

RUN apt-get update && apt-get upgrade -y && apt-get install -y rsync

# get ray dashboard 
RUN pip install -U "ray[default]"