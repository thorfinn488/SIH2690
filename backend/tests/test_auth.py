import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_register_login_me_flow():
    unique_phone = f"99{str(uuid.uuid4().int)[:8]}"
    # 1. Register new user
    reg_payload = {
        "name": "Test Artisan",
        "phone": unique_phone,
        "password": "SecretPassword123",
        "role": "ARTISAN",
        "region": "Punjab",
        "craft_specialty": "Phulkari",
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_json = reg_resp.json()
    assert reg_json["success"] is True
    assert "token" in reg_json["data"]
    token = reg_json["data"]["token"]

    # 2. Access /api/auth/me with valid Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_json = me_resp.json()
    assert me_json["success"] is True
    assert me_json["data"]["phone"] == unique_phone

    # 3. Login with credentials
    login_payload = {"phone": unique_phone, "password": "SecretPassword123"}
    login_resp = client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    assert login_resp.json()["success"] is True


def test_auth_me_unauthorized_without_token():
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    json_data = resp.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "UNAUTHORIZED"
