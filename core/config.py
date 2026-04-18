import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL: raise ValueError("DATABASE_URL is not set in .env")

DEFAULT_BUILDING_NAME = "Special Building"
DEFAULT_BUILDING_DESCRIPTION = (
    "This is the special building of software engineering major in my university"
)

DEFAULT_FLOOR_NUMBER = 3