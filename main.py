import os

import discord
from commands.rules import Rules
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD")
GUILD = int(os.getenv("GUILD"))
guild_object = discord.Object(id=GUILD)


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guild_object)
            self.synced = True
        print(f"We have logged in as {self.user}.")


client = aclient()
tree = app_commands.CommandTree(client)


@tree.command(name="test", description="testing", guild=guild_object)
async def self(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Hello {name} !")
    
tree.add_command(Rules(client), guild=guild_object)

client.run(TOKEN)

