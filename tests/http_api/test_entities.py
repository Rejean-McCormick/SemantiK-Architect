from app.adapters.api.main import create_app

app = create_app()
API_PREFIX = "/api/v1/entities"


def _entity_operations() -> list[tuple[str, dict]]:
    schema = app.openapi()
    out: list[tuple[str, dict]] = []
    for path, path_item in schema.get("paths", {}).items():
        if not str(path).startswith(API_PREFIX) or not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            if isinstance(operation, dict):
                out.append((str(path), operation))
    return out


def test_entities_routes_registered_under_api_prefix() -> None:
    operations = _entity_operations()
    assert operations, f"Expected at least one route under {API_PREFIX} to be registered."


def test_entities_routes_are_tagged_entities() -> None:
    operations = _entity_operations()
    assert operations, f"No routes found under {API_PREFIX} to check tags."
    for path, operation in operations:
        tags = operation.get("tags", [])
        assert "Entities" in tags or "entities" in tags, (
            f"Route {path} is missing the 'Entities' tag. Found: {tags}"
        )
