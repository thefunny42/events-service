import contextlib

import fastapi
import whtft.app

from . import api, database, settings

__version__ = "0.1.0"


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    yield
    await database.database.close()


app = fastapi.FastAPI(lifespan=lifespan)


app.mount("/metrics", api.metrics.app)


@app.middleware("http")
async def db_session_middleware(request: fastapi.Request, call_next):
    async with database.database.annotate(request):
        response = await call_next(request)
    return response


@app.get("/health")
async def get_health(ready: bool = False):
    return {}


app.include_router(api.router)


def main():  # pragma: no cover
    whtft.app.main(app, settings.settings)
