import json

import pytest

from events_service.database import ActivityRepository
from events_service.schemas import Activity


@pytest.mark.asyncio
async def test_get_activity(client, mocked_opa_allow, token, fastapi_request):
    repository = ActivityRepository(fastapi_request)
    added = (await repository.add(Activity(name="Sport", events=[]))).id
    await repository.session.commit()

    response = client.get(f"/api/activities/{added}", auth=token)
    assert response.status_code == 200
    assert response.json() == {"name": "Sport", "id": added, "events": []}
    assert mocked_opa_allow.called
    assert len(mocked_opa_allow.calls) == 1
    assert json.loads(mocked_opa_allow.calls[0].request.content) == {
        "input": {
            "method": "GET",
            "path": ["api", "activities", str(added)],
            "roles": [],
        }
    }


@pytest.mark.asyncio
async def test_get_activity_not_found(client, mocked_opa_allow, token):
    response = client.get("/api/activities/42", auth=token)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert mocked_opa_allow.called
    assert len(mocked_opa_allow.calls) == 1
    assert json.loads(mocked_opa_allow.calls[0].request.content) == {
        "input": {
            "method": "GET",
            "path": ["api", "activities", "42"],
            "roles": [],
        }
    }


@pytest.mark.asyncio
async def test_list_activities(
    client, mocked_opa_allow, token, fastapi_request
):
    repository = ActivityRepository(fastapi_request)
    added1 = (await repository.add(Activity(name="Sport", events=[]))).id
    added2 = (await repository.add(Activity(name="Reading", events=[]))).id
    await repository.session.commit()

    response = client.get("/api/activities", auth=token)
    assert response.status_code == 200
    assert response.json() == {
        "activities": [
            {"name": "Sport", "id": added1, "events": []},
            {"name": "Reading", "id": added2, "events": []},
        ]
    }
    assert mocked_opa_allow.called
    assert len(mocked_opa_allow.calls) == 1
    assert json.loads(mocked_opa_allow.calls[0].request.content) == {
        "input": {
            "method": "GET",
            "path": ["api", "activities"],
            "roles": [],
        }
    }


@pytest.mark.asyncio
async def test_add_activity(client, mocked_opa_allow, token, fastapi_request):
    repository = ActivityRepository(fastapi_request)
    assert await repository.list() == []

    response = client.post(
        "/api/activities", auth=token, json={"name": "Shopping"}
    )
    assert response.status_code == 201
    assert response.json() == {"name": "Shopping", "id": 1, "events": []}
    assert mocked_opa_allow.called
    assert len(mocked_opa_allow.calls) == 1
    assert json.loads(mocked_opa_allow.calls[0].request.content) == {
        "input": {
            "method": "POST",
            "path": ["api", "activities"],
            "roles": [],
        }
    }

    activities = await repository.list()
    assert len(activities) == 1
    assert activities[0].name == "Shopping"
    assert activities[0].id == 1


@pytest.mark.asyncio
async def test_delete_activity(
    client, mocked_opa_allow, token, fastapi_request
):
    repository = ActivityRepository(fastapi_request)
    added = (await repository.add(Activity(name="Sport", events=[]))).id
    await repository.session.commit()

    response = client.delete(f"/api/activities/{added}", auth=token)
    assert response.status_code == 200
    assert mocked_opa_allow.called
    assert len(mocked_opa_allow.calls) == 1
    assert json.loads(mocked_opa_allow.calls[0].request.content) == {
        "input": {
            "method": "DELETE",
            "path": ["api", "activities", str(added)],
            "roles": [],
        }
    }
    assert await repository.list() == []
    assert await repository.get(added) is None


@pytest.mark.asyncio
async def test_delete_activity_not_found(client, mocked_opa_allow, token):
    response = client.delete("/api/activities/42", auth=token)
    assert response.status_code == 404
    assert mocked_opa_allow.called
    assert len(mocked_opa_allow.calls) == 1
    assert json.loads(mocked_opa_allow.calls[0].request.content) == {
        "input": {
            "method": "DELETE",
            "path": ["api", "activities", "42"],
            "roles": [],
        }
    }
