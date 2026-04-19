import json
from datetime import datetime, timezone
from pathlib import Path

from db.models.plan import Route

SAVED_ROUTES_FILE = Path(__file__).resolve().parents[3] / "data" / "saved_routes.json"


def save_route_to_json(route: Route) -> str:
    SAVED_ROUTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    saved_routes: list[dict] = []
    if SAVED_ROUTES_FILE.exists():
        try:
            with SAVED_ROUTES_FILE.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
            if isinstance(loaded, list):
                saved_routes = loaded
        except (OSError, json.JSONDecodeError):
            saved_routes = []

    saved_at = datetime.now(timezone.utc).isoformat()
    saved_routes.append(
        {
            "saved_at": saved_at,
            "route": route.model_dump(),
        }
    )

    with SAVED_ROUTES_FILE.open("w", encoding="utf-8") as file:
        json.dump(saved_routes, file, indent=2, ensure_ascii=True)

    return saved_at
