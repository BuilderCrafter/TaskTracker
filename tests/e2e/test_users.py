import pytest
from uuid import uuid4, UUID
from tests.factories import UserFactory
from tests.e2e.helper_functions import parse_iso


@pytest.mark.asyncio
async def test_get_user_ok(client, async_session):
    user = await UserFactory.create_async(session=async_session)

    r = await client.get(f"/api/v1/users/{user.id}")
    assert r.status_code == 200, r.text
    assert r.json()["email"] == user.email


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    r = await client.get(f"/api/v1/users/{uuid4()}")
    assert r.status_code == 404, r.text
    assert r.json()["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_list_users_returns_all(client, async_session):
    users = [await UserFactory.create_async(session=async_session) for _ in range(3)]

    response = await client.get("/api/v1/users/")
    assert response.status_code == 200, response.text

    payload = response.json()  # ← list[dict]

    assert len(payload) == 3

    returned_by_id = {UUID(item["id"]): item for item in payload}

    for user in users:
        row = returned_by_id.get(user.id)
        assert row is not None, f"User {user.id} missing from response"

        assert row["email"] == user.email
        assert row["full_name"] == user.full_name


@pytest.mark.asyncio
async def test_update_user(client, async_session):
    # Create user
    user = await UserFactory.create_async(session=async_session)

    response = await client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200, response.text

    created_orig = user.created_at
    updated_orig = user.updated_at

    # Update payload
    payload = {
        "full_name": f"{user.full_name}_new",
        "email": f"new_{user.email}",
        "is_active": False,
    }

    new_response = await client.patch(f"/api/v1/users/{user.id}", json=payload)
    data = new_response.json()

    assert new_response.status_code == 200, new_response.text
    for key, value in payload.items():
        assert data[key] == value

    created_resp = parse_iso(data["created_at"])
    updated_resp = parse_iso(data["updated_at"])

    assert created_resp == created_orig
    assert updated_resp > updated_orig

    await async_session.refresh(user)
    assert user.email == payload["email"]
    assert user.full_name == payload["full_name"]
    assert user.is_active == payload["is_active"]
    assert user.created_at == created_orig
    assert user.updated_at > updated_orig


@pytest.mark.asyncio
async def test_delete_user(client, async_session):
    user = await UserFactory.create_async(session=async_session)

    r = await client.get(f"/api/v1/users/{user.id}")
    assert r.status_code == 200, r.text

    r = await client.delete(f"/api/v1/users/{user.id}")
    assert r.status_code == 204, r.text

    r = await client.get(f"/api/v1/users/{user.id}")
    assert r.status_code == 404, r.text
