# Task 1 Backend

## Structure

```text
app/
  api/
    routes/
  core/
```

## Local Startup

Start the project locally with Docker Compose from the repository root.

1. Start the local stack:

   ```bash
   docker compose -f deployment/local/docker-compose.yaml up --build
   ```

3. Stop the local stack:

   ```bash
   docker compose -f deployment/local/docker-compose.yaml down
   ```

4. Open the local endpoints:

   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
   - Health check: [http://127.0.0.1:8000/api/v1/health/](http://127.0.0.1:8000/api/v1/health/)

