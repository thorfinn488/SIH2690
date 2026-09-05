import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_product_ownership_restriction():
    phone_a = f"99{str(uuid.uuid4().int)[:8]}"
    phone_b = f"98{str(uuid.uuid4().int)[:8]}"

    # 1. Register Artisan A
    reg_a = client.post("/api/auth/register", json={
        "name": "Artisan A",
        "phone": phone_a,
        "password": "Password123",
        "role": "ARTISAN",
    }).json()
    token_a = reg_a["data"]["token"]

    # 2. Register Artisan B
    reg_b = client.post("/api/auth/register", json={
        "name": "Artisan B",
        "phone": phone_b,
        "password": "Password123",
        "role": "ARTISAN",
    }).json()
    token_b = reg_b["data"]["token"]

    # 3. Artisan A creates a product
    headers_a = {"Authorization": f"Bearer {token_a}"}
    create_resp = client.post("/api/products", headers=headers_a)
    assert create_resp.status_code == 201
    product_id = create_resp.json()["data"]["product_id"]

    # 4. Artisan B tries to modify or view Artisan A's product -> 403 FORBIDDEN
    headers_b = {"Authorization": f"Bearer {token_b}"}
    edit_resp = client.put(f"/api/products/{product_id}/catalogue", json={"name": "Hacked Name"}, headers=headers_b)
    assert edit_resp.status_code == 403
    json_data = edit_resp.json()
    assert json_data["success"] is False
    assert json_data["error"]["code"] == "FORBIDDEN"
