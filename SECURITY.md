# Security — Improvements

All identified security improvements for the Kubernetes deployment have been implemented.

## Critical

### 1. Run container as non-root user ✅

**Dockerfile:** system user/group `apolo` with `USER apolo` before ENTRYPOINT.

**Kubernetes:** `runAsNonRoot: true`, `runAsUser: 1001`, `runAsGroup: 1001`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, `readOnlyRootFilesystem: true`.

### 2. RabbitMQ credentials in Secret ✅

Credentials managed via `k8s/rabbitmq-secret.yaml` and referenced via `secretKeyRef` in both Deployment and StatefulSet.

### 2b. No default credentials ✅

The insecure `guest/guest` (RabbitMQ) and `admin/admin` (Grafana) fallbacks have been removed:

- **Docker Compose** requires `RABBITMQ_USER`, `RABBITMQ_PASS`, `GRAFANA_ADMIN_USER`, and `GRAFANA_ADMIN_PASSWORD` via `${VAR:?...}`. It fails fast if they are not provided (see `.env.example`; real values live in a gitignored `.env`).
- **Kubernetes** sources Grafana admin credentials from a `grafana-admin` Secret (`k8s/grafana-secret.yaml`) instead of hardcoded env values.
- The `rabbitmq-secret.yaml` and `grafana-secret.yaml` files are templates with placeholder passwords and instructions to generate real ones out-of-band.

### 2c. Enforced RabbitMQ authentication ✅

`apolo_11/src/messaging.py` now connects with `pika.PlainCredentials(RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)`. Previously the client passed no credentials, so pika silently authenticated as the anonymous `guest` account and the configured credentials were ignored. Verified end-to-end on Rancher (`dockerd`): the new user authenticates and connects, while `guest` and wrong passwords are rejected with `403 ACCESS_REFUSED`.

### 3. Resource limits ✅

CPU/memory requests and limits on both `apolo-11` Deployment and `rabbitmq` StatefulSet.

## High

### 4. Liveness and readiness probes ✅

HTTP probes against `/api/stats` with appropriate delays and thresholds.

### 5. Container image vulnerability scanning ✅

Trivy scan in CI pipeline blocking CRITICAL and HIGH severity CVEs.

## Medium

### 6. Network policies ✅

`k8s/rabbitmq-network-policy.yaml` restricts ingress to RabbitMQ from `app=apolo-11` pods only on ports 5672 and 15672.

### 7. PodDisruptionBudget ✅

`k8s/apolo-pdb.yaml` with `maxUnavailable: 0` to prevent voluntary disruptions.

### 8. Seccomp profile ✅

`seccompProfile.type: RuntimeDefault` applied at both pod and container level for Deployment and StatefulSet.

## Low

### 9. ImagePullPolicy ✅

Set to `Always` in both Deployment and StatefulSet to ensure fresh images in production.

### 10. HorizontalPodAutoscaler ✅

`k8s/apolo-hpa.yaml` scales 1–3 replicas based on CPU (70%) and memory (80%) utilization.

## Priority Matrix

| Item                | Priority | Effort | Impact | Status  |
| ------------------- | -------- | ------ | ------ | ------- |
| Non-root user       | Critical | Low    | High   | ✅ Done |
| RabbitMQ Secret     | Critical | Low    | High   | ✅ Done |
| No default creds    | Critical | Low    | High   | ✅ Done |
| Enforced RMQ auth   | Critical | Low    | High   | ✅ Done |
| Resource limits     | Critical | Low    | High   | ✅ Done |
| Probes              | High     | Low    | High   | ✅ Done |
| Image scanning      | High     | Medium | Medium | ✅ Done |
| NetworkPolicy       | Medium   | Medium | Medium | ✅ Done |
| PodDisruptionBudget | Medium   | Low    | Medium | ✅ Done |
| Seccomp             | Medium   | Medium | Medium | ✅ Done |
| ImagePullPolicy     | Low      | Low    | Low    | ✅ Done |
| HPA                 | Low      | Medium | Low    | ✅ Done |

## Docker Compose

`docker-compose.yml` also updated with:

- Resource limits via `deploy.resources`
- Credentials via environment variables (`.env` file recommended)
- Consistent volume mount paths with K8s (`/data/results`)

## Remaining Considerations

- **Secret rotation**: The `rabbitmq-auth` Secret uses `stringData` with plaintext values. For production, use an external secrets manager (Vault, AWS Secrets Manager, etc.) or `externalSecrets` operator.
- **TLS/Ingress**: The Ingress does not include TLS configuration. Add TLS termination with cert-manager for production.
- **Audit logging**: Enable Kubernetes audit logging to track security-relevant events.
- **Pod Security Standards**: Consider enforcing `restricted` Pod Security Standard at the namespace level.
