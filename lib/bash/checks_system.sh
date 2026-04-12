#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_SYSTEM_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_SYSTEM_SH_LOADED="1"

check_system() {
  local category="SYSTEM"
  local disk_free_pct ram_mb swap_mb ip4

  disk_free_pct="$(df -P / 2>/dev/null | awk 'NR==2 {gsub("%","",$5); print 100-$5}' || true)"
  if [[ -n "$disk_free_pct" ]]; then
    if (( disk_free_pct > 20 )); then
      record_ok "$category" "Disk free on /: ${disk_free_pct}%"
    elif (( disk_free_pct >= 10 )); then
      record_warn "$category" "Disk free on / is low: ${disk_free_pct}%"
    else
      record_fail "$category" "Disk free on / critically low: ${disk_free_pct}%"
    fi
  else
    record_warn "$category" "Could not determine disk free percentage"
  fi

  ram_mb="$(free -m 2>/dev/null | awk '/^Mem:/ {print $2}' || true)"
  if [[ -n "$ram_mb" ]]; then
    if (( ram_mb < 1024 )); then
      record_warn "$category" "Low RAM detected: ${ram_mb} MB"
    else
      record_info "$category" "RAM total: ${ram_mb} MB"
    fi
  else
    record_warn "$category" "Could not determine total RAM"
  fi

  swap_mb="$(free -m 2>/dev/null | awk '/^Swap:/ {print $2}' || true)"
  if [[ -n "$swap_mb" ]]; then
    if (( swap_mb == 0 )); then
      record_warn "$category" "No swap configured"
    else
      record_info "$category" "Swap total: ${swap_mb} MB"
    fi
  else
    record_warn "$category" "Could not determine swap size"
  fi

  record_info "$category" "Timezone: $(safe_timezone)"
  record_info "$category" "Hostname: $(safe_hostname)"

  ip4="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
  if [[ -n "$ip4" ]]; then
    record_info "$category" "Primary IP: $ip4"
  fi
}
