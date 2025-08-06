from discord import app_commands, Interaction

class RenameAll(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="rename_all_shek",
            description="Renomme tous les membres en Shek",
            callback=self.rename_all_shek
        )

    async def rename_all_shek(self, interaction: Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Commande à utiliser sur un serveur.", ephemeral=True)
            return
        count = 0
        for member in guild.members:
            try:
                await member.edit(nick="Shek")
                count += 1
            except Exception:
                continue
        await interaction.response.send_message(f"{count} membres renommés en Shek.")


class UnrenameAll(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="unrename_all_shek",
            description="Réinitialise le pseudo de tous les membres",
            callback=self.unrename_all_shek
        )

    async def unrename_all_shek(self, interaction: Interaction):
        await interaction.response.defer()
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("Commande à utiliser sur un serveur.", ephemeral=True)
            return
        count = 0
        for member in guild.members:
            try:
                await member.edit(nick=None)
                count += 1
            except Exception:
                continue
        await interaction.followup.send(f"{count} pseudos réinitialisés.")