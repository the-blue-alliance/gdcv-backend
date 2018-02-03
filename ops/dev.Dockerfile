FROM ubuntu:16.04
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
  openssh-server


# Add gcloud repository and Cloud SDK dependencies
RUN apt-get update && apt-get install -y apt-transport-https curl
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk-xenial main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
RUN apt-get update && apt-get install -y \
  google-cloud-sdk \
  google-cloud-sdk-pubsub-emulator

# Set up frc-livescore dependencies
RUN apt-get update && apt-get install -y tesseract-ocr imagemagick locales unzip
ENV LC_ALL C
COPY ./build-opencv.sh /build-opencv.sh
RUN /build-opencv.sh 3.4.0

# Install mysql server and python library
RUN apt-get install -y mysql-server libmysqlclient-dev

# Configure ssh server
RUN mkdir /var/run/sshd
RUN echo 'root:tba' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
EXPOSE 22

# Expose ports for status thrift server
EXPOSE 6000

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]
