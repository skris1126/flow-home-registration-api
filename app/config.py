import os
from pathlib import Path
from typing import Any

import yaml

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "application.yml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_config = _load_yaml(Path(os.getenv("CONFIG_FILE", _DEFAULT_CONFIG_PATH)))

# Env vars take precedence over config/application.yml, same as Spring Boot's
# property-source ordering (OS environment overrides application.yml).
POSTGRES_DSN = os.getenv("POSTGRES_DSN") or _config.get("postgres", {}).get("dsn")

_origins_env = os.getenv("DASHBOARD_ORIGINS")
if _origins_env is not None:
    DASHBOARD_ORIGINS = [origin.strip() for origin in _origins_env.split(",") if origin.strip()]
else:
    DASHBOARD_ORIGINS = _config.get("dashboard", {}).get("origins", [])
