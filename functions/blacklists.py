import json

from config import BLACKLISTS_JSON_FILE_PATH


def is_person_blacklisted(user_id: int):
    with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
        data = json.load(f)

    return (user_id in data["blacklists"]["users"] or user_id in data["blacklists"]["roles"])

def is_channel_blacklisted(channel_id: int):
    with open(BLACKLISTS_JSON_FILE_PATH, "r") as f:
        data = json.load(f)

    return (channel_id in data["blacklists"]["channels"]["text"] or channel_id in data["blacklists"]["channels"]["voice"])