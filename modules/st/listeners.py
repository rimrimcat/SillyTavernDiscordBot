import hikari
import requests
import tanjun
from hikari.channels import DMChannel, TextableChannel

from helpers import is_st_started
from settings import CHARACTER_NAME, LOCAL_SERVER_PORT
from st_server import Datas, Responses

REQUEST_URL = f"http://127.0.0.1:{LOCAL_SERVER_PORT}"
CARD_URL = f"{REQUEST_URL}/card"
CHAT_URL = f"{REQUEST_URL}/chat"
REGENERATE_URL = f"{REQUEST_URL}/regenerate"

component = tanjun.Component()


@component.with_listener()
async def on_load(event: hikari.events.StartedEvent):
    rest = event.app.rest

    # Try to get ST avatar
    if is_st_started():
        # trunk-ignore(bandit/B113)
        resp = requests.get(CARD_URL)
        path = resp.json()["data"]["path"]
        await rest.edit_my_user(username=CHARACTER_NAME, avatar=path)
    else:
        await rest.edit_my_user(username=CHARACTER_NAME)


@component.with_listener()
async def on_message(event: hikari.MessageCreateEvent) -> None:
    rest = event.app.rest
    me = await rest.fetch_my_user()
    bot_id = me.id

    author_handle = event.message.author.global_name
    author_nick = event.message.author.display_name
    author_id = event.author_id

    guild_id = event.message.guild_id  # None if Direct Message
    guild_name = (
        (await rest.fetch_guild(guild_id)).name if guild_id else "Direct Message"
    )

    channel = await event.message.fetch_channel()
    channel_id = event.channel_id
    channel_name = (
        (await rest.fetch_channel(channel_id)).name if guild_id else "Direct Message"
    )
    content = event.message.content

    # For debugging
    print(f"Guild: {guild_name}({guild_id})")
    print(f"Channel: {channel_name}({channel_id})")
    print(f"Author: {author_nick}@{author_handle}({author_id})")
    print(f"Content: {content}")

    if not event.is_human or content.startswith("/") or content.startswith("!"):
        return

    if not is_st_started():
        return

    if guild_id is None and isinstance(channel, DMChannel):
        # Direct Message
        async with channel.trigger_typing():
            data = Datas.for_dm(
                author_handle=author_handle,
                message=event.message.content,
            )

            # trunk-ignore(bandit/B113)
            resp: requests.models.Response = requests.post(CHAT_URL, json=data)
            resp_data: Responses.Response = resp.json()
            await channel.send(resp_data["data"]["message"])
    elif bot_id in event.message.user_mentions_ids and isinstance(
        channel, hikari.GuildChannel
    ):
        # Group Message with trigger
        async with channel.trigger_typing():
            data = Datas.for_group(
                author_handle=author_handle,
                guild_id=guild_id,
                channel_id=channel_id,
                message=content,
                trigger=True,
            )

            # trunk-ignore(bandit/B113)
            resp = requests.post(CHAT_URL, json=data)
            resp_data = resp.json()
            await channel.send(resp_data["data"]["message"])
    elif isinstance(channel, hikari.GuildChannel):
        # Group Message without trigger
        async with channel.trigger_typing():
            data = Datas.for_group(
                author_handle=author_handle,
                guild_id=guild_id,
                channel_id=channel_id,
                message=content,
                trigger=False,
            )
            # trunk-ignore(bandit/B113)
            resp = requests.post(CHAT_URL, json=data)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
