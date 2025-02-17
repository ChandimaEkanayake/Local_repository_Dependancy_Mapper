#!/bin/bash

# Create conda environment
conda init
conda create -n codelink_mapper python=3.9 -y
conda activate codelink_mapper

# Install dependencies
pip install -r requirements.txt
