import json

from config import DEFAULTS_JSON_FILE_PATH

async def is_tracking():
    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
        data = json.load(file)

        if data["tracking_start_date"] == 0:
            return False
        else:
            return True
        
async def get_tracking_start_date():
    with open(DEFAULTS_JSON_FILE_PATH, "r") as file:
        data = json.load(file)

    return data["tracking_start_date"]