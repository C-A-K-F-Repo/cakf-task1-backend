# Task 1 Backend 


## Structure

```text
app/
  api/
    routes/
  core/
```

## Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to see OpenAPI docs.
