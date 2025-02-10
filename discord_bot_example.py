import asyncio
import os
from pathlib import Path

import hikari
import tanjun

from settings import DISCORD_BOT_TOKEN, TEST_GUILD

if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

BOT = hikari.GatewayBot(
    intents=hikari.Intents.ALL,
    token=DISCORD_BOT_TOKEN,
)

client = tanjun.Client.from_gateway_bot(
    BOT,
    declare_global_commands=TEST_GUILD or True,
    mention_prefix=True,
)


client.load_modules(
    *[f for f in Path("./modules/st").glob("*.py") if f.name != "__init__.py"]
)


if __name__ == "__main__":
    BOT.run()
