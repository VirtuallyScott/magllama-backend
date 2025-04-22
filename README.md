# magllama

magllama is a microservice-based API for managing users, roles, permissions, projects, scans, and artifacts with PostgreSQL backend.

## Features

- User management with UUID primary keys
- Role-based access control with permissions
- Project and project membership management
- Activity logging
- Async FastAPI backend with asyncpg for PostgreSQL

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (can be run via Docker)

### Running with Docker Compose

Create a `.env` file with your database URL, for example:

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
```

Then run:

```bash
docker-compose up --build
```

This will start the API server and a PostgreSQL database.

### API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API docs.

## Project Structure

- `api/` - FastAPI application source code
- `postgres/` - SQL schema and initialization scripts
- `db/` - Database-related scripts or migrations (empty currently)

## Contributing

Contributions are welcome! Please open issues or pull requests.

## License

MIT License
