# Kubernetes

```bash
# Create namespace (optional)
kubectl create ns apolo

# Deploy RabbitMQ
kubectl apply -f rabbitmq-service.yaml
kubectl apply -f rabbitmq-statefulset.yaml

# Deploy apolo-11
kubectl apply -f apolo-configmap.yaml
kubectl apply -f apolo-pvc.yaml
kubectl apply -f apolo-deployment.yaml

# Check status
kubectl get pods -w

# View logs
kubectl logs -l app=apolo-11

# Access RabbitMQ management
kubectl port-forward svc/rabbitmq 15672:15672
# Open http://localhost:15672 (guest/guest)
```

## Decoupled (future)

Split generator and reporter into separate deployments:

- **Generator**: publishes events to RabbitMQ, no persistent storage needed
- **Reporter**: consumes from RabbitMQ, writes results to PVC
- **RabbitMQ**: decoupling layer between them
