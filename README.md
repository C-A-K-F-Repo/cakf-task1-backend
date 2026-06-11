# Task 1 Backend

## UML-diagram
[link](https://app.diagrams.net/#G18hfqUKyweYrpzRoLNKt0ZssW1pXkYcji#%7B%22pageId%22%3A%22Gc_lvAdkFbzJWjvOFYQN%22%7D)

## Architecture UML-diagram
[link](https://app.diagrams.net/#G18hfqUKyweYrpzRoLNKt0ZssW1pXkYcji#%7B%22pageId%22%3A%22Q3Dqq7EHyLY_Jdj5hEPb%22%7D)

## Report pdf file `report.pdf`

## Structure

```text
app/
  api/
    routes/
  core/
```

## Local Startup

Start the project locally with Docker Compose from the repository root.

Use exactly one profile at a time:

- `app`: API + Postgres only. The app runs with `OTEL_ENABLED=false`.
- `obs`: API + Postgres + OpenTelemetry Collector + VictoriaLogs + VictoriaTraces + Grafana. The app runs with `OTEL_ENABLED=true`.

### App Profile

1. Start the local API and database:

   ```bash
   docker compose -f deployment/local/docker-compose.yaml --profile app up --build
   ```

2. Stop the app profile stack:

   ```bash
   docker compose -f deployment/local/docker-compose.yaml --profile app down
   ```

3. Open the local endpoints:

   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
   - Health check: [http://127.0.0.1:8000/api/v1/health/](http://127.0.0.1:8000/api/v1/health/)

### Obs Profile

1. Start the full local observability stack:

   ```bash
   docker compose -f deployment/local/docker-compose.yaml --profile obs up --build
   ```

2. Stop the observability stack:

   ```bash
   docker compose -f deployment/local/docker-compose.yaml --profile obs down
   ```

3. Open the local endpoints:

   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
   - Health check: [http://127.0.0.1:8000/api/v1/health/](http://127.0.0.1:8000/api/v1/health/)
   - Grafana: [http://127.0.0.1:3000](http://127.0.0.1:3000) (`admin` / `admin`)
   - Grafana datasources are provisioned automatically on startup: `VictoriaLogs` and `VictoriaTraces`
   - VictoriaLogs health: [http://127.0.0.1:9428/health](http://127.0.0.1:9428/health)
   - VictoriaTraces health: [http://127.0.0.1:10428/health](http://127.0.0.1:10428/health)
