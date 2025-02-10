from datetime import datetime

import hikari
import requests
import tanjun
from hikari import DMChannel, GuildChannel, TextableChannel
from tanjun.abc import SlashContext

from settings import LOCAL_SERVER_PORT
from st_server import Datas, Responses

REQUEST_URL = f"http://127.0.0.1:{LOCAL_SERVER_PORT}"
CHAT_URL = f"{REQUEST_URL}/chat"
REGENERATE_URL = f"{REQUEST_URL}/regenerate"
CLEAR_URL = f"{REQUEST_URL}/clear"

component = tanjun.Component()


@component.with_slash_command
@tanjun.as_slash_command("regenerate", "Makes the bot regenerate the response")
async def regenerate(ctx: SlashContext) -> None:
    cache = ctx.client.cache
    rest = ctx.client.rest

    author_handle = ctx.author.global_name

    guild = ctx.get_guild()
    channel = ctx.get_channel()

    bot = cache.get_me() or rest.fetch_my_user()

    await ctx.defer(ephemeral=True)

    if guild is None:
        # Direct Message
        # TODO: CANT ALWAYS ASSUME THIS; NO GUILD => DM OR GROUP DM
        channel = await ctx.author.fetch_dm_channel()

        msg_it = channel.fetch_history(around=datetime.now())
        msg: hikari.Message = await anext(msg_it)

        if (msg.author.id == bot.id) and msg.content:
            # Check if last message is from bot
            async with channel.trigger_typing():
                data = Datas.for_dm(
                    author_handle=author_handle,
                    message="",
                )

                # trunk-ignore-all(bandit/B113)
                resp: requests.models.Response = requests.post(
                    REGENERATE_URL, json=data
                )

                resp_data: Responses.Response = resp.json()

                await msg.edit(resp_data["data"]["message"])
    elif isinstance(channel, GuildChannel):
        # Group Message

        msg_it = channel.fetch_history(around=datetime.now())
        msg = await anext(msg_it)
        if (msg.author.id == bot.id) and msg.content:
            # Check if last message is from bot
            async with channel.trigger_typing():
                data = Datas.for_group(
                    author_handle=author_handle,
                    guild_id=guild.id,
                    channel_id=channel.id,
                    message="",
                    trigger=False,
                )

                resp = requests.post(REGENERATE_URL, json=data)
                resp_data = resp.json()
                await msg.edit(resp_data["data"]["message"])

    await ctx.respond("[Response sent.]", delete_after=3)


@component.with_slash_command
@tanjun.as_slash_command("trigger", "Triggers the bot to respond in group chat")
async def trigger(ctx: SlashContext) -> None:
    author_handle = ctx.author.global_name

    guild = ctx.get_guild()
    guild_id = guild.id
    channel = ctx.get_channel()
    channel_id = channel.id

    await ctx.defer()

    if (guild is not None) and isinstance(channel, GuildChannel):
        async with channel.trigger_typing():
            data = Datas.for_group(
                author_handle=author_handle,
                guild_id=guild_id,
                channel_id=channel_id,
                message="",
                trigger=True,
            )

            resp: requests.models.Response = requests.post(CHAT_URL, json=data)
            resp_data: Responses.Response = resp.json()
            await channel.send(content=resp_data["data"]["message"])

        await ctx.respond("[Response sent.]", delete_after=1)
    else:
        await ctx.respond("[Command only usable on server channels!]", delete_after=10)


@component.with_slash_command
@tanjun.as_slash_command("clear", "Clears the chat history with the bot")
async def clear(ctx: SlashContext) -> None:
    cache = ctx.client.cache
    rest = ctx.client.rest

    author_handle = ctx.author.global_name

    guild = ctx.get_guild()
    channel = ctx.get_channel()

    bot = cache.get_me() or rest.fetch_my_user()

    await ctx.defer(ephemeral=True)

    if guild is None:
        # Direct Message
        # TODO: CANT ALWAYS ASSUME THIS; NO GUILD => DM OR GROUP DM

        data = Datas.for_dm(
            author_handle=author_handle,
        )
        resp: requests.models.Response = requests.post(
            CLEAR_URL,
            json=data,
        )
    elif isinstance(channel, GuildChannel):
        # Group Message
        data = Datas.for_group(
            author_handle=author_handle,
            guild_id=guild.id,
            channel_id=channel.id,
            message="",
        )

        resp = requests.post(
            CLEAR_URL,
            json=data,
        )

    await ctx.respond("[History cleared.]", delete_after=10)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
