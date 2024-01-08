import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD")
GUILD = os.getenv("GUILD")
client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord !')
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(guild.members)
    members = '\n - '.join([member.name for member in guild.members])
    print(members)
client.run(TOKEN)
