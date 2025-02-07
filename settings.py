# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
if not os.path.exists(dotenv_path):
    with open(dotenv_path, "w+") as file:
        file.writelines(
            [
                "SILLY_TAVERN_PORT=8000\n",
                "LOCAL_SERVER_PORT=8001\n",
                "CHARACTER_NAME=Rim\n",
                "DISCORD_BOT_TOKEN=\n"
            ]
        )
    raise Exception("Dotenv generated. Please rerun again after editing the contents.")

load_dotenv(dotenv_path)

SILLY_TAVERN_PORT = int(os.environ.get("SILLY_TAVERN_PORT"))
LOCAL_SERVER_PORT = int(os.environ.get("LOCAL_SERVER_PORT"))
CHARACTER_NAME = os.environ.get("CHARACTER_NAME")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
