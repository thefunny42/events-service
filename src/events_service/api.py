from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from whtft.metrics import Metrics
from whtft.security import Checker

from . import database, schemas, settings

security = Checker(settings.settings)

router = APIRouter(prefix="/api", dependencies=[Depends(security)])

metrics = Metrics(prefix="eventsservice")


@router.post(
    "/activities",
    status_code=status.HTTP_201_CREATED,
    response_class=ORJSONResponse,
)
@metrics.measure()
async def add_activity(
    repository: Annotated[database.ActivityRepository, Depends()],
    activity: schemas.Activity,
):
    "Create a new activity"
    if (added_activity := await repository.add(activity)) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not add activity.",
        )
    return added_activity


@router.get(
    "/activities",
    response_model=schemas.Activities,
    response_class=ORJSONResponse,
)
@metrics.measure()
async def list_activities(
    repository: Annotated[database.ActivityRepository, Depends()]
):
    "List activities as a JSON array"
    return {"activities": await repository.list()}


@router.get(
    "/activities/{activity_id}",
    response_model=schemas.IdentifedActivity,
    response_class=ORJSONResponse,
)
@metrics.measure()
async def get_activity(
    repository: Annotated[database.ActivityRepository, Depends()],
    activity_id: int,
):
    "Get an activity"
    if (activity := await repository.get(activity_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return activity


@router.delete("/activities/{activity_id}")
@metrics.measure()
async def delete_activity(
    repository: Annotated[database.ActivityRepository, Depends()],
    activity_id: int,
):
    "Delete an activity"
    if await repository.delete(activity_id) is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
