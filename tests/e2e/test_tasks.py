import pytest
import time
from uuid import UUID
from tests.e2e.helper_functions import parse_iso
from tests.factories import TaskFactory, UserFactory


@pytest.mark.asyncio
async def test_get_task_by_id(client, async_session):
    task = await TaskFactory.create_async(session=async_session)

    response = await client.get(f"/api/v1/tasks/id/{task.id}")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == task.name


@pytest.mark.asyncio
async def test_get_task_by_name(client, async_session):
    task = await TaskFactory.create_async(session=async_session)

    response = await client.get(f"/api/v1/tasks/name/{task.name}")
    assert response.status_code == 200, response.text
    for resp in response.json():
        assert resp["name"] == task.name


@pytest.mark.asyncio
async def test_get_all_tasks(client, async_session):
    tasks = [await TaskFactory.create_async(session=async_session) for _ in range(3)]

    response = await client.get("/api/v1/tasks/")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert len(payload) == 3

    returned_by_id = {UUID(item["id"]): item for item in payload}

    for task in tasks:
        row = returned_by_id.get(task.id)
        assert row is not None, f"Task {task.id} missing from response"

        assert row["name"] == task.name
        assert row["description"] == task.description


@pytest.mark.asyncio
async def test_post_task(client, async_session):
    user = await UserFactory.create_async(session=async_session)
    task_in = {
        "name": "Shopping list",
        "description": "Eggs, Milk, Bread",
        "deadline": None,
        "complete": False,
        "owner_id": str(user.id),
    }

    post_resp = await client.post("/api/v1/tasks/", json=task_in)
    assert post_resp.status_code == 201, post_resp.text

    resp = await client.get(f"/api/v1/tasks/name/{task_in['name']}")
    assert resp.status_code == 200, resp.text
    for key in task_in.keys():
        assert task_in[key] == resp.json()[0][key]


@pytest.mark.asyncio
async def test_update_task(client, async_session):
    task = await TaskFactory.create_async(session=async_session)

    resp = await client.get(f"/api/v1/tasks/id/{task.id}")
    assert resp.status_code == 200, resp.text

    orig_created = task.created_at
    orig_updated = task.updated_at

    task_update = {
        "name": "Test name",
        "description": "Test description",
        "set_deadline": True,
        "deadline": None,
        "complete": True,
    }

    time.sleep(1)
    upt_resp = await client.patch(f"/api/v1/tasks/id/{task.id}", json=task_update)
    assert upt_resp.status_code == 200, upt_resp.text
    payload = upt_resp.json()

    task_update.pop("set_deadline")
    for key in task_update.keys():
        assert payload[key] == task_update[key]

    assert orig_created == parse_iso(payload["created_at"])
    assert orig_updated < parse_iso(payload["updated_at"])

    await async_session.refresh(task)
    assert task.name == payload["name"]
    assert task.description == payload["description"]
    assert task.deadline == payload["deadline"]
    assert task.complete == payload["complete"]
    assert task.created_at == orig_created
    assert task.updated_at > orig_updated


@pytest.mark.asyncio
async def test_delete_task(client, async_session):
    task = await TaskFactory.create_async(session=async_session)

    r = await client.get(f"/api/v1/tasks/id/{task.id}")
    assert r.status_code == 200, r.text

    r = await client.delete(f"/api/v1/tasks/id/{task.id}")
    assert r.status_code == 204, r.text

    r = await client.get(f"/api/v1/tasks/id/{task.id}")
    assert r.status_code == 404, r.text
