import pytest
import time
from uuid import UUID
from tests.e2e.helper_functions import parse_iso
from tests.factories import ProjectFactory, UserFactory


@pytest.mark.asyncio
async def test_get_project_by_id(client, async_session):
    project = await ProjectFactory.create_async(session=async_session)

    response = await client.get(f"/api/v1/projects/{project.id}")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == project.name


@pytest.mark.asyncio
async def test_get_project_by_name(client, async_session):
    project = await ProjectFactory.create_async(session=async_session)

    response = await client.get(f"/api/v1/projects/name/{project.name}")
    assert response.status_code == 200, response.text
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == project.name


@pytest.mark.asyncio
async def test_get_all_tasks(client, async_session):
    projects = [
        await ProjectFactory.create_async(session=async_session) for _ in range(3)
    ]

    response = await client.get("/api/v1/projects/")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert len(payload) == 3

    returned_by_id = {UUID(item["id"]): item for item in payload}

    for project in projects:
        row = returned_by_id.get(project.id)
        assert row is not None, f"Project {project.id} missing from response"

        assert row["name"] == project.name
        assert row["description"] == project.description


@pytest.mark.asyncio
async def test_post_project(client, async_session):
    user = await UserFactory.create_async(session=async_session)
    project_in = {
        "name": "Alpha Project",
        "description": "Create Alpha version of the API",
        "owner_id": str(user.id),
    }

    post_resp = await client.post("/api/v1/projects/", json=project_in)
    assert post_resp.status_code == 201, post_resp.text

    resp = await client.get(f"/api/v1/projects/name/{project_in['name']}")
    assert resp.status_code == 200, resp.text
    for key in project_in.keys():
        assert project_in[key] == resp.json()[0][key]


@pytest.mark.asyncio
async def test_update_project(client, async_session):
    project = await ProjectFactory.create_async(session=async_session)

    resp = await client.get(f"/api/v1/projects/{project.id}")
    assert resp.status_code == 200, resp.text

    orig_created = project.created_at
    orig_updated = project.updated_at

    project_update = {"name": "Test name", "description": "Test description"}

    time.sleep(1)
    upt_resp = await client.patch(f"/api/v1/projects/{project.id}", json=project_update)
    assert upt_resp.status_code == 200, upt_resp.text
    payload = upt_resp.json()

    for key in project_update.keys():
        assert payload[key] == project_update[key]

    assert orig_created == parse_iso(payload["created_at"])
    assert orig_updated < parse_iso(payload["updated_at"])

    await async_session.refresh(project)
    assert project.name == payload["name"]
    assert project.description == payload["description"]
    assert project.created_at == orig_created
    assert project.updated_at > orig_updated


@pytest.mark.asyncio
async def test_delete_project(client, async_session):
    project = await ProjectFactory.create_async(session=async_session)

    r = await client.get(f"/api/v1/projects/{project.id}")
    assert r.status_code == 200, r.text

    r = await client.delete(f"/api/v1/projects/{project.id}")
    assert r.status_code == 204, r.text

    r = await client.get(f"/api/v1/projects/{project.id}")
    assert r.status_code == 404, r.text
