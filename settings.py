import os
from os.path import dirname, join

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
if not os.path.exists(dotenv_path):
    with open(dotenv_path, "w+") as file:
        file.writelines(
            [
                "CHARACTER_NAME=\n\n",
                "DISCORD_BOT_TOKEN=\n",
                "TEST_GUILD=\n\n",
                "TEMP_FOLDER=\n\n",
                "PLAYWRIGHT_TIMEOUT=\n\n",
                "LOCAL_SERVER_PORT=\n",
                "SILLY_TAVERN_PORT=\n\n",
            ]
        )
    raise Exception("Dotenv generated. Please rerun again after editing the contents.")

load_dotenv(dotenv_path)

CHARACTER_NAME = os.environ.get("CHARACTER_NAME", "")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
TEST_GUILD = int(os.environ.get("TEST_GUILD", "0"))
TEMP_FOLDER = os.environ.get("TEMP_FOLDER", "ST_DISCORD_TEMP")
PLAYWRIGHT_TIMEOUT = int(os.environ.get("PLAYWRIGHT_TIMEOUT", "0")) or 2000
LOCAL_SERVER_PORT = int(os.environ.get("LOCAL_SERVER_PORT", "0")) or 8001
SILLY_TAVERN_PORT = int(os.environ.get("SILLY_TAVERN_PORT", "0")) or 8000
