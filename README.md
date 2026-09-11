# Registration Service

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

This starts Postgres, runs the Flyway migrations in `db/migrations/`, and
serves the API on `http://localhost:8091`.

To run `flow-home-login-api` against the same database, start this stack
first so the schema exists, then start `flow-home-login-api` (it joins the
same `flow_home_auth_net` network and talks to the `auth-postgres`
container).

## Configuration

See `.env.example`:

- `POSTGRES_DSN` — connection string for the `users` table
- `DASHBOARD_ORIGINS` — comma-separated CORS origins allowed to call this API
