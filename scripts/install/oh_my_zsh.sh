#!/bin/bash

echo "---> Installing oh_my_zsh.sh"

sudo apt -y install zsh
sudo chsh -s /bin/zsh vagrant
su -l vagrant -s "/bin/sh" -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

su -l vagrant -s "/bin/sh" -c "
echo '
# global aliases
alias -g docker-compose=\"DOCKER_CLIENT_TIMEOUT=120 COMPOSE_HTTP_TIMEOUT=120 sudo docker-compose\"
alias -g docker=\"sudo docker\"
' >> ~/.zshrc
"

echo "---> Finished installing oh_my_zsh.sh"