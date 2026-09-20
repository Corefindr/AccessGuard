from fastapi.testclient import TestClient


def _user_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "employee_id": "EMP001",
        "name": "Alex Morgan",
        "email": "alex.morgan@example.com",
        "team": "Service Desk",
        "lead_name": "Chris Alvarez",
        "lead_email": "chris.alvarez@example.com",
        "manager_name": "Dana Brooks",
        "manager_email": "dana.brooks@example.com",
        "active": True,
    }
    payload.update(overrides)
    return payload


def test_create_user(client: TestClient) -> None:
    response = client.post("/api/users", json=_user_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["employee_id"] == "EMP001"
    assert body["email"] == "alex.morgan@example.com"
    assert body["active"] is True


def test_create_user_normalizes_email_and_trims_employee_id(client: TestClient) -> None:
    response = client.post(
        "/api/users",
        json=_user_payload(employee_id="  EMP009  ", email="Alex.Morgan@Example.COM"),
    )
    assert response.status_code == 201
    assert response.json()["employee_id"] == "EMP009"
    assert response.json()["email"] == "alex.morgan@example.com"


def test_create_user_rejects_blank_employee_id(client: TestClient) -> None:
    response = client.post("/api/users", json=_user_payload(employee_id="   "))
    assert response.status_code == 422


def test_create_user_rejects_invalid_email(client: TestClient) -> None:
    response = client.post("/api/users", json=_user_payload(email="not-an-email"))
    assert response.status_code == 422


def test_list_users(client: TestClient) -> None:
    client.post("/api/users", json=_user_payload())
    client.post("/api/users", json=_user_payload(employee_id="EMP002", email="jordan.patel@example.com", name="Jordan Patel"))
    response = client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user(client: TestClient) -> None:
    created = client.post("/api/users", json=_user_payload()).json()
    response = client.get(f"/api/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["employee_id"] == "EMP001"


def test_user_not_found(client: TestClient) -> None:
    response = client.get("/api/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_replace_user(client: TestClient) -> None:
    created = client.post("/api/users", json=_user_payload()).json()
    response = client.put(
        f"/api/users/{created['id']}",
        json=_user_payload(name="Alex M. Morgan", team="Identity Operations"),
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Alex M. Morgan"
    assert response.json()["team"] == "Identity Operations"


def test_patch_user(client: TestClient) -> None:
    created = client.post("/api/users", json=_user_payload()).json()
    response = client.patch(f"/api/users/{created['id']}", json={"team": "Privileged Access"})
    assert response.status_code == 200
    assert response.json()["team"] == "Privileged Access"
    assert response.json()["email"] == "alex.morgan@example.com"


def test_soft_delete_user(client: TestClient) -> None:
    created = client.post("/api/users", json=_user_payload()).json()
    response = client.delete(f"/api/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["active"] is False
    fetched = client.get(f"/api/users/{created['id']}")
    assert fetched.json()["active"] is False


def test_duplicate_employee_id(client: TestClient) -> None:
    client.post("/api/users", json=_user_payload())
    response = client.post(
        "/api/users",
        json=_user_payload(email="other.user@example.com"),
    )
    assert response.status_code == 409
    assert "employee_id" in response.json()["detail"]


def test_duplicate_email(client: TestClient) -> None:
    client.post("/api/users", json=_user_payload())
    response = client.post(
        "/api/users",
        json=_user_payload(employee_id="EMP002"),
    )
    assert response.status_code == 409
    assert "email" in response.json()["detail"]


def test_update_conflict_employee_id(client: TestClient) -> None:
    first = client.post("/api/users", json=_user_payload()).json()
    second = client.post(
        "/api/users",
        json=_user_payload(employee_id="EMP002", email="jordan.patel@example.com"),
    ).json()
    response = client.patch(f"/api/users/{second['id']}", json={"employee_id": first["employee_id"]})
    assert response.status_code == 409


def test_filter_users_by_active_and_team(client: TestClient) -> None:
    client.post("/api/users", json=_user_payload())
    client.post(
        "/api/users",
        json=_user_payload(
            employee_id="EMP002",
            email="casey.ellis@example.com",
            name="Casey Ellis",
            team="Mainframe Support",
            active=False,
        ),
    )
    active = client.get("/api/users", params={"active": True})
    assert len(active.json()) == 1
    assert active.json()[0]["employee_id"] == "EMP001"

    desk = client.get("/api/users", params={"team": "Service Desk"})
    assert len(desk.json()) == 1
    assert desk.json()[0]["team"] == "Service Desk"


def test_search_users(client: TestClient) -> None:
    client.post("/api/users", json=_user_payload(name="Nishant Rao", employee_id="EMP100", email="nishant.rao@example.com"))
    client.post("/api/users", json=_user_payload(name="Alex Morgan", employee_id="EMP001", email="alex.morgan@example.com"))
    response = client.get("/api/users", params={"search": "nishant"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["employee_id"] == "EMP100"


def test_user_pagination(client: TestClient) -> None:
    for index in range(3):
        client.post(
            "/api/users",
            json=_user_payload(
                employee_id=f"EMP00{index + 1}",
                email=f"user{index + 1}@example.com",
                name=f"User {index + 1}",
            ),
        )
    page = client.get("/api/users", params={"skip": 1, "limit": 1})
    assert page.status_code == 200
    assert len(page.json()) == 1
    assert page.json()[0]["employee_id"] == "EMP002"

    invalid = client.get("/api/users", params={"limit": 201})
    assert invalid.status_code == 422
