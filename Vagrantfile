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


  if ENV['VAGRANT_DEFAULT_PROVIDER'] == 'vmware_desktop'
    config.vm.box = "generic/ubuntu2204"

    config.vm.provider "vmware_desktop" do |vmware|
      vmware.vmx["displayName"] = "sigtunnel"
      # Display the VMware GUI when booting the machine
      # vmware.gui = true
      
      # Customize the amount of memory on the VM:
      vmware.memory = "16384" # 16GB
      vmware.cpus = 4
    end
  else
    config.vm.box = "ubuntu/jammy64"

    config.vm.provider :virtualbox do |vb|
      vb.name = "sigtunnel"
      #   # Display the VirtualBox GUI when booting the machine
      #   vb.gui = true

      # Enable Symbolic Links for the Virtual Machine
      # vb.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root", "1"]

      # Customize the amount of memory on the VM:
      vb.memory = "16384" # 16GB
      vb.cpus = 4
    end

    # The official vagrant-vbguest plugin was archived, it fails to run on ruby 3.2+.
    # The gem referenced here was compiled from https://github.com/dheerapat/vagrant-vbguest
    # config.vagrant.plugins = {
    #   'vagrant-vbguest' => {
    #     'sources' =>[
    #       'vagrant-vbguest-0.32.1.gem',
    #       'https://rubygems.org/', # needed but not used
    #     ],
    #   }
    # }
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

  # Platform RESTful API
  config.vm.network "forwarded_port",
      guest: 8080,
      host:  8080,
      auto_correct: true

  # Platform RESTful API - Debugger
  config.vm.network "forwarded_port",
      guest: 5005,
      host:  5005,
      auto_correct: true

  # Platform Web UI
  config.vm.network "forwarded_port",
      guest: 3000,
      host:  3000,
      auto_correct: true
  
  # material-kit-react-main
  config.vm.network "forwarded_port",
      guest: 3001,
      host:  3001,
      auto_correct: true
  
  # AWS Cognito - Local
  config.vm.network "forwarded_port",
      guest: 9229,
      host:  9229,
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
  config.vm.synced_folder "..", "/home/vagrant/sigtunnel", disabled: false

  # Disable the default share of the current code directory. Doing this
  # provides improved isolation between the vagrant box and your host
  # by making sure your Vagrantfile isn't accessable to the vagrant box.
  # If you use this you may want to enable additional shared subfolders as
  # shown above.
  config.vm.synced_folder ".", "/vagrant", disabled: true

  class GitHubEmail
      def valid_email?(email)
        # Regular expression for basic email validation
        email_regex = /\A[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\z/
        !!(email =~ email_regex) # Use =~ to check the match and convert to a boolean
      end
      def to_s
          print "-----------------------------------------------------------\n"
          print " Provide your sigtunnel email to generate SSH keys.\n"
          print "-----------------------------------------------------------\n"
          print "Email: " 
          email = STDIN.gets.chomp

          unless valid_email?(email)
            raise ArgumentError, "Invalid email address!"
          end
          return email
      end
  end

  class WaitingGithubSSHKey
      def to_s
        print "-----------------------------------------------------------\n"
        print " Visit https://github.com/settings/keys and set your new SSH Key.\n"
        print " Click ENTER when done.\n"
        print "-----------------------------------------------------------\n"
        return STDIN.gets.chomp
      end 
  end

  # Give execution permission to our scripts
  config.vm.provision "file", source: "./scripts", destination: "/home/vagrant/scripts"
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/bash" -c "chmod +x /home/vagrant/scripts/*/*.sh"
  SHELL
  # Install Oh My ZSh
  config.vm.provision "shell", path: "scripts/install/oh_my_zsh.sh"
  # Config Github SSH Keys
  config.vm.provision "shell", env: {"EMAIL" => GitHubEmail.new}, inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/config/github_ssh_key.sh $EMAIL"
  SHELL
  # Clone GitHub repositories
  config.vm.provision "shell", env: {"ENTER" => WaitingGithubSSHKey.new}, inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/config/clone_repositories.sh"
  SHELL
  # Install Brew
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/brew.sh"
  SHELL
  # Install Git Pre Commit
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/pre-commit.sh"
  SHELL
  # Install Pre Commit Hooks to existing repositories
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/config/install_pre_commits.sh"
  SHELL
  # Install dos2unis
  config.vm.provision "shell", path: "scripts/install/dos2unix.sh"
  # Install Python
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/python.sh"
  SHELL
  # Install NodeJS
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/nodejs.sh"
  SHELL
  # Install NodeJS Packages
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/nodejs-packages.sh"
  SHELL
  # Install Java JRE/JDK
  config.vm.provision "shell", path: "scripts/install/java.sh"
  # Install Quarkus CLI
  config.vm.provision "shell", path: "scripts/install/quarkus.sh"
  # Install AWS CLI and AWS Session Manager Plugin
  config.vm.provision "shell", path: "scripts/install/aws-cli.sh"
  # Install Docker and Docker Compose
  config.vm.provision "shell", path: "scripts/install/docker.sh"
  # Install Terraform
  config.vm.provision "shell", path: "scripts/install/terraform.sh"
  # Install Terraform Add Ons (TFSec, TFLint, Terragrunt)
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/install/terraform-add-ons.sh"
  SHELL
  # Install SOPS: Secrets OPerationS
  config.vm.provision "shell", path: "scripts/install/sops.sh"
  # Install Localstack
  config.vm.provision "shell", path: "scripts/install/localstack.sh"
  # Copy .aws/config and .aws/credentials
  config.vm.provision "file", source: "./scripts/config/.aws", destination: "/home/vagrant/.aws"
  # Setup AWS SSO login function
  config.vm.provision "shell", inline: <<-SHELL
    su -l vagrant -s "/bin/zsh" -c "/home/vagrant/scripts/config/aws.sh"
  SHELL
  # Setup Complete message
  config.vm.provision "shell", inline: <<-SHELL
    echo "---> Setup Complete."
  SHELL
end
