import os
import sched
import time

import discord
from commands.recall import Recall
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD")
GUILD = int(os.getenv("GUILD"))
env_path_rules = os.getenv("ENV_PATH_RULES")
env_path_recall = os.getenv("ENV_PATH_RECALL")
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
        for guild in self.guilds:
            if guild.id == guild_object.id:
                recall._get_env(guild)

    
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if self.user.id == payload.user_id:
            return
        
        await recall.check_reaction_add(payload)

client = aclient()
tree = app_commands.CommandTree(client)
recall = Recall(client, env_path_recall)

tree.add_command(recall, guild=guild_object)

client.run(TOKEN)

