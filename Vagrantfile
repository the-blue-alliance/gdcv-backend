# -*- mode: ruby -*-
# vi: set ft=ruby:expandtab:tabstop=2:softtabstop=2

Vagrant.require_version "> 1.8.1"

Vagrant.configure("2") do |config|
  config.vm.define "gdcv" do |gdcv|
    # Sync the TBA code directory
    gdcv.vm.synced_folder "./", "/gdcv",
      type: "rsync",
      owner: "root",
      group: "root",
      rsync__rsync_path: "rsync",
      rsync__auto: true

    # Forward thrift server
    ports = []
    ports.push("6000:6000")
    gdcv.vm.network "forwarded_port", guest: 6000, host: 6000

    # Provision with docker
    gdcv.vm.hostname = "tba-gdcv"
    gdcv.vm.provider "docker" do |d|
      d.name = "gdcv"
      d.build_dir = "ops"
      d.dockerfile = "dev.Dockerfile"
      d.ports = ports
      d.has_ssh = true
      d.create_args = ["--add-host", "metadata.google.internal:127.0.0.1"]
    end

    # Bootstrap local mysql db
    gdcv.vm.provision "shell",
      inline: "cd /gdcv && ./scripts/setup-mysql.sh",
      privileged: false

    # Start the GDCV server
    gdcv.vm.provision "shell",
      inline: "cd /gdcv && ./scripts/bootstrap-dev-gdcv.sh",
      privileged: false,
      run: "always"
  end

  # Configure ssh into container
  config.ssh.insert_key = true
  config.ssh.username = "root"
  config.ssh.password = "tba"
  config.ssh.port = 2222
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
end
