import json

from functions.database import database

from config import DATABASE_FILE_PATH
from config import DEFAULTS_JSON_FILE_PATH

async def is_person_jailed(user_id: int):
    db = database(DATABASE_FILE_PATH)
    return db.is_person_jailed(user_id)

async def get_jail_role():
    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
        data = json.load(file)

    return data["jail_role"]