import requests
import os
from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from settings import LOCAL_SERVER_PORT, TEMP_FOLDER
import pickle

REQUEST_URL = f"http://127.0.0.1:{LOCAL_SERVER_PORT}"


NICKNAMES_FILE = f"{TEMP_FOLDER}/nicknames.pkl"


def is_st_started():
    try:
        # trunk-ignore(bandit/B113)
        tresp = requests.get(REQUEST_URL)
        tresp_data = tresp.json()
        if not tresp_data["status"] or tresp_data["status"] != "success":
            raise ConnectionError()
        return True
    except (ConnectionError, MaxRetryError):
        print("ST server not started yet!")
        return False


def get_nickname(author_handle: str):
    if os.path.exists(NICKNAMES_FILE):
        with open(NICKNAMES_FILE, "rb") as file:
            nicknames = pickle.load(file)
        return nicknames.get(author_handle, author_handle)
    else:
        return author_handle
