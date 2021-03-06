FROM gdcv-base:latest
MAINTAINER The Blue Alliance

# Get additional apt dependencies for development
RUN apt-get update && apt-get install -y \
  openssh-server \
  google-cloud-sdk-pubsub-emulator \
  mysql-server \
  default-jre

# Configure ssh server
RUN mkdir /var/run/sshd
RUN echo 'root:tba' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN echo "export PATH=${PATH}:/root/google-cloud-sdk/bin" >> /etc/profile
RUN echo "127.0.0.1       metadata metadata.google.internal" >> /etc/hosts
EXPOSE 22

# Expose ports for status thrift server
EXPOSE 6000

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]
