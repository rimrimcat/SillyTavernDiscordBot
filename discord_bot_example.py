import asyncio
import os

import hikari
import requests
from hikari.channels import DMChannel, TextableChannel

from settings import DISCORD_BOT_TOKEN, LOCAL_SERVER_PORT
from st_server import Datas, Responses

REQUEST_URL = f"http://127.0.0.1:{LOCAL_SERVER_PORT}"
DM_URL = f"{REQUEST_URL}/chat"
GROUP_URL = f"{REQUEST_URL}/groupchat"

if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


bot = hikari.GatewayBot(
    intents=hikari.Intents.ALL,
    token=DISCORD_BOT_TOKEN,
)


@bot.listen()
async def on_message(event: hikari.MessageCreateEvent) -> None:
    # Do not respond to bots nor webhooks pinging us, only user accounts

    bot_id = bot.get_me().id

    author_handle = event.message.author.global_name
    author_nick = event.message.author.display_name
    author_id = event.author_id

    guild_id = event.message.guild_id  # None if Direct Message
    guild_name = (
        (await bot.rest.fetch_guild(guild_id)).name if guild_id else "Direct Message"
    )

    channel = await event.message.fetch_channel()
    channel_id = event.channel_id
    channel_name = (
        (await bot.rest.fetch_channel(channel_id)).name
        if guild_id
        else "Direct Message"
    )
    content = event.message.content

    # For debugging
    print(f"Guild: {guild_name}({guild_id})")
    print(f"Channel: {channel_name}({channel_id})")
    print(f"Author: {author_nick}@{author_handle}({author_id})")
    print(f"Content: {content}")

    if not event.is_human:
        return

    if guild_id is None and isinstance(channel, DMChannel):
        # Direct Message
        async with channel.trigger_typing():
            data: Datas.Data = {
                "persona": author_handle,
                "chat": author_handle,
                "message": event.message.content,
                "character": "",
                "trigger": False,
            }

            # trunk-ignore(bandit/B113)
            resp: requests.models.Response = requests.post(DM_URL, json=data)
            resp_data: Responses.Response = resp.json()
            await channel.send(resp_data["data"]["message"])
    elif bot_id in event.message.user_mentions_ids and isinstance(
        channel, TextableChannel
    ):
        # Group Message with trigger
        async with channel.trigger_typing():
            data = {
                "persona": author_handle,
                "chat": f"{guild_name}_{channel_id}",
                "message": content,
                "character": "",
                "trigger": True,
            }
            # trunk-ignore(bandit/B113)
            resp = requests.post(GROUP_URL, json=data)
            resp_data = resp.json()
            await channel.send(resp_data["data"]["message"])
    elif isinstance(channel, TextableChannel):
        # Group Message without trigger
        async with channel.trigger_typing():
            data = {
                "persona": author_handle,
                "chat": f"{guild_name}_{channel_id}",
                "message": content,
                "character": "",
                "trigger": False,
            }
            # trunk-ignore(bandit/B113)
            resp = requests.post(GROUP_URL, json=data)


if __name__ == "__main__":
    bot.run()
