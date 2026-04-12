#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_SETUP_PACKAGES_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_SETUP_PACKAGES_SH_LOADED="1"

install_base_packages() {
  log_step "Installing base packages"

  export DEBIAN_FRONTEND=noninteractive

  apt-get update || abort "apt-get update failed"

  apt-get install -y \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    unzip \
    tar \
    gzip \
    rsync \
    nano \
    ufw \
    openssh-server \
    apt-transport-https \
    software-properties-common \
    || abort "Failed installing base packages"

  log_ok "Base packages installed"
}
