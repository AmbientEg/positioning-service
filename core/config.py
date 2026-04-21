import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(database_url: str) -> str:
    # Ensure SQLAlchemy async engine uses asyncpg driver even if env uses a sync URL.
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

    parsed = urlparse(database_url)
    if parsed.scheme == "postgresql+asyncpg":
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))

        # asyncpg expects "ssl"; "sslmode"/"channel_binding" are libpq-oriented.
        if "ssl" not in query and "sslmode" in query:
            query["ssl"] = query.pop("sslmode")
        query.pop("channel_binding", None)

        parsed = parsed._replace(query=urlencode(query))
        return urlunparse(parsed)

    return database_url


DATABASE_URL = _normalize_database_url(os.getenv("DATABASE_URL", ""))

if not DATABASE_URL: raise ValueError("DATABASE_URL is not set in .env")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# Defaults to disabled SQL logs in production, enabled otherwise.
SQL_ECHO = os.getenv("SQL_ECHO", "false" if IS_PRODUCTION else "true").lower() == "true"

DEFAULT_BUILDING_NAME = "Special Building"
DEFAULT_BUILDING_DESCRIPTION = (
    "This is the special building of software engineering major in my university"
)

DEFAULT_FLOOR_NUMBER = 3