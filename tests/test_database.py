import pytest

from events_service.database import ActivityRepository
from events_service.schemas import Activity


@pytest.mark.asyncio
async def test_activity(fastapi_request):
    repository = ActivityRepository(fastapi_request)
    assert await repository.list() == []

    activity = await repository.add(Activity(name="Sport", events=[]))
    assert activity.id
    assert activity.name == "Sport"

    assert await repository.list() == [activity]
    assert await repository.get(activity.id) == activity

    assert await repository.delete(activity.id) is True
    assert await repository.list() == []
    assert await repository.get(activity.id) is None

    assert await repository.delete(activity.id) is False
    assert await repository.list() == []
    assert await repository.get(activity.id) is None
