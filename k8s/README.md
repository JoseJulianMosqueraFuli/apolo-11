# Kubernetes

## Quick Start

```bash
# Deploy everything
kubectl apply -f k8s/

# Check status
kubectl get pods -w
```

## Access

### Web Dashboard
```bash
kubectl port-forward svc/apolo-11 8000:8000
# Open http://localhost:8000
```

### RabbitMQ Management
```bash
kubectl port-forward svc/rabbitmq 15672:15672
# Open http://localhost:15672 (guest/guest)
```

### Logs
```bash
kubectl logs -l app=apolo-11 -f
```

### Results
```bash
kubectl exec deploy/apolo-11 -- ls /data/results
```

## Ingress (optional)

If you have an ingress controller (e.g., ingress-nginx), add to `/etc/hosts`:

```
127.0.0.1 apolo.local rabbitmq.local
```

Then access:
- http://apolo.local — Web dashboard
- http://rabbitmq.local — RabbitMQ management
- http://apolo.local/docs — Swagger API docs

## Resources

| Manifest                  | Kind          | Description                            |
| ------------------------- | ------------- | -------------------------------------- |
| `rabbitmq-service.yaml`   | Service       | Exposes RabbitMQ (5672 AMQP, 15672 UI) |
| `rabbitmq-statefulset.yaml` | StatefulSet | RabbitMQ with persistent storage       |
| `apolo-configmap.yaml`    | ConfigMap     | Mission configuration YAML             |
| `apolo-pvc.yaml`          | PVC           | 1Gi persistent volume for results      |
| `apolo-deployment.yaml`   | Deployment    | apolo-11 with TUI + Web dashboard      |
| `apolo-service.yaml`      | Service       | Exposes web dashboard (port 8000)      |
| `rabbitmq-ingress.yaml`   | Ingress       | Routes apolo.local and rabbitmq.local  |

## Architecture

```
        ┌──────────────┐
        │   Ingress    │
        │  (nginx)     │
        └──┬───────┬───┘
           │       │
    ┌──────▼──┐ ┌──▼───────────┐
    │ apolo-11 │ │ rabbitmq     │
    │ :8000    │ │ :5672        │
    │ TUI+Web  │ │ :15672 (UI)  │
    └──────┬───┘ └─────────────┘
           │
    ┌──────▼──────┐
    │ PVC (1Gi)   │
    │ /data/results│
    └─────────────┘
```

## Decoupled (future)

Split generator and reporter into separate deployments:

- **Generator**: publishes events to RabbitMQ, no persistent storage needed
- **Reporter**: consumes from RabbitMQ, writes results to PVC
- **RabbitMQ**: decoupling layer between them
