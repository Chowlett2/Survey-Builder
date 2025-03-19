#!/bin/bash

# Install python3-distutils for missing distutils issue
sudo apt-get update
sudo apt-get install python3-distutils -y

# Install any additional dependencies, if necessary
pip install -r requirements.txt
