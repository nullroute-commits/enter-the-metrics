#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "==> Validating docker compose configuration"
docker compose config >/dev/null

echo "==> Verifying expected services are present"
mapfile -t services < <(docker compose config --services)
expected_services=(
  grafana
  prometheus
  loki
  promtail
  syslog-ng
  node-exporter
  snmp-exporter
  cadvisor
)

for expected in "${expected_services[@]}"; do
  if ! printf '%s\n' "${services[@]}" | grep -Fxq "${expected}"; then
    echo "Missing expected service: ${expected}" >&2
    exit 1
  fi
done

echo "==> Verifying referenced local config files exist"
required_files=(
  ./prometheus/config/prometheus.yml
  ./loki/config/loki-config.yml
  ./promtail/config/promtail-config.yml
  ./syslog-ng/config/syslog-ng.conf
  ./snmp-exporter/config/snmp.yml
)

for required_file in "${required_files[@]}"; do
  if [[ ! -f "${required_file}" ]]; then
    echo "Missing required file: ${required_file}" >&2
    exit 1
  fi
done

echo "All smoke tests passed."
