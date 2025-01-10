#!/bin/bash

echo "---> Installing aws-cli.sh"

# Install AWS CLI
sudo apt-get -y install unzip
sudo mkdir /home/vagrant/aws
cd /home/vagrant/aws || return
sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo unzip awscliv2.zip
sudo ./aws/install
sudo rm -rf /home/vagrant/aws

# Install AWS Session Manager Plugin
sudo mkdir /home/vagrant/aws-session-manager
sudo curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "/home/vagrant/aws-session-manager/session-manager-plugin.deb"
sudo dpkg -i /home/vagrant/aws-session-manager/session-manager-plugin.deb
sudo rm -rf /home/vagrant/aws-session-manager

# Set the timezone to UTC
sudo timedatectl set-ntp on

echo "---> Finished intalling aws-cli.sh"