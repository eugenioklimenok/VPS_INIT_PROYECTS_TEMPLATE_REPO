#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_DOCKER_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_DOCKER_SH_LOADED="1"

check_docker() {
  local user="$1"
  local category="DOCKER"

  if ! command_exists docker; then
    record_fail "$category" "Docker command not found"
    return
  fi

  record_ok "$category" "Docker command available"

  if docker info >/dev/null 2>&1; then
    record_ok "$category" "Docker daemon responding"
  else
    record_fail "$category" "Docker daemon not responding"
  fi

  if docker compose version >/dev/null 2>&1; then
    record_ok "$category" "Docker Compose plugin available"
  else
    record_fail "$category" "Docker Compose plugin not available"
  fi

  if id -nG "$user" 2>/dev/null | grep -qw docker; then
    record_ok "$category" "User $user belongs to docker group"
  else
    record_warn "$category" "User $user does not belong to docker group"
  fi
}
