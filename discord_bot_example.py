import discord
from settings import DISCORD_BOT_TOKEN, LOCAL_SERVER_PORT
import requests
from st_server import Datas
from st_server import Responses

REQUEST_URL = f"http://127.0.0.1:{LOCAL_SERVER_PORT}"
DM_URL = f"{REQUEST_URL}/chat"
GROUP_URL = f"{REQUEST_URL}/groupchat"


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message: discord.Message):
        print(f"Message from {message.author}: {message.content}")
        if client.user == message.author:
            return

        if "Direct Message" in str(message.channel):
            # DM
            data: Datas.Data = {
                "persona": message.author.name,
                "chat": message.author.name,
                "message": message.content,
                "character": "",
                "trigger": False,
            }
            resp: requests.models.Response = requests.post(DM_URL, json=data)
            resp_data: Responses.Response = resp.json()
            await message.channel.send(resp_data["data"]["message"])
            return
        elif client.user in message.mentions:
            # Mentioned in Server
            data = {
                "persona": message.author.name,
                "chat": f"{message.channel.guild.name}_{message.channel.id}",
                "message": message.content,
                "character": "",
                "trigger": True,
            }
            resp = requests.post(GROUP_URL, json=data)
            resp_data = resp.json()
            await message.channel.send(resp_data["data"]["message"])
        else:
            # Not Mentioned
            data = {
                "persona": message.author.name,
                "chat": f"{message.channel.guild.name}_{message.channel.id}",
                "message": message.content,
                "character": "",
                "trigger": False,
            }
            resp = requests.post(GROUP_URL, json=data)
            resp_data = resp.json()


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)
