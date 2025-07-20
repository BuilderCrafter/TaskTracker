import pytest
from tests.factories import TaskFactory


@pytest.mark.asyncio
async def test_get_task(client, async_session):
    task = await TaskFactory.create_async(session=async_session)

    response = await client.get(f"/api/v1/tasks/id/{task.id}")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == task.name
