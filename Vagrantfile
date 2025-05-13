# ENV['VAGRANT_DISABLE_STRICT_DEPENDENCY_ENFORCEMENT'] = '1'
# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.

  config.vm.box = "ubuntu/jammy64"

  config.vm.provider :virtualbox do |vb|
    vb.name = "graph-demo"
    #   # Display the VirtualBox GUI when booting the machine
    #   vb.gui = true

    # Customize the amount of memory on the VM:
    vb.memory = "16384" # 16GB
    vb.cpus = 4
  end

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access

  # Use public network with auto-bridge instead of specifying a particular interface
  config.vm.network "public_network", auto_correct: true

  # Platform RESTful API
  config.vm.network "forwarded_port",
      guest: 8080,
      host:  8080,
      auto_correct: true

  # Platform Frontend
  config.vm.network "forwarded_port",
      guest: 3000,
      host:  3000,
      auto_correct: true

  # Platform RESTful API - Debugger
  config.vm.network "forwarded_port",
      guest: 5005,
      host:  5005,
      auto_correct: true

  # Database - PostgreSQL
  config.vm.network "forwarded_port",
      guest: 5432,
      host:  5432,
      auto_correct: true

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder "..", "/home/vagrant/graph-demo", disabled: false

  # Disable the default share of the current code directory. Doing this
  # provides improved isolation between the vagrant box and your host
  # by making sure your Vagrantfile isn't accessable to the vagrant box.
  # If you use this you may want to enable additional shared subfolders as
  # shown above.
  config.vm.synced_folder ".", "/vagrant", disabled: true

  # Give execution permission to our scripts
  config.vm.provision "file", source: "./scripts", destination: "/home/vagrant/scripts"
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/bash" -c "chmod +x /home/vagrant/scripts/*/*.sh"
  SHELL
  # Install Oh My ZSh
  config.vm.provision "shell", path: "scripts/install/oh_my_zsh.sh"
  # Install Brew
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/brew.sh"
  SHELL
  # Install dos2unis
  config.vm.provision "shell", path: "scripts/install/dos2unix.sh"
  # Install NodeJS
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/nodejs.sh"
  SHELL
  # Install Docker and Docker Compose
  config.vm.provision "shell", path: "scripts/install/docker.sh"
  # Setup Complete message
  config.vm.provision "shell", inline: <<-SHELL
    echo "---> Setup Complete."
  SHELL
end
