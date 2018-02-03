#! /bin/bash

# Script to interact with the thrift server running in the dev container
# This is basically a wrapper around a properly formed pex command
# https://github.com/pantsbuild/pex

# First, make sure we're running from TBA root
# Do this by hackily asserting that .travis.yml exists here
if [ ! -f ./.travis.yml ]; then
    echo "Run this script from the TBA repo root"
    exit -1
fi

pex thriftpy requests -- ./gdcv/local-client/gdcv-thrift-client.py
