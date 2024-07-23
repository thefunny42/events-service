import uuid
from typing import Literal, overload

import alembic.config
import alembic.context
import alembic.environment
import alembic.script
import fastapi
import fastapi.testclient
import httpx
import pytest
import pytest_asyncio
import respx
import sqlalchemy
import whtft.security
import whtft.app.repository

from events_service import api, main, models, settings
from events_service.database import Database


@pytest.fixture(scope="package")
def checker():
    return whtft.security.Checker(settings.Settings())


@pytest_asyncio.fixture()
async def database():
    database = Database(settings.Settings())
    try:
        yield database
    finally:
        await database.close()


@pytest_asyncio.fixture
async def token(checker):
    return await checker.generate_token()


@pytest_asyncio.fixture
async def client(checker, alembic_env):
    main.app.dependency_overrides.clear()
    main.app.dependency_overrides[api.security] = checker
    with fastapi.testclient.TestClient(main.app) as client:
        yield client


@pytest.fixture
def mocked_opa(checker):
    with respx.mock(base_url=checker.settings.authorization_url) as mock:
        yield mock.post(name="opa")


@pytest.fixture
def mocked_opa_allow(mocked_opa):
    mocked_opa.return_value = httpx.Response(
        200, json={"result": {"allow": True}}
    )
    yield mocked_opa


@pytest_asyncio.fixture
async def fastapi_request(alembic_env, database: Database):
    request = fastapi.Request({"type": "http"})
    async with database.annotate(request):
        yield request


@pytest_asyncio.fixture
async def alembic_env(async_db_connection):
    config = alembic.config.Config()
    config.set_main_option("script_location", "events_service:alembic")
    config.set_main_option("version_path_separator", "os")
    script = alembic.script.ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs("head", rev)

    with alembic.environment.EnvironmentContext(
        config, script, fn=upgrade
    ) as context:

        def migrate(sync_db_connection):
            context.configure(
                connection=sync_db_connection,
                target_metadata=models.Base.metadata,
            )
            with context.begin_transaction():
                context.run_migrations()

        await async_db_connection.run_sync(migrate)

    yield async_db_connection


@pytest_asyncio.fixture
async def async_db_connection(database: Database):
    async with database.connect() as connection:
        await connection.execution_options(isolation_level="AUTOCOMMIT")

        @overload
        async def run(query: str, fetch: Literal[False] = False) -> None: ...

        @overload
        async def run(query: str, fetch: Literal[True]) -> str: ...

        async def run(query, fetch=False):
            result = await connection.execute(sqlalchemy.text(query))
            if fetch and (row := result.fetchone()) is not None:
                return row[0]
            return None

        test_schema = uuid.uuid4().hex
        search_path = await run("SHOW search_path", fetch=True)
        user = await run("SELECT CURRENT_USER", fetch=True)
        await run(f'CREATE SCHEMA "{test_schema}" AUTHORIZATION "{user}"')
        await run(f'ALTER ROLE "{user}" SET search_path = "{test_schema}"')
        await run(f'SET search_path = "{test_schema}"')
        try:
            yield connection
        finally:
            await run(f'ALTER ROLE "{user}" SET search_path = {search_path}')
            await run(f'DROP SCHEMA "{test_schema}" CASCADE')
