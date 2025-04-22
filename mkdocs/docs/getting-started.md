# Getting Started

Welcome to the magllama project!

## Prerequisites

- Python 3.9+
- Docker & Docker Compose
- PostgreSQL

## Quickstart

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-dir>
   ```

2. **Copy and configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

   - For production, set your `DATABASE_URL` to use a dedicated PostgreSQL user with only `SELECT`, `INSERT`, and `UPDATE` privileges (no `DELETE`, `ALTER`, or `TRUNCATE`). See the "Database" docs for details.

3. **Start the services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the API:**
   - The API will be available at [http://localhost:8000/](http://localhost:8000/)

5. **Run database migrations (if needed):**
   ```bash
   psql -U postgres -h localhost -d postgres -f postgres/init.sql
   ```

6. **Explore the API documentation:**
   - [Swagger UI (OpenAPI) docs](http://localhost:8000/docs)
   - [ReDoc documentation](http://localhost:8000/redoc)
   - [OpenAPI JSON schema](http://localhost:8000/openapi.json)
   - Root endpoint: [http://localhost:8000/](http://localhost:8000/)
