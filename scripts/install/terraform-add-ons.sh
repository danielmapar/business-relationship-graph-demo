#!/bin/bash

echo "---> Installing terraform-add-ons.sh"

eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# Install TF Lint
NONINTERACTIVE=1 brew install tflint
# Install TF Sec from Aquasec
NONINTERACTIVE=1 brew install trivy
# Install Terragrunt
NONINTERACTIVE=1 brew install terragrunt
# Install Terragrunt Docs
NONINTERACTIVE=1 brew install terraform-docs
# Install Terragrunt Graphviz to create Dependency Graphs
NONINTERACTIVE=1 brew install graphviz
# Install Terragrunt Autocomplete
terragrunt --install-autocomplete

echo "---> Finished installing terraform-add-ons.sh"