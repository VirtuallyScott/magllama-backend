# Building

## Building the API

You can build the API service using Docker:

```bash
docker-compose build api
```

Or build the Docker image directly:

```bash
docker build -t magllama-api ./api
```

## Running Locally (without Docker)

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r api/requirements.txt
   ```

3. Set up environment variables (see `.env.example`).

4. Start the API:
   ```bash
   uvicorn api.main:app --reload
   ```
