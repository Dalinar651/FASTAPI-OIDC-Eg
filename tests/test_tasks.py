import asyncio

import httpx
import pytest
from httpx import ASGITransport


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_crud_flow(client):
    payload = {
        "name": "Write tests",
        "description": "Add CRUD test coverage",
        "created_by": "dhruv",
        "completed": False,
    }

    resp = await client.post("/tasks/", json=payload)
    assert resp.status_code == 201
    task = resp.json()
    task_id = task["id"]

    assert task["name"] == payload["name"]
    assert task["description"] == payload["description"]
    assert task["created_by"] == payload["created_by"]
    assert task["completed"] is False
    assert task["created_at"]
    assert task["updated_at"]

    resp = await client.get("/tasks/")
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id

    resp = await client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200

    update_payload = {
        "name": "Write more tests",
        "description": "Now with updates",
        "created_by": "malicious",
        "completed": True,
    }
    resp = await client.put(f"/tasks/{task_id}", json=update_payload)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["name"] == update_payload["name"]
    assert updated["description"] == update_payload["description"]
    assert updated["completed"] is True
    assert updated["created_by"] == payload["created_by"]
    assert updated["updated_at"] != task["updated_at"]

    resp = await client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/tasks/{task_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_ordering(client):
    payload_1 = {
        "name": "First task",
        "description": "Created first",
        "created_by": "dhruv",
        "completed": False,
    }
    payload_2 = {
        "name": "Second task",
        "description": "Created second",
        "created_by": "dhruv",
        "completed": False,
    }

    resp = await client.post("/tasks/", json=payload_1)
    assert resp.status_code == 201
    first_id = resp.json()["id"]

    await asyncio.sleep(0.01)

    resp = await client.post("/tasks/", json=payload_2)
    assert resp.status_code == 201
    second_id = resp.json()["id"]

    resp = await client.get("/tasks/")
    assert resp.status_code == 200
    tasks = resp.json()
    assert tasks[0]["id"] == second_id
    assert tasks[1]["id"] == first_id


@pytest.mark.asyncio
async def test_validation_errors(client):
    base = {
        "name": "Valid",
        "description": "Valid description",
        "created_by": "dhruv",
        "completed": False,
    }

    resp = await client.post("/tasks/", json={**base, "name": ""})
    assert resp.status_code == 422

    resp = await client.post("/tasks/", json={**base, "name": " "})
    assert resp.status_code == 422

    resp = await client.post("/tasks/", json={**base, "description": "x" * 4001})
    assert resp.status_code == 422

    resp = await client.post("/tasks/", json={**base, "created_by": ""})
    assert resp.status_code == 422

    resp = await client.get("/tasks/?limit=0")
    assert resp.status_code == 422

    resp = await client.get("/tasks/?offset=-1")
    assert resp.status_code == 422

    resp = await client.get("/tasks/not-a-uuid")
    assert resp.status_code == 422
