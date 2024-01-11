from discord import app_commands
import discord


class Rules(app_commands.Group):
    """Manage the command related to the rules"""
    def __init__(self, client: discord.Client):
        super().__init__()
        self.bot = client

    @app_commands.command(name="setchannel", description="Permet d'indiquer le channel dans lequel les règles sont.")
    async def essai(self, interaction: discord.Interaction):
        print()
        await interaction.response.send_message("Hello !")

