#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_SETUP_DOCKER_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_SETUP_DOCKER_SH_LOADED="1"

install_docker_prereqs() {
  apt-get install -y ca-certificates curl gnupg || abort "Failed installing Docker prerequisites"
  install -m 0755 -d /etc/apt/keyrings || abort "Failed to create /etc/apt/keyrings"

  if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc \
      || abort "Failed downloading Docker GPG key"
    chmod a+r /etc/apt/keyrings/docker.asc || abort "Failed setting permissions on Docker GPG key"
    log_ok "Docker GPG key installed"
  else
    log_ok "Docker GPG key already present"
  fi
}

add_docker_repo() {
  local arch codename repo_line source_file
  arch="$(dpkg --print-architecture)"
  codename="$(. /etc/os-release && echo "$VERSION_CODENAME")"
  source_file="/etc/apt/sources.list.d/docker.list"
  repo_line="deb [arch=${arch} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${codename} stable"

  if [[ -f "$source_file" ]] && grep -Fqx "$repo_line" "$source_file"; then
    log_ok "Docker repository already configured"
  else
    printf '%s\n' "$repo_line" > "$source_file" || abort "Failed writing Docker repository"
    log_ok "Docker repository configured"
  fi
}

install_docker_stack() {
  local user="$1"

  log_step "Installing Docker stack"

  install_docker_prereqs
  add_docker_repo

  apt-get update || abort "apt-get update failed after adding Docker repo"

  apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    || abort "Docker installation failed"

  systemctl enable --now docker || abort "Failed to enable/start Docker service"

  docker version >/dev/null 2>&1 || abort "Docker command not working after installation"
  docker compose version >/dev/null 2>&1 || abort "Docker Compose plugin not working after installation"

  if id -nG "$user" 2>/dev/null | grep -qw docker; then
    log_ok "User $user already belongs to docker group"
  else
    usermod -aG docker "$user" || abort "Failed to add $user to docker group"
    log_ok "User $user added to docker group"
  fi

  log_ok "Docker stack installed and ready"
}
