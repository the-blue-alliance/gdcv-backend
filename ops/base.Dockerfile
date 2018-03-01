FROM ubuntu:18.04
MAINTAINER The Blue Alliance

# Set debconf to run non-interactively
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Get apt dependencies
RUN apt-get update && apt-get install -y \
  git \
  sudo \
  python3 \
  python3-dev \
  python3-pip \
  build-essential \
  checkinstall \
  libssl-dev \
  tmux \
  vim \
  wget \
  build-essential \
  libsm6 \
  cmake git pkg-config libavcodec-dev libavformat-dev libswscale-dev ffmpeg \
  python3-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev

# Add gcloud repository and Cloud SDK dependencies
RUN apt-get update && apt-get install -y apt-transport-https curl
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk-xenial main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
RUN apt-get update && apt-get install -y \
  google-cloud-sdk

# Set up frc-livescore dependencies
RUN apt-get update && apt-get install -y tesseract-ocr imagemagick locales unzip
#ENV LC_ALL C
#COPY ./build-opencv.sh /build-opencv.sh
#RUN /build-opencv.sh 3.4.0

# Install mysql python library
RUN apt-get install -y libmysqlclient-dev mysql-client

CMD ["/bin/bash"]
