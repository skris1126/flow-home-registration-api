# Registration Service

Standalone FastAPI service that owns account creation for Flow Home. It is the
source of truth for the `users` table schema — it ships and runs the Flyway
migrations that [`login-service`](../login-service) depends on.

## Endpoints

- `POST /api/auth/register` — create an account (email, username, password, 4-digit PIN)
- `GET /health` — confirms the database and migrated schema are reachable

## Running locally

```bash
docker network create flow_home_auth_net   # once, shared with login-service
docker compose up --build
```

This starts Postgres, runs the Flyway migrations in `db/migrations/`, and
serves the API on `http://localhost:8091`.

To run `login-service` against the same database, start this stack first so
the schema exists, then start `login-service` (it joins the same
`flow_home_auth_net` network and talks to the `auth-postgres` container).

## Configuration

See `.env.example`:

- `POSTGRES_DSN` — connection string for the `users` table
- `DASHBOARD_ORIGINS` — comma-separated CORS origins allowed to call this API
