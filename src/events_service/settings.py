import pydantic
import whtft.security


class Settings(whtft.security.Settings):
    default_database_url: pydantic.AnyUrl = pydantic.Field(default=...)


settings = Settings()
