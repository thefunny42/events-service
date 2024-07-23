import contextlib

import fastapi
import pydantic
import sqlalchemy
import sqlalchemy.ext.asyncio

from . import models, settings


class Database:

    def __init__(self, settings: settings.Settings):
        self.url = str(settings.default_database_url)
        self.engine = sqlalchemy.ext.asyncio.create_async_engine(self.url)
        self.sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(
            self.engine
        )

    async def close(self):
        await self.engine.dispose()

    @contextlib.asynccontextmanager
    async def connect(self):
        async with self.engine.connect() as connection:
            yield connection

    @contextlib.asynccontextmanager
    async def annotate(self, request: fastapi.Request):
        "Annotate a fastapi request with a database session"
        async with self.session() as session:
            request.state.session = session
            request.state.dirty = False
            yield request
            if request.state.dirty:
                await session.commit()

    @contextlib.asynccontextmanager
    async def session(self):
        "Return a database session"
        session = self.sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


database = Database(settings.settings)


class Repository[T]:
    model: type[T]

    def __init__(
        self,
        request: fastapi.Request,
    ):
        self.request = request

    @property
    def session(self) -> sqlalchemy.ext.asyncio.AsyncSession:
        return self.request.state.session

    def set_dirty(self):
        self.request.state.dirty = True

    async def get(self, id: int):
        return await self.session.get(self.model, id)

    async def delete(self, id: int):
        item = await self.session.get(self.model, id)
        if item is not None:
            await self.session.delete(item)
            self.set_dirty()
            return True
        return False

    async def list(self):
        scalars = await self.session.scalars(sqlalchemy.select(self.model))
        return scalars.all()

    async def add(self, data: pydantic.BaseModel):
        item = self.model(**data.model_dump())
        self.session.add(item)
        await self.session.flush()
        self.set_dirty()
        return item


class ActivityRepository(Repository[models.Activity]):
    model = models.Activity
