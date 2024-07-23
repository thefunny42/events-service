import pydantic


class Base(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class Identified(Base):
    id: int


class Event(Base):
    pass


class Activity(Base):
    name: str
    events: list[Event] = pydantic.Field(default_factory=list)


class IdentifedActivity(Identified, Activity):
    pass


class Activities(pydantic.BaseModel):
    activities: list[IdentifedActivity] = pydantic.Field(default_factory=list)
