from discord import app_commands, Interaction

class RenameAll(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="rename_all_shek",
            description="Renomme tous les membres en Shek",
            callback=self.rename_all_shek
        )

    async def rename_all_shek(self, interaction: Interaction):
        await interaction.response.defer()
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("Commande à utiliser sur un serveur.", ephemeral=True)
            return
        members = list(guild.members)
        total = len(members)
        count = 0
        progress_msg = await interaction.followup.send(f"Renommage en cours... 0/{total}")
        for member in members:
            try:
                await member.edit(nick="Shek")
                count += 1
            except Exception:
                continue
            if count % 10 == 0 or count == total:
                await progress_msg.edit(content=f"Renommage en cours... {count}/{total}")
        await progress_msg.edit(content=f"{count} membres renommés en Shek.")



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
        members = list(guild.members)
        total = len(members)
        count = 0
        progress_msg = await interaction.followup.send(f"Réinitialisation en cours... 0/{total}")
        for member in members:
            try:
                await member.edit(nick=None)
                count += 1
            except Exception:
                continue
            if count % 10 == 0 or count == total:
                await progress_msg.edit(content=f"Réinitialisation en cours... {count}/{total}")
        await progress_msg.edit(content=f"{count} pseudos réinitialisés.")