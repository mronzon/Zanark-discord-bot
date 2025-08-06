import os
import sched
import time

import discord
from commands.gvg import Gvg
from commands.recall import Recall
from commands.rename import RenameAll, UnrenameAll
from discord import app_commands
from dotenv import load_dotenv
import aiohttp

from commands.rules import Rules
from commands.bdg import Bdg

load_dotenv()

TOKEN = os.getenv("DISCORD")
GUILD = int(os.getenv("GUILD"))
env_path_rules = os.getenv("ENV_PATH_RULES")
env_path_recall = os.getenv("ENV_PATH_RECALL")
env_path_bdg = os.getenv("ENV_PATH_BDG")
env_path_gvg = os.getenv("ENV_PATH_GVG")
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
                rules.save_guild(guild)

    
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if self.user.id == payload.user_id:
            return
        
        await recall.check_reaction_add(payload)
        await rules.check_reaction_add(payload)

    async def on_message(self, message: discord.Message):
        if message.author.id == self.user.id:
            return
        # Gestion attente image
        handled = await bdg.handle_message(message)
        if handled:
            return
        
        if rules.wait_message and message.channel == rules.channel_wait:
            await rules.message_rules(message)
    
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.user.id:
            return
        
        await rules.check_reaction_remove(payload)

client = aclient()
tree = app_commands.CommandTree(client)
recall = Recall(client, env_path_recall)
rules = Rules(client, env_path_rules)
bdg = Bdg(client, env_path_bdg)
gvg = Gvg(client, env_path_gvg, "./ressources/heros.json")
tree.add_command(recall, guild=guild_object)
tree.add_command(rules, guild=guild_object)
tree.add_command(bdg, guild=guild_object)
tree.add_command(gvg, guild=guild_object)
tree.add_command(RenameAll(), guild=guild_object)
tree.add_command(UnrenameAll(), guild=guild_object)
client.run(TOKEN)

