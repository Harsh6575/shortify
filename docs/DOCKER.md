# Docker Setup Instructions

## Local Development

To start the environment with isolated Dev volumes:

```bash
docker-compose -f infra/dev.docker-compose.yml --env-file infra/.env.dev up -d
```

## Production Testing

To run the production-ready containers:

```bash
docker-compose -f infra/prod.docker-compose.yml --env-file infra/.env.prod up -d
```

## Cleaning Up

To remove volumes for a specific environment without touching others:

```bash
docker-compose -f infra/dev.docker-compose.yml down -v
```
