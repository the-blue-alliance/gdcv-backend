#! /bin/bash
set -e

echo "Current python version: "
python3 --version

echo "Downloading latest source from GitHub"
rm -f /gdcv
git clone https://github.com/the-blue-alliance/gdcv-backend.git /gdcv
cd /gdcv
git log -n 1

echo "Updating gdcv dependencies"
pip3 install -r ./requirements.txt --upgrade
find bin/ -name '*.whl' -exec pip3 install --upgrade --force-reinstall {} \;

echo "Starting gdcv..."
python3 ./gdcv/main.py
