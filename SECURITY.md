# Security — Pending Improvements

Below are identified security gaps and planned improvements for the Kubernetes deployment. Each item includes priority, effort, and impact.

## Critical

### 1. Run container as non-root user

**Problem:** `python:3.12-slim` runs as `root` by default. If the container is compromised, an attacker has full host access via container escape.

**Fix in `Dockerfile`:**
```dockerfile
RUN addgroup --system apolo && adduser --system --ingroup apolo apolo
USER apolo
```

**Fix in `k8s/apolo-deployment.yaml`:**
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  runAsGroup: 1001
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  readOnlyRootFilesystem: true
```

### 2. RabbitMQ credentials in Secret

**Problem:** Username and password are hardcoded in `rabbitmq-statefulset.yaml`.

**Fix:** Create a Secret and reference it:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: rabbitmq-auth
type: Opaque
stringData:
  username: guest
  password: guest  # TODO: rotate before production
```

Then in the StatefulSet:
```yaml
env:
  - name: RABBITMQ_DEFAULT_USER
    valueFrom:
      secretKeyRef:
        name: rabbitmq-auth
        key: username
  - name: RABBITMQ_DEFAULT_PASS
    valueFrom:
      secretKeyRef:
        name: rabbitmq-auth
        key: password
```

### 3. Resource limits

**Problem:** No CPU/memory limits set. A runaway process can starve the node.

**Fix in `k8s/apolo-deployment.yaml` and `rabbitmq-statefulset.yaml`:**
```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

## High

### 4. Liveness and readiness probes

**Problem:** If the application hangs, Kubernetes has no way to detect it and restart the pod.

**Fix in `k8s/apolo-deployment.yaml`:**
```yaml
livenessProbe:
  httpGet:
    path: /api/stats
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /api/stats
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 5. Container image vulnerability scanning

**Problem:** No automated scanning for CVEs in the container image.

**Proposed CI integration:**
```yaml
- name: Scan image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: apolo-11:latest
    format: table
    exit-code: 1
    severity: CRITICAL,HIGH
```

## Medium

### 6. Network policies

**Problem:** Any pod in the namespace can communicate with any other pod. No network isolation between apolo-11 and RabbitMQ.

**Fix:** Create a NetworkPolicy that only allows apolo-11 to talk to RabbitMQ on port 5672.

### 7. PodDisruptionBudget

**Problem:** Without a PDB, voluntary disruptions (node drain, etc.) can take down all replicas.

### 8. Seccomp / AppArmor profile

**Problem:** No seccomp profile restricts system calls available to the container.

## Low

### 9. ImagePullPolicy

`IfNotPresent` is acceptable for local development but should be `Always` in production to ensure fresh images.

### 10. HorizontalPodAutoscaler

No autoscaling configured. Could add HPA based on CPU/memory metrics for the web dashboard.

## Priority Matrix

| Item | Priority | Effort | Impact |
|------|----------|--------|--------|
| Non-root user | Critical | Low | High |
| RabbitMQ Secret | Critical | Low | High |
| Resource limits | Critical | Low | High |
| Probes | High | Low | High |
| Image scanning | High | Medium | Medium |
| NetworkPolicy | Medium | Medium | Medium |
| PodDisruptionBudget | Medium | Low | Medium |
| Seccomp | Medium | Medium | Medium |
| ImagePullPolicy | Low | Low | Low |
| HPA | Low | Medium | Low |

## Timeline

1. **Short term** (next sprint): Items 1–4 (critical + probes)
2. **Medium term** (next month): Items 5–6 (image scanning + network policy)
3. **Long term**: Items 7–10
