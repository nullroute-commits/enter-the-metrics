# Metrics Stack

[![CI](https://github.com/nullroute-commits/enter-the-metrics/actions/workflows/ci.yml/badge.svg)](https://github.com/nullroute-commits/enter-the-metrics/actions/workflows/ci.yml)

Installs and configures the following services to work together:

- [Grafana](https://grafana.com/) `12.4.2`
- [Prometheus](https://prometheus.io/) `v3.11.0`
- [Loki](https://grafana.com/docs/loki/latest/) `3.7.1`
- [Alloy](https://grafana.com/docs/alloy/latest/) `v1.15.0`
- [syslog-ng](https://www.syslog-ng.com/) `4.11.0`
- [snmp_exporter](https://github.com/prometheus/snmp_exporter) `v0.30.1`
- [node_exporter](https://github.com/prometheus/node_exporter) `v1.11.1`
- [cAdvisor](https://github.com/google/cadvisor) `v0.52.1`



One line explanation of each service does:

- **Grafana**: Visualising your metrics in dashboards. Sources data from many datasources (eg. Prometheus, Loki, InfluxDB)
- **Prometheus**: Collecting metric data
- **Loki**: Collecting metric data related to logs
- **Alloy**: Telemetry collector that sends logs to Loki (replaces the deprecated Promtail agent)
- **syslog-ng**: Syslog forwarder (sends logs to Alloy)
- **node_exporter**: Exposes a system's metrics (cpu, ram, network, disc etc) to Prometheus
- **snmp_exporter**: Forwards SNMP traffic from SNMP devices to Prometheus
- **cAdvisor**: Sends Docker container metrics to Prometheus

*This repo is inspired by the excellent work done in* [grafana-loki-syslog-aio](https://github.com/lux4rd0/grafana-loki-syslog-aio).

## Running

Start up the stack with:

```
docker compose pull
docker compose up -d --force-recreate
```

## Testing

Run the smoke test suite from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

This validates:
- compose configuration integrity
- expected service definitions
- presence of required local configuration files
- persistence and network wiring for core observability services
- upstream AI agent source-of-truth registration

## AI Agent Source of Truth

This repository tracks `agent.md` as its local AI skill registry and points at [`nullroute-commits/agency-agents`](https://github.com/nullroute-commits/agency-agents) as the upstream source of truth.

For GitHub Copilot, the upstream agents can be installed directly with the upstream integration flow documented in `agency-agents/integrations/github-copilot/README.md`, which copies selected `.md` agent files into `~/.github/agents/` and `~/.copilot/agents/`.

## Login

The default login is `admin`/`admin`. You can change the password to whatever you like after that.

## Preconfigured Dashboards

There are five preconfigure performance metrics Dashboards:

- Docker
- Grafana
- Loki
- Prometheus
- Node Exporter


![Performance Dashboards](docs/img/performance-dashboards.png)


The Prometheus dashboard as an example:


![Example Dashboard](docs/img/prometheus-dashboard.png)




To add custom configuration you need to update the appropriate config files as outlined below.

### Prometheus

Add your custom scrapers:


```yaml
#prometheus/config/prometheus.yml
 - job_name: 'your_job_name'
   static_configs:
   - targets: ['target_id:port'] # endpoint running /metrics
```

For example, to get metrics from a [node_exporter](https://github.com/prometheus/node_exporter) running on `192.168.1.50` add the following to `prometheus/config/prometheus.yml`:

```
- job_name: 'my-node-exporter'
  static_configs:
  - targets: ['192.168.1.50:9100']
```

See [The Prometheus Configuration Documentation](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) for more examples.

### SNMP Exporter

To register your [SNMP](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol) stats:
1. Enable SNMP functionality on your device
1. Configure your community name for your SNMP community
1. Add the community name to `snmp-exporter/config/snmp.yml`:



```yaml
#snmp-exporter/config/snmp.yml
  auth:
    community: <your community name>
```


Then add the following section to your `prometheus/config/prometheus.yml`:

```
 - job_name: 'snmp-exporter'
   static_configs:
   - targets: ['<target_ip_1>']
     labels:
       job: '<your_label_1>'
   - targets: ['<target_ip_2>']
     labels:
       job: 'your_label_2'
   metrics_path: /snmp
   params:
     module: [if_mib] # Name of snmp module. If you generated your own snmp.yml file then use the name of that module here.
   relabel_configs:
     - source_labels: [__address__]
       target_label: __param_target
     - source_labels: [__param_target]
       target_label: instance
     - target_label: __address__
       replacement: <host ip running snmp_exporter>:9116  # The SNMP exporter's real hostname:port.
```

### Links
 - [An Advanced Guide to Network Monitoring with Grafana and Prometheus](https://grafana.com/blog/2022/02/01/an-advanced-guide-to-network-monitoring-with-grafana-and-prometheus/)
- [Step-By-Step Guide to Connecting Prometheus to pfsense via Snmp](https://brendonmatheson.com/2021/02/07/step-by-step-guide-to-connecting-prometheus-to-pfsense-via-snmp.html)

## Syslogs

To forward syslogs to syslog-ng, set the following as the syslog server in the source device:
`<host ip running syslog-ng>:514` or `<host ip running syslog-ng>:601` depending on what your device supports.


## General Information

To test any service exposing metrics to Prometheus, you can query their `/metrics` endpoint.

For example to query your Grafana metrics hit: `http://<host ip running grafana>:3000/metrics`

## Service Endpoints

| Service | HTTP Ports | Other Ports |
| ------- | ---- | ---- |
| Grafana| [Web](http://localhost:3000), [Metrics](http://localhost:3000/metrics) | - |
| Prometheus| [Web](http://localhost:9090), [Metrics](http://localhost:9090/metrics) | - |
| Loki| [Web](http://localhost:3100/ready), [Metrics](http://localhost:3100/metrics) | - |
| Alloy| [Web](http://localhost:12345), [Metrics](http://localhost:12345/metrics) | tcp 1514 |
| node_exporter| [Web](http://localhost:9100/), [Metrics](http://localhost:9100/metrics) | - |
| cAdvisor| [Web](http://localhost:8080/), [Metrics](http://localhost:8080/metrics) | - |
| snmp_exporter| [Web](http://localhost:9116/), [Metrics](http://localhost:9116/metrics) | - |
| syslog-ng| - | udp 514, tcp 601 |


## CI/CD

This repository includes GitHub Actions workflows for continuous integration and deployment. All CI/CD steps run inside Docker containers — no host-level language runtimes are required.

- **CI** (`.github/workflows/ci.yml`): Runs on every push and pull request to `main`. Validates the Docker Compose configuration and runs the smoke test suite inside a `docker:cli` container.
- **Deploy** (`.github/workflows/deploy.yml`): Runs automatically on push to `main` or can be triggered manually. Uses a `docker:cli` container to sync stack files to the remote host via `rsync` over SSH and deploys with `docker compose up`.

Prometheus and Loki now store runtime data in Docker-managed named volumes so metrics and log data survive container recreation without requiring extra bind-mounted data directories.

### Deployment Setup

To enable automated deployments, configure the following secrets in your GitHub repository settings (**Settings → Secrets and variables → Actions**):

| Secret | Description |
| ------ | ----------- |
| `DEPLOY_HOST` | Hostname or IP of the target server |
| `DEPLOY_USER` | SSH username on the target server |
| `DEPLOY_SSH_KEY` | Private SSH key for authentication |
| `DEPLOY_PATH` | Absolute path on the server where the stack will be deployed |

You must also create a GitHub [environment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) called **production** in **Settings → Environments** for the deploy workflow to run against.

## Issues

If you run this stack as a non-root user (for example on Linux), you can run into permission issues such as:

> mkdir: can't create directory '/var/lib/grafana/plugins': Permission denied
> GF_PATHS_DATA='/var/lib/grafana' is not writable.

This will be evident when you run `docker ps` and see Grafana continuously restarting. You can have a look at its logs
via `docker logs grafana`


This is because Grafana [expects](https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/#migrate-to-v51-or-later) specific users and groups to control the Grafana configuration directories:

```
uid=472(grafana) gid=0(root) groups=0(root)
```

You will have to do the following on your volume mounted to `/var/lib/grafana`:

```
chown -R 472:0 ./grafana/data
```


Another way to do this, as recommended in the Grafana [documentation](https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/#migrate-to-v51-or-later), is to jump onto the started container and change ownership of the relevant directories.

Jump onto the Grafana container with:

```
docker exec -it <CONTAINER ID> bash
```

Note: The <CONTAINER_ID> can be found by running `docker ps --format="{{.ID}}\t{{.Names}}"`:

```
22c444431284    grafana
```

Then change the ownership of the relevant directories:

```
# in the container you just started:
chown -R root:root /etc/grafana && \
chmod -R a+r /etc/grafana && \
chown -R grafana:grafana /var/lib/grafana && \
chown -R grafana:grafana /usr/share/grafana
```

## Starting from a Clean Slate


If you've already run `docker compose up` on this repository, there will be some data files created that will persist your current state. If you want to start from a clean slate do the following:

1. `docker compose down -v`
1. Delete the `grafana/data/grafana.db` file (`rm grafana/data/grafana.db`)

Now you should be able to run up the stack again and start with the defaults:

```
docker compose pull
docker compose up -d --force-recreate
```
