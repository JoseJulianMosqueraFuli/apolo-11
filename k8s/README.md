# Kubernetes

## Quick Start

### Credentials (required — no defaults)

The manifests read RabbitMQ/Grafana credentials from Secrets. Create them with strong
values before deploying (do not commit real passwords):

```bash
kubectl create secret generic rabbitmq-auth \
  --from-literal=username=apolo \
  --from-literal=password="$(openssl rand -base64 18)" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic grafana-admin \
  --from-literal=admin-user=apolo_admin \
  --from-literal=admin-password="$(openssl rand -base64 18)" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Deploy everything

```bash
kubectl apply -f k8s/
kubectl get pods -w
```

### Local cluster (Docker Desktop / kind)

On a local cluster you use a locally-built image instead of pulling from a registry.
This exact flow is verified on Docker Desktop (kubeadm, dockerd runtime):

```bash
# 1. Build the image (Docker Desktop's cluster shares its image store)
docker build -t apolo-11:latest .

# 2. Create the RabbitMQ secret (see "Credentials" above), then deploy the core stack
kubectl apply -f k8s/rabbitmq-secret.yaml \
               -f k8s/rabbitmq-service.yaml \
               -f k8s/rabbitmq-statefulset.yaml \
               -f k8s/apolo-configmap.yaml \
               -f k8s/apolo-pvc.yaml \
               -f k8s/apolo-deployment.yaml

# 3. Local only: use the locally-built image (manifests default to imagePullPolicy: Always for prod)
kubectl patch deployment apolo-11 --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/imagePullPolicy","value":"IfNotPresent"}]'

# 4. Verify (expect "Conectado a RabbitMQ" and the app running)
kubectl get pods
kubectl logs deploy/apolo-11 --tail=-1 | grep -i rabbitmq
```

> On **kind** (containerd, not dockerd), load the image into the cluster instead of step 3:
> `kind load docker-image apolo-11:latest`

### Tear down

```bash
kubectl delete -f k8s/
kubectl delete pvc --all
```

### Verify the security fix in-cluster

```bash
# Default guest account must be rejected
kubectl exec rabbitmq-0 -- rabbitmqctl authenticate_user guest guest        # -> invalid credentials
# Secret user must authenticate
kubectl exec rabbitmq-0 -- sh -c 'rabbitmqctl authenticate_user "$RABBITMQ_DEFAULT_USER" "$RABBITMQ_DEFAULT_PASS"'  # -> Success
# Secret is injected into the app pod
kubectl exec deploy/apolo-11 -- sh -c 'echo "$RABBITMQ_DEFAULT_USER @ $RABBITMQ_HOST"'
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
# Open http://localhost:3000 (credentials from the grafana-admin Secret)
```

### RabbitMQ Management

```bash
kubectl port-forward svc/rabbitmq 15672:15672
# Open http://localhost:15672 (credentials from the rabbitmq-auth Secret)
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

| Manifest                          | Kind                    | Description                                           |
| --------------------------------- | ----------------------- | ----------------------------------------------------- |
| `rabbitmq-service.yaml`           | Service                 | Exposes RabbitMQ (5672 AMQP, 15672 UI)                |
| `rabbitmq-statefulset.yaml`       | StatefulSet             | RabbitMQ with persistent storage                      |
| `rabbitmq-secret.yaml`            | Secret                  | RabbitMQ credentials (username/password)              |
| `rabbitmq-network-policy.yaml`    | NetworkPolicy           | Restricts ingress to RabbitMQ from generator/reporter |
| `apolo-configmap.yaml`            | ConfigMap               | Mission configuration YAML                            |
| `apolo-pvc.yaml`                  | PVC                     | 1Gi persistent volume for results                     |
| `apolo-deployment.yaml`           | Deployment              | Legacy: combined apolo-11 (all mode)                  |
| `generator-deployment.yaml`       | Deployment              | Generator only (writes device logs)                   |
| `reporter-deployment.yaml`        | Deployment              | Reporter only (processes logs, serves API)            |
| `apolo-service.yaml`              | Service                 | Exposes reporter web dashboard (port 8000)            |
| `apolo-pdb.yaml`                  | PodDisruptionBudget     | Limits voluntary disruptions to 0                     |
| `apolo-hpa.yaml`                  | HorizontalPodAutoscaler | Scales reporter 1-3 replicas                          |
| `prometheus-configmap.yaml`       | ConfigMap               | Prometheus scrape configuration                       |
| `prometheus-deployment.yaml`      | Deployment              | Prometheus time-series database                       |
| `prometheus-service.yaml`         | Service                 | Exposes Prometheus UI (port 9090)                     |
| `grafana-datasources.yaml`        | ConfigMap               | Grafana datasource provisioning                       |
| `grafana-dashboard-provider.yaml` | ConfigMap               | Dashboard auto-provisioning config                    |
| `grafana-dashboard.yaml`          | ConfigMap               | Apollo 11 Grafana dashboard JSON                      |
| `grafana-deployment.yaml`         | Deployment              | Grafana visualization platform                        |
| `grafana-service.yaml`            | Service                 | Exposes Grafana UI (port 3000)                        |
| `rabbitmq-ingress.yaml`           | Ingress                 | Routes apolo.local and rabbitmq.local                 |

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
# Set credentials first (no defaults)
cp .env.example .env   # then edit the values

# Full stack with monitoring
docker compose up --build

# Access
# - Web Dashboard: http://localhost:8000
# - Prometheus:    http://localhost:9090
# - Grafana:       http://localhost:3000 (credentials from .env)
# - RabbitMQ:      http://localhost:15672 (credentials from .env)
```
