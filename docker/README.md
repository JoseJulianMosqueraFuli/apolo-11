# Docker

Archivos de contenedorización del proyecto Apolo 11.

## Estructura

```
docker/
├── Dockerfile          # Multi-stage build (builder + runtime)
├── .dockerignore       # Archivos excluidos del contexto de build
├── docker-compose.yml  # Stack completo (app + RabbitMQ + Prometheus + Grafana)
└── README.md
```

## Uso

### Levantar el stack completo

```bash
cd docker
docker compose --env-file ../.env up --build
```

### Solo build de la imagen

```bash
docker build -f docker/Dockerfile -t apolo-11:latest .
```

### Variables de entorno requeridas

Copia `.env.example` a `.env` en la raíz del proyecto y configura:

- `RABBITMQ_USER` / `RABBITMQ_PASS`
- `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`

## Servicios

| Servicio   | Puerto      | Descripción                                  |
| ---------- | ----------- | -------------------------------------------- |
| generator  | —           | Genera archivos de misión                    |
| reporter   | 8000        | Procesa archivos + API + métricas Prometheus |
| rabbitmq   | 5672, 15672 | Message broker (AMQP + Management UI)        |
| prometheus | 9090        | Scraping de métricas                         |
| grafana    | 3000        | Dashboard de monitoreo                       |
