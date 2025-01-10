#!/bin/bash

# Function to switch AWS SSO profiles
echo '
function findStringInFile() {
    # Check if the correct number of arguments is provided
    if [ $# -ne 2 ]; then
        echo "Usage: findStringInFile <config_file> <search_string>"
        return 1
    fi

    # Store the arguments in variables
    local config_file="$1"
    local search_string="$2"

    # Check if the config file exists
    if [ ! -f "$config_file" ]; then
        echo "Error: Config file '$config_file' does not exist."
        return 1
    fi

    # Search for the string in the config file and print the matching lines
    grep "$search_string" "$config_file"
}

# Function to switch AWS SSO profiles
function awsuse() {
  if [ -z "$1" ]; then
    echo "No environment supplied"
  else
    if findStringInFile ~/.aws/config $1; then
      export AWS_PROFILE=${1}
      echo "AWS command line environment set to [${1}]"
      aws sso logout
      aws sso login
    else
      echo "AWS profile [${1}] not found."
      echo "Please choose from an existing profile:"
      grep "\[profile" ~/.aws/config
      echo "Or create a new one."
    fi
  fi
}
' >> ~/.zshrc