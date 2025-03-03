import json
from config import PERMISSIONS_JSON_FILE_PATH

def check_permissions_of_user(user_id, command):
    with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
        permissions = json.load(f)

    for permission in permissions:
        if permission["command"] == command:
            if user_id in permission["users"]:
                return True
    return False

def check_permissions_of_role(role_id, command):
    with open(PERMISSIONS_JSON_FILE_PATH, "r") as f:
        permissions = json.load(f)

    for permission in permissions:
        if permission["command"] == command:
            if role_id in permission["roles"]:
                return True
    return False