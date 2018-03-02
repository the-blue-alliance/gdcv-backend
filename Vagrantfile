# -*- mode: ruby -*-
# vi: set ft=ruby:expandtab:tabstop=2:softtabstop=2

Vagrant.require_version "> 1.8.1"

# Install vagrant plugin
# From: https://github.com/hashicorp/vagrant/issues/1874#issuecomment-165904024
# @param: plugin type: Array[String] desc: The desired plugin to install
def ensure_plugins(plugins)
  logger = Vagrant::UI::Colored.new
  result = false
  plugins.each do |p|
    pm = Vagrant::Plugin::Manager.new(
      Vagrant::Plugin::Manager.user_plugins_file
    )
    plugin_hash = pm.installed_plugins
    next if plugin_hash.has_key?(p)
    result = true
    logger.warn("Installing plugin #{p}")
    if not system "vagrant plugin install #{p}"
      logger.error("Unable to install plugin #{p}")
      exit -1
    end
  end
  if result
    logger.warn('Re-run vagrant up now that plugins are installed')
    exit
  end
end

# Make sure we have all the proper plugins installed
ensure_plugins(["vagrant-triggers"])

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

  # Before we start the dev container, make sure we have the latest base image
  # pulled from Google
  config.trigger.before [:up] do
    info "Pulling latest base container from Google"
    run "gcloud docker -- pull gcr.io/tbatv-prod-hrd/gdcv-base:latest"
  end
end
