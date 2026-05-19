import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCKER_COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
PROMETHEUS_CONFIG_FILE = REPO_ROOT / "prometheus/config/prometheus.yml"
LOKI_CONFIG_FILE = REPO_ROOT / "loki/config/loki-config.yml"
AGENT_SOT_FILE = REPO_ROOT / "agent.md"
EXPECTED_SERVICES = {
    "grafana",
    "prometheus",
    "loki",
    "alloy",
    "syslog-ng",
    "node-exporter",
    "snmp-exporter",
    "cadvisor",
}
REQUIRED_FILES = [
    "prometheus/config/prometheus.yml",
    "loki/config/loki-config.yml",
    "alloy/config/config.alloy",
    "syslog-ng/config/syslog-ng.conf",
    "snmp-exporter/config/snmp.yml",
]


class ComposeSmokeTests(unittest.TestCase):
    def read_service_block(self, service_name: str) -> str:
        compose_text = DOCKER_COMPOSE_FILE.read_text()
        pattern = rf"(?ms)^  {re.escape(service_name)}:\n(?P<body>(?:^(?:    ).*\n?)*)"
        match = re.search(pattern, compose_text)
        self.assertIsNotNone(match, f"Service block not found: {service_name}")
        return match.group("body")

    def run_compose(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["docker", "compose", *args],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_compose_configuration_is_valid(self) -> None:
        self.run_compose("config")

    def test_expected_services_are_defined(self) -> None:
        output = self.run_compose("config", "--services").stdout
        stripped_lines = [line.strip() for line in output.splitlines()]
        services = {line for line in stripped_lines if line}
        self.assertTrue(
            EXPECTED_SERVICES.issubset(services),
            f"Missing services: {sorted(EXPECTED_SERVICES - services)}",
        )

    def test_required_local_config_files_exist(self) -> None:
        missing_files = [
            file_path
            for file_path in REQUIRED_FILES
            if not (REPO_ROOT / file_path).is_file()
        ]
        self.assertEqual([], missing_files, f"Missing files: {missing_files}")

    def test_observability_data_is_persisted(self) -> None:
        compose_text = DOCKER_COMPOSE_FILE.read_text()
        self.assertIn("prometheus-data:/prometheus", compose_text)
        self.assertIn("loki-data:/loki", compose_text)
        self.assertIn("prometheus-data: {}", compose_text)
        self.assertIn("loki-data: {}", compose_text)
        self.assertIn("path_prefix: /loki", LOKI_CONFIG_FILE.read_text())

    def test_snmp_exporter_shares_the_stack_network(self) -> None:
        snmp_exporter_block = self.read_service_block("snmp-exporter")
        self.assertIn("networks:\n      loki: null", snmp_exporter_block)

    def test_prometheus_scrapes_core_services(self) -> None:
        prometheus_config = PROMETHEUS_CONFIG_FILE.read_text()
        self.assertIn("- job_name: 'cadvisor'", prometheus_config)
        self.assertIn("- job_name: 'snmp-exporter'", prometheus_config)
        self.assertIn("targets: ['snmp-exporter:9116']", prometheus_config)

    def test_agent_source_of_truth_exists(self) -> None:
        self.assertTrue(AGENT_SOT_FILE.is_file())
        agent_sot = AGENT_SOT_FILE.read_text()
        self.assertIn("nullroute-commits/agency-agents", agent_sot)
        self.assertIn("source of truth", agent_sot.lower())


if __name__ == "__main__":
    unittest.main()
