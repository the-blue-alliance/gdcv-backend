#! /bin/bash

# A script that pulls the opencv source and builds it with all the
# options our project requres.
# Takes the opencv version (e.g. 3.4.0) as the only argument
set -e

src_path=/opencv
opencv_version=$1
echo "Installing opencv $opencv_version"

# Install dependencies
apt-get install -y build-essential
apt-get install -y cmake git pkg-config libavcodec-dev libavformat-dev libswscale-dev ffmpeg
apt-get install -y python3-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

# Set up directories for building
mkdir -p $src_path
cd $src_path

# Get main opencv source
wget -q https://github.com/opencv/opencv/archive/$opencv_version.zip
unzip -q $opencv_version.zip
rm $opencv_version.zip
mkdir opencv-$opencv_version/build

# Get sources for contrib modules
wget -q https://github.com/opencv/opencv_contrib/archive/$opencv_version.zip
unzip -q $opencv_version.zip
rm $opencv_version.zip

# Build opencv
cd opencv-$opencv_version/build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_EXTRA_MODULES_PATH=$src_path/opencv_contrib-$opencv_version/modules \
      -D WITH_FFMPEG=1 \
      -D PYTHON_EXECUTABLE=$(which python3) \
      -D WITH_TBB=ON \
      -D BUILD_NEW_PYTHON_SUPPORT=ON \
      -D WITH_V4L=ON  \
      -D WITH_OPENGL=ON ..
make -j8
make install
sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
ldconfig
echo "opencv install complete"
