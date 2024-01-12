from discord import app_commands
import discord
import json

class Rules(app_commands.Group):
    """Manage the command related to the rules"""
    def __init__(self, client: discord.Client, env_path: str):
        super().__init__()
        self.bot = client
        self.channel = None
        self.env_path = env_path
        self.env = None
        self.wait_message = False
        self.channel_wait = None
        with open(self.env_path, 'r', encoding='UTF-8') as file:
            self.env = json.load(file)
        

    @app_commands.command(name="salon", description="Permet d'indiquer le salon textuel dans lequel les règles sont.")
    async def salon(self, interaction: discord.Interaction, channel: str):  
        try:
            channel_id = channel.split("#")[1][:-1]
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            await interaction.response.send_message("Le channel a été mis à jour")
            self.channel = channel
            self.env["rules_channel"] = channel_id
            self._save_env()
        except:
            await interaction.response.send_message("Veuillez me donner un salon textuel seulement.")
    
    @app_commands.command(name="text", description="Permet de mettre un texte dans le channel règles.")
    async def text(self, interaction: discord.Interaction):
        if self.channel == None:
            await interaction.response.send_message("Aucun salon textuel a été choisi !")
            return
        await interaction.response.send_message("Veuillez donner le texte :")
        self.wait_message = True
        self.channel_wait = interaction.channel

    async def message_rules(self, message: discord.Message):
        await self.channel.send(message.content)
        self.wait_message = False
        self.channel_wait = None

    def _get_env(self):
        if self.env["rules_channel"] != 0:
            self.channel = self.bot.get_channel(self.env["rules_channel"])
    
    def _save_env(self):
        with open(self.env_path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.env, indent=4, ensure_ascii=False))
    

        

