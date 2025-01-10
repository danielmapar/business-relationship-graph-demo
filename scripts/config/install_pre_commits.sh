#!/bin/bash

eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

install_pre_commits() {
  local org_name="$1"
  shift
  local repositories=("$@")
  for repo_name in "${repositories[@]}"; do
    if [[ -n "${repo_name}" ]]; then
      echo "Installing pre-commit and hooks for: ${repo_name}"
      pushd "./${repo_name}" || continue
      pre-commit install --install-hooks || echo "Failed installing hooks for repo: ./${repo_name}"
      popd || continue
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
)

mkdir -p /home/vagrant/sigtunnel
cd /home/vagrant/sigtunnel || return

install_pre_commits "${org_name}" "${repositories[@]}"

mkdir -p /home/vagrant/sigtunnel/community-repositories
cd /home/vagrant/sigtunnel/community-repositories || return

install_pre_commits "${org_name}" "${community_repositories[@]}"