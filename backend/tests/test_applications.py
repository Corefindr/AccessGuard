from fastapi.testclient import TestClient


def _application_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "ServiceNow",
        "description": "ITSM platform used for incidents and requests.",
        "application_owner": "Alex Rivera",
        "owner_email": "alex.rivera@example.com",
        "criticality": "HIGH",
        "dormancy_threshold_days": 45,
        "reminder_before_days": 14,
        "active": True,
    }
    payload.update(overrides)
    return payload


def test_create_application(client: TestClient) -> None:
    response = client.post("/api/applications", json=_application_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "ServiceNow"
    assert body["criticality"] == "HIGH"
    assert body["dormancy_threshold_days"] == 45


def test_create_application_trims_name(client: TestClient) -> None:
    response = client.post("/api/applications", json=_application_payload(name="  CyberArk  "))
    assert response.status_code == 201
    assert response.json()["name"] == "CyberArk"


def test_create_application_rejects_blank_name(client: TestClient) -> None:
    response = client.post("/api/applications", json=_application_payload(name="   "))
    assert response.status_code == 422


def test_invalid_negative_thresholds(client: TestClient) -> None:
    dormancy = client.post("/api/applications", json=_application_payload(dormancy_threshold_days=-1))
    reminder = client.post("/api/applications", json=_application_payload(name="CyberArk", reminder_before_days=-7))
    assert dormancy.status_code == 422
    assert reminder.status_code == 422


def test_list_applications(client: TestClient) -> None:
    client.post("/api/applications", json=_application_payload())
    client.post("/api/applications", json=_application_payload(name="CyberArk", criticality="CRITICAL"))
    response = client.get("/api/applications")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_application(client: TestClient) -> None:
    created = client.post("/api/applications", json=_application_payload()).json()
    response = client.get(f"/api/applications/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "ServiceNow"


def test_application_not_found(client: TestClient) -> None:
    response = client.get("/api/applications/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found."


def test_replace_application(client: TestClient) -> None:
    created = client.post("/api/applications", json=_application_payload()).json()
    response = client.put(
        f"/api/applications/{created['id']}",
        json=_application_payload(description="Updated ITSM platform.", reminder_before_days=10),
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated ITSM platform."
    assert response.json()["reminder_before_days"] == 10


def test_patch_application(client: TestClient) -> None:
    created = client.post("/api/applications", json=_application_payload()).json()
    response = client.patch(
        f"/api/applications/{created['id']}",
        json={"criticality": "CRITICAL", "dormancy_threshold_days": 30},
    )
    assert response.status_code == 200
    assert response.json()["criticality"] == "CRITICAL"
    assert response.json()["name"] == "ServiceNow"


def test_soft_delete_application(client: TestClient) -> None:
    created = client.post("/api/applications", json=_application_payload()).json()
    response = client.delete(f"/api/applications/{created['id']}")
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_duplicate_application_name(client: TestClient) -> None:
    client.post("/api/applications", json=_application_payload())
    response = client.post("/api/applications", json=_application_payload(description="Duplicate name"))
    assert response.status_code == 409
    assert "name" in response.json()["detail"]


def test_filter_applications(client: TestClient) -> None:
    client.post("/api/applications", json=_application_payload())
    client.post(
        "/api/applications",
        json=_application_payload(name="Microsoft 365", criticality="MEDIUM", active=False),
    )
    high = client.get("/api/applications", params={"criticality": "HIGH"})
    assert len(high.json()) == 1
    assert high.json()[0]["name"] == "ServiceNow"

    active = client.get("/api/applications", params={"active": True})
    assert len(active.json()) == 1


def test_search_applications(client: TestClient) -> None:
    client.post("/api/applications", json=_application_payload())
    client.post(
        "/api/applications",
        json=_application_payload(
            name="CyberArk",
            description="Privileged access management vault.",
            application_owner="Priya Raman",
        ),
    )
    by_owner = client.get("/api/applications", params={"search": "priya"})
    by_description = client.get("/api/applications", params={"search": "vault"})
    assert len(by_owner.json()) == 1
    assert by_owner.json()[0]["name"] == "CyberArk"
    assert len(by_description.json()) == 1


def test_application_pagination(client: TestClient) -> None:
    names = ["ServiceNow", "CyberArk", "Microsoft 365"]
    for name in names:
        client.post("/api/applications", json=_application_payload(name=name))
    page = client.get("/api/applications", params={"skip": 0, "limit": 2})
    assert page.status_code == 200
    assert len(page.json()) == 2

    invalid = client.get("/api/applications", params={"skip": -1})
    assert invalid.status_code == 422
