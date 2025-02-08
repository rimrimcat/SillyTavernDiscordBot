# SillyTavernDiscordBot

Allows for interaction between SillyTavern and Discord using Playwright and Hikari.

## Installation

In your venv or conda environment:

```bash
pip install -r requirements
playwright install-deps
playwright install chromium
```

## Usage

If you don't have a discord bot yet, please create one first: https://discord.com/developers/applications

After running `st_server.py` or `settings.py`, a new `.dotenv` file should appear, if there isn't already.

You will need to set the variables there accordingly.

If done, run `st_server.py` and `discord_bot_example.py` (can be done on separate terminal).

DM your discord bot, or add to a server channel and mention if you want it to generate a message.

## How does it work?

1. `ST` class uses Playwright to create a headless chromium browser that connects to SillyTavern, simulating user actions such as changing persona, changing chat, or sending a message.
2. `AsyncServer` class uses aiohttp to make a local web server.
3. The discord bot sends POST request to the `AsyncServer`, which gets processed and the `ST` class is used to perform sending messages and stuff.
4. If the LLM has a reply, then the discord bot will send the message to corresponding DM/Server channel.

## Contributing

Feel free to contribute.