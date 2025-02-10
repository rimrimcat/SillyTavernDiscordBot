import asyncio
import os
from pathlib import Path

import hikari
import tanjun

from settings import DISCORD_BOT_TOKEN

if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


# TODO: CHANGE NICKNAME
# TODO: IMPERSONATE
# TODO: BOT FIRST MESSAGE

BOT = hikari.GatewayBot(
    intents=hikari.Intents.ALL,
    token=DISCORD_BOT_TOKEN,
)

client = tanjun.Client.from_gateway_bot(
    BOT,
    declare_global_commands=True,
    mention_prefix=True,
)

client.load_modules(
    *[f for f in Path("./modules/st").glob("*.py") if f.name != "__init__.py"]
)


if __name__ == "__main__":
    BOT.run()
