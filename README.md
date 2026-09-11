# flow-home-registration-api

Standalone FastAPI service that owns account creation for Flow Home. It is the
source of truth for the `users` table schema — it ships and runs the Flyway
migrations that [`flow-home-login-api`](../flow-home-login-api) depends on.

## Endpoints

- `POST /api/auth/register` — create an account (email, username, password, 4-digit PIN)
- `GET /health` — confirms the database and migrated schema are reachable

## Running locally

```bash
docker network create flow_home_auth_net   # once, shared with flow-home-login-api
docker compose up --build
```

The compose service is still named `registration-service` internally; the
running container is `flow-home-registration-api`.

This starts Postgres, runs the Flyway migrations in `db/migrations/`, and
serves the API on `http://localhost:8091`.

To run `flow-home-login-api` against the same database, start this stack
first so the schema exists, then start `flow-home-login-api` (it joins the
same `flow_home_auth_net` network and talks to the `auth-postgres`
container).

## Configuration

Defaults live in `config/application.yml`:

```yaml
postgres:
  dsn: postgresql://flow_home:flow_home@localhost:5432/flow_home_auth

dashboard:
  origins:
    - http://localhost:8081
    - http://localhost:5173
```

Environment variables override the file when set (see `.env.example`), the
same precedence Spring Boot uses between `application.yml` and the
environment:

- `POSTGRES_DSN` — connection string for the `users` table
- `DASHBOARD_ORIGINS` — comma-separated CORS origins allowed to call this API
- `CONFIG_FILE` — path to an alternate YAML config file (defaults to
  `config/application.yml`)
