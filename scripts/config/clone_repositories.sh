#!/bin/bash

clone_repositories() {
  local org_name="$1"
  shift
  local repositories=("$@")
  for repo_name in "${repositories[@]}"; do
    if [[ -n "${repo_name}" ]]; then
      echo "Cloning repository: ${repo_name}"
      GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git clone "${org_name}/${repo_name}.git" || echo "Failed cloning repo: ${org_name}/${repo_name}.git"
    fi
  done
}

# GitHub organization name
org_name="git@github.com:sigtunnel"

# List of GitHub repository URLs in an array
repositories=(
  "infrastructure"
  "platform-api"
  "platform-frontend"
  "github-workflows"
  "api-docs"
)

community_repositories=(
  "workspace-github-workflows"
  "workspace-integration"
  "workspace-workers"
  "workspace-worker-libraries"
)

mkdir -p /home/vagrant/sigtunnel
cd /home/vagrant/sigtunnel || return

clone_repositories "${org_name}" "${repositories[@]}"

mkdir -p /home/vagrant/sigtunnel/community-repositories
cd /home/vagrant/sigtunnel/community-repositories || return

clone_repositories "${org_name}" "${community_repositories[@]}"