import json, time

from config import DEFAULTS_JSON_FILE_PATH


async def stats_roles_set() -> bool:
    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
        data = json.load(file)

        if data["top_stats_role"] != 0 and data["sub_stats_role"] != 0:
            return True
        else:
            return False

async def is_tracking():
    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
        data = json.load(file)

        if data["tracking_start_date"] == 0:
            return False
        else:
            return True
        
async def get_tracking_start_date() -> int:
    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
        data = json.load(file)

    return data["tracking_start_date"]

async def reset_tracking_start_date():
    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
        data = json.load(file)

    data["tracking_start_date"] = int(time.time())

    with open(DEFAULTS_JSON_FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

async def get_days_passed():
    current_date = int(time.time())
    start_date = await get_tracking_start_date()

    return round((current_date - start_date) / 86400)