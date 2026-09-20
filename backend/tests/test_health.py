from app.api.routes.health import get_health


def test_health_endpoint_does_not_require_database_rows() -> None:
    assert get_health() == {"status": "ok", "application": "AccessGuard"}
