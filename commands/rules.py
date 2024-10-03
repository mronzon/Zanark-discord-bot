from discord import app_commands
import discord
import json

class Rules(app_commands.Group):
    """Manage the command related to the rules"""
    def __init__(self, client: discord.Client, env_path: str):
        super().__init__()
        self.bot = client
        self.env_path = env_path
        self.guild: discord.Guild = None
        self.channel = None
        self.env = None
        self.wait_message = False
        self.channel_wait = None
        
        with open(self.env_path, 'r', encoding='UTF-8') as file:
            self.env = json.load(file)
        

    @app_commands.command(name="salon", description="Permet d'indiquer le salon textuel dans lequel les règles sont.")
    async def salon(self, interaction: discord.Interaction, channel: discord.TextChannel):  
        if not self._check_roles(interaction.user):
            await interaction.response.send_message("Vous n'avez pas le role nécessaire pour lancer cette commande", ephemeral=True)
            return
        try:
            await interaction.response.send_message("Le channel a été mis à jour")
            self.channel = channel
            self.env["rules_channel"] = channel.id
            self._save_env()
        except:
            await interaction.response.send_message("Veuillez me donner un salon textuel seulement.")
    
    @app_commands.command(name="text", description="Permet de mettre un texte dans le channel règles.")
    async def text(self, interaction: discord.Interaction):
        if not self._check_roles(interaction.user):
            await interaction.response.send_message("Vous n'avez pas le role nécessaire pour lancer cette commande", ephemeral=True)
            return
        if self.channel == None:
            await interaction.response.send_message("Aucun salon textuel a été choisi !", ephemeral=True)
            return
        await interaction.response.send_message("Veuillez donner le texte :")
        
        self.wait_message = True
        self.channel_wait = interaction.channel
    
    @app_commands.command(name="roles", description="Permet d'associer un role avec une réaction.")
    async def roles(self, interaction: discord.Interaction, reaction: str, role: discord.Role):
        if not self._check_roles(interaction.user):
            await interaction.response.send_message("Vous n'avez pas le role nécessaire pour lancer cette commande", ephemeral=True)
            return
        if self.channel == None:
            await interaction.response.send_message("Aucun salon textuel a été choisi !", ephemeral=True)
            return
        try:
            good = False
            async for message in self.channel.history(limit=50):
                if message.author == self.bot.user:
                    await message.add_reaction(reaction)
                    good = True
                    break
            if good:
                await interaction.response.send_message(f"La reaction {reaction} est associé au role {role}")
                self.env["reaction_role"].append({"role": role.name, "reaction": reaction})
                self._save_env()
            else:
                await interaction.response.send_message(f"Aucun message n'a été posté de la part du bot dans le salon {self.channel}")
        except:
            await interaction.response.send_message("Veuillez ajouter un role avec la mention !")
        

    @app_commands.command(name="admin", description="Permet d'ajouter un role admin")
    async def add_role_admin(self, interaction: discord.Interaction, role: discord.Role):
        if not self._check_roles(interaction.user):
            await interaction.response.send_message("Vous n'avez pas les permissions spéciaux pour lancer cette commande", ephemeral=True)
            return
        self.env["roles"].append(role.name)
        self._save_env()
        await interaction.response.send_message("Le role admin a été mis à jour")


    async def message_rules(self, message: discord.Message):
        if not self._check_roles(message.author):
            return
        message = await self.channel.send(message.content)
        self.env["text_id"] = message.id
        self._save_env()
        self.wait_message = False
        self.channel_wait = None
        for role_emoji in self.env["reaction_role"]:
            await message.add_reaction(role_emoji["reaction"])

    async def check_reaction_add(self, payload: discord.RawReactionActionEvent):
        if self.channel == None:
            return
        if payload.channel_id == self.channel.id and payload.message_id == self.env["text_id"]:
            for role_emoji in self.env["reaction_role"]:
                if role_emoji["reaction"] == "" or role_emoji["reaction"] == str(payload.emoji):
                    user = discord.utils.get(self.bot.get_all_members(), id=payload.user_id)
                    role = discord.utils.get(self.guild.roles, name=role_emoji["role"])
                    await user.add_roles(role)
    
    async def check_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if self.channel == None:
            return
        if payload.channel_id == self.channel.id and payload.message_id == self.env["text_id"]:
            for role_emoji in self.env["reaction_role"]:
                if role_emoji["reaction"] == "" or role_emoji["reaction"] == str(payload.emoji):
                    user = discord.utils.get(self.bot.get_all_members(), id=payload.user_id)
                    role = discord.utils.get(self.guild.roles, name=role_emoji["role"])
                    await user.remove_roles(role)

    def save_guild(self, guild: discord.Guild):
        self.guild = guild
        if guild.rules_channel != None:
            self.channel = guild.rules_channel
        else:
            self._get_env()
    def _get_env(self):
        if self.env["rules_channel"] != 0:
            self.channel = self.bot.get_channel(self.env["rules_channel"])
    
    def _save_env(self):
        with open(self.env_path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.env, indent=4, ensure_ascii=False))
    
    def _check_roles(self, user: discord.User | discord.Member) -> bool:
        if user.guild_permissions.administrator:
            return True
        for role in self.env["roles"]:
            for role_user in user.roles:
                if role == role_user.name:
                    return True
        return False

