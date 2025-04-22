# Deploying

## Docker Compose

The recommended way to deploy magllama is with Docker Compose:

```bash
docker-compose up --build -d
```

## Production Considerations

- Set secure values in your `.env` file.
- Use a production-ready database (not the default local one).
- Configure HTTPS for the API.
- Set up backups for your PostgreSQL database.
- Use a process manager or orchestration platform for production deployments.

## Database Initialization

If you need to initialize the database manually:

```bash
psql -U postgres -h <db-host> -d <db-name> -f postgres/init.sql
```
