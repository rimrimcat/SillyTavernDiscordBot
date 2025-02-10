from datetime import datetime
import os
import pickle
from typing import Annotated, Optional

import hikari
import requests
import tanjun
from hikari import DMChannel, GuildChannel, TextableChannel
from tanjun.abc import SlashContext
from tanjun.annotations import Str

from settings import LOCAL_SERVER_PORT, TEMP_FOLDER
from st_server import Datas, Responses
from helpers import get_nickname

REQUEST_URL = f"http://127.0.0.1:{LOCAL_SERVER_PORT}"
CHAT_URL = f"{REQUEST_URL}/chat"
REGENERATE_URL = f"{REQUEST_URL}/regenerate"
CLEAR_URL = f"{REQUEST_URL}/clear"
DESC_URL = f"{REQUEST_URL}/desc"
NICKNAME_URL = f"{REQUEST_URL}/nickname"


GREETINGS_FILE = f"{TEMP_FOLDER}/greetings.pkl"
NICKNAMES_FILE = f"{TEMP_FOLDER}/nicknames.pkl"

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
                    author_handle=get_nickname(author_handle),
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
                    author_handle=get_nickname(author_handle),
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
                author_handle=get_nickname(author_handle),
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
            author_handle=get_nickname(author_handle),
        )
        resp: requests.models.Response = requests.post(
            CLEAR_URL,
            json=data,
        )

        await ctx.respond("[History cleared.]", delete_after=10)

        if os.path.exists(GREETINGS_FILE):
            channel = await ctx.author.fetch_dm_channel()
            with open(GREETINGS_FILE, "rb") as file:
                # trunk-ignore-all(bandit/B301)
                greetings = pickle.load(file)
                await channel.send(greetings[0])

    elif isinstance(channel, GuildChannel):
        # Group Message
        data = Datas.for_group(
            author_handle=get_nickname(author_handle),
            guild_id=guild.id,
            channel_id=channel.id,
            message="",
        )

        resp = requests.post(
            CLEAR_URL,
            json=data,
        )

        await ctx.respond("[History cleared.]", delete_after=10)

        if os.path.exists(GREETINGS_FILE):
            with open(GREETINGS_FILE, "rb") as file:
                greetings = pickle.load(file)
                await channel.send(greetings[0])

    else:
        await ctx.respond("[Invalid channel.]", delete_after=10)


@component.with_slash_command
@tanjun.with_str_slash_option(
    "new_description", "New description to set to yourself", default=""
)
@tanjun.as_slash_command("description", "Gets or sets your description")
async def description(ctx: SlashContext, new_description: str = "") -> None:
    author_handle = ctx.author.global_name
    is_new_desc = True if new_description else False

    await ctx.defer(ephemeral=True)

    data = Datas.for_dm(
        author_handle=get_nickname(author_handle),
        message=new_description,
        trigger=is_new_desc,
    )
    resp: requests.models.Response = requests.post(
        DESC_URL,
        json=data,
    )

    if is_new_desc:
        await ctx.respond("[Description set.]", delete_after=10)
    else:
        resp_data: Responses.Response = resp.json()
        desc = resp_data["data"]["message"]

        if desc:
            await ctx.respond(f"[Obtained description: {desc}]")
        else:
            await ctx.respond("[No description found, please set one first.]")


@component.with_slash_command
@tanjun.with_str_slash_option(
    "new_nickname", "New nickname to set to yourself", default=""
)
@tanjun.as_slash_command("nickname", "Gets or sets your nickname")
async def nickname(ctx: SlashContext, new_nickname: str = "") -> None:
    author_handle = ctx.author.global_name
    is_new_nick = True if new_nickname else False

    if os.path.exists(NICKNAMES_FILE):
        with open(NICKNAMES_FILE, "rb") as file:
            nicknames = pickle.load(file)
    else:
        nicknames = {}

    if new_nickname == nicknames.get(author_handle):
        is_new_nick = False

    await ctx.defer(ephemeral=True)

    if is_new_nick:
        # Check if nickname isnt taken yet
        if new_nickname in nicknames.values():
            # Dont want to deal with same nicknames
            await ctx.respond(
                "[Nickname already taken! Please choose another nickname.]",
                delete_after=10,
            )
            return

        # Check if it exists already
        if author_handle in nicknames:
            # Nickname set, rename using stored nickname

            data = Datas.for_dm(
                author_handle=nicknames[author_handle],
                message=new_nickname,
            )
            resp: requests.models.Response = requests.post(
                NICKNAME_URL,
                json=data,
            )

            nicknames[author_handle] = new_nickname

            with open(NICKNAMES_FILE, "wb") as file:
                pickle.dump(nicknames, file)

            await ctx.respond(
                f"[Nickname successfully set to {new_nickname}]", delete_after=10
            )
        else:
            # New nickname
            nicknames[author_handle] = new_nickname

            with open(NICKNAMES_FILE, "wb") as file:
                pickle.dump(nicknames, file)

            data = Datas.for_dm(
                author_handle=author_handle,
                message=new_nickname,
            )
            resp = requests.post(
                NICKNAME_URL,
                json=data,
            )

            await ctx.respond(
                f"[Nickname successfully set to {new_nickname}]", delete_after=10
            )

    else:
        # Just return the current one
        if author_handle in nicknames:
            await ctx.respond(
                f"[Current nickname: {nicknames[author_handle]}]", delete_after=10
            )
        else:
            await ctx.respond("[No nickname, please set one first.]", delete_after=10)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
