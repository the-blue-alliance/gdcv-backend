#! /bin/bash

# Script to interact with the thrift server running in the dev container
# This is basically a wrapper around a properly formed pex command
# https://github.com/pantsbuild/pex

# First, make sure we're running from TBA root
# Do this by hackily asserting that .travis.yml exists here
if [ ! -f ./Vagrantfile ]; then
    echo "Run this script from the repo root"
    exit -1
fi

echo "Starting tests..."
pex thriftpy requests -- ./local-client/gdcv-thrift-client.py
