# Kubernetes

## Quick Start

```bash
# Deploy everything
kubectl apply -f k8s/

# Check status
kubectl get pods -w
```

## Access

### Web Dashboard (Reporter)
```bash
kubectl port-forward svc/apolo-11 8000:8000
# Open http://localhost:8000
```

### Prometheus
```bash
kubectl port-forward svc/prometheus 9090:9090
# Open http://localhost:9090
```

### Grafana
```bash
kubectl port-forward svc/grafana 3000:3000
# Open http://localhost:3000 (admin/admin)
```

### RabbitMQ Management
```bash
kubectl port-forward svc/rabbitmq 15672:15672
# Open http://localhost:15672 (guest/guest)
```

### Logs
```bash
kubectl logs -l app=apolo-generator -f
kubectl logs -l app=apolo-reporter -f
```

### Results
```bash
kubectl exec deploy/apolo-reporter -- ls /data/results
```

## Architecture

```
                    ┌──────────────┐
                    │   Ingress    │
                    │  (nginx)     │
                    └──┬───────┬───┘
                       │       │
          ┌────────────▼──┐ ┌──▼───────────┐
          │ apolo-reporter│ │ rabbitmq     │
          │ :8000         │ │ :5672        │
          │ Web API       │ │ :15672 (UI)  │
          └──┬────────────┘ └──┬─────┬─────┘
             │                 │     │
             │          ┌──────▼──┐  │
             │          │apolo-gen│  │
             │          │         │  │
             │          └─────────┘  │
             │                       │
      ┌──────▼──────┐         ┌──────▼──────┐
      │ PVC (1Gi)   │         │ Prometheus  │
      │ /data/results│         │ :9090       │
      └─────────────┘         └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │  Grafana    │
                              │ :3000       │
                              └─────────────┘
```

## Resources

| Manifest                  | Kind          | Description                            |
| ------------------------- | ------------- | -------------------------------------- |
| `rabbitmq-service.yaml`   | Service       | Exposes RabbitMQ (5672 AMQP, 15672 UI) |
| `rabbitmq-statefulset.yaml` | StatefulSet | RabbitMQ with persistent storage       |
| `rabbitmq-secret.yaml`    | Secret        | RabbitMQ credentials (username/password) |
| `rabbitmq-network-policy.yaml` | NetworkPolicy | Restricts ingress to RabbitMQ from generator/reporter |
| `apolo-configmap.yaml`    | ConfigMap     | Mission configuration YAML             |
| `apolo-pvc.yaml`          | PVC           | 1Gi persistent volume for results      |
| `apolo-deployment.yaml`   | Deployment    | Legacy: combined apolo-11 (all mode)   |
| `generator-deployment.yaml` | Deployment  | Generator only (writes device logs)    |
| `reporter-deployment.yaml` | Deployment   | Reporter only (processes logs, serves API) |
| `apolo-service.yaml`      | Service       | Exposes reporter web dashboard (port 8000) |
| `apolo-pdb.yaml`          | PodDisruptionBudget | Limits voluntary disruptions to 0 |
| `apolo-hpa.yaml`          | HorizontalPodAutoscaler | Scales reporter 1-3 replicas |
| `prometheus-configmap.yaml` | ConfigMap   | Prometheus scrape configuration        |
| `prometheus-deployment.yaml` | Deployment | Prometheus time-series database        |
| `prometheus-service.yaml` | Service       | Exposes Prometheus UI (port 9090)      |
| `grafana-datasources.yaml` | ConfigMap    | Grafana datasource provisioning        |
| `grafana-dashboard-provider.yaml` | ConfigMap | Dashboard auto-provisioning config |
| `grafana-dashboard.yaml`  | ConfigMap     | Apollo 11 Grafana dashboard JSON       |
| `grafana-deployment.yaml` | Deployment    | Grafana visualization platform         |
| `grafana-service.yaml`    | Service       | Exposes Grafana UI (port 3000)         |
| `rabbitmq-ingress.yaml`   | Ingress       | Routes apolo.local and rabbitmq.local  |

## Decoupled Architecture

Generator and Reporter run as separate deployments communicating via RabbitMQ:

- **Generator**: creates device log files, publishes events to RabbitMQ, no API endpoint
- **Reporter**: processes log files, serves web dashboard + Prometheus `/metrics`, writes to PVC
- **RabbitMQ**: decoupling layer between them
- **Prometheus**: scrapes `/metrics` from Reporter every 15s
- **Grafana**: visualizes Prometheus data with pre-configured dashboard

### Scaling

Only the Reporter is exposed via Service and can be scaled via HPA. The Generator runs as a single instance since it writes to the same PVC.

## Docker Compose (local)

```bash
# Full stack with monitoring
docker compose up --build

# Access
# - Web Dashboard: http://localhost:8000
# - Prometheus:    http://localhost:9090
# - Grafana:       http://localhost:3000 (admin/admin)
# - RabbitMQ:      http://localhost:15672 (guest/guest)
```
