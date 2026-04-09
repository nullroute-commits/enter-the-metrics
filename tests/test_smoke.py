import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
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


if __name__ == "__main__":
    unittest.main()
