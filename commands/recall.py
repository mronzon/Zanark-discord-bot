import threading
import time
from discord import app_commands
import discord
import json
import datetime
import asyncio

day_week = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

class Recall(app_commands.Group):
  """Manage the command related to the bdg"""
  def __init__(self, client: discord.Client, env_path):
    super().__init__()
    self.bot = client
    self.env = None
    self.thread = None
    self.category = None
    self.role = None
    self.names = ""
    self.start = False
    self.env_path = env_path
    with open(self.env_path, 'r', encoding='UTF-8') as file:
      self.env = json.load(file)
    
  @app_commands.command(name="bdg", description="Permet de mettre en place un rappel automatique pour le boss de guild")
  async def bdg(self, interaction: discord.Interaction, names: str):
    if not self._check_roles(interaction.user):
      await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour lancer cette commande", ephemeral=True)
      return
    if self.role == None:
      await interaction.response.send_message("Vous n'avez pas configurer le rôle.", ephemeral=True)
      return
    if self.env["reaction"] == "":
      await interaction.response.send_message("Veuillez renseigner une réaction avant de lancer cette commande", ephemeral=True)
      return
    if self.env["msg"] == "":
      await interaction.response.send_message("Veuillez renseigner un message avant de lancer cette commande", ephemeral=True)
      return
    if self.category != None:
      for day in day_week:
        name = f"rappel-{day}"
        for chan in self.category.channels:
          if chan.name == name:
            await chan.delete()
        
      now = datetime.datetime.now()
      day = day_week[now.weekday()]
      
      channel = await interaction.guild.create_text_channel(name=f"rappel-{day}", category=self.category)
      if channel != None:
        ids = names.split(" ")
        for id_user in ids:
          if not '@' in id_user:
            continue
          id_user = id_user.split("@")[1][:-1]
          try:
            user = interaction.guild.get_member(int(id_user))
          except:
            await interaction.response.send_message("Veuillez mentionner une bonne personne.", ephemeral=True)
            return
          if user != None:
            await user.add_roles(self.role)
        self.channel = channel
        self.names = names
        self.start = True
        self.bot.loop.create_task(self.send_message_periodically())
        await interaction.response.send_message("Rappel automatique lancé", ephemeral=True)
      else:
        await interaction.response.send_message("Impossible de créer le calon, voir avec TeckDown", ephemeral=True)
    else:
      await interaction.response.send_message("Veuillez choisir une catégorie avant de faire cette commande.", ephemeral=True)
    
  @app_commands.command(name="setcategory", description="Permet de choisir la catégorie dans laquelle les channels vont être créés")
  async def setcategory(self, interaction: discord.Interaction, category_id: str):
    if not self._check_roles(interaction.user):
      await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour lancer cette commande", ephemeral=True)
      return
    try:
      category = discord.utils.get(interaction.guild.categories, id=int(category_id))
      await interaction.response.send_message("La catégorie a été mise à jour")
      self.category = category
      self.env["category"] = category_id
      self._save_env()
    except:
      await interaction.response.send_message("Veuillez me donner un id d'une catégorie.", ephemeral=True)
  
  @app_commands.command(name="setrole", description="Ajouter le role que les personnes vont avoir. Juste donner le nom du rôle")
  async def setRole(self, interaction: discord.Interaction, role: discord.Role):
    if not self._check_roles(interaction.user):
      await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour lancer cette commande", ephemeral=True)
      return
    try:
      self.role = role
      self.env["role"] = role.id
      self._save_env()
      await interaction.response.send_message("Le role a été mise à jour")
    except:
      await interaction.response.send_message("Pas de rôle donné, veuillez réessayer.", ephemeral=True)

  @app_commands.command(name="reaction", description="Ajouter la réaction qu'ils vont devoir mettre pour arrêter le rappel")
  async def reaction(self, interaction: discord.Interaction, reaction: str):
    if not self._check_roles(interaction.user):
      await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour lancer cette commande", ephemeral=True)
      return
    self.env["reaction"] = reaction
    self._save_env()
    await interaction.response.send_message(f"La réaction {reaction} a bien été enregistré")

  @app_commands.command(name="msg", description="Ajouter du message personnalisé (/mention/ doit être obligatoirement être dans le message)")
  async def msg(self, interaction: discord.Interaction, msg: str):
    if not self._check_roles(interaction.user):
      await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour lancer cette commande", ephemeral=True)
      return
    if "/mention/" not in msg:
      await interaction.response.send_message("Veuillez mettre _mention_ dans le message !", ephemeral=True)
      return
    self.env["msg"] = msg
    self._save_env()
    await interaction.response.send_message(f"Le message a bien été enregistré")

  @app_commands.command(name="seemsg", description="Voir le message personnalisé qui a été mis.")
  async def msg(self, interaction: discord.Interaction):
    if not self._check_roles(interaction.user):
      await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour lancer cette commande", ephemeral=True)
      return
    await interaction.response.send_message(self.env["msg"])

  @app_commands.command(name="stop", description="Permet de stopper l'envoie de message automatique")
  async def stop(self, interaction: discord.Interaction):
    if not self.start:
      await interaction.response.send_message("Pas de message automatique de lancé", ephemeral=True)
      return
    self.start = False
    await interaction.response.send_message("Arret")
    
  async def send_message_periodically(self):
    while self.start:
      if not '@' in self.names:
        self.start = False
        return
      now = datetime.datetime.now()
      await self.bot.wait_until_ready()
      message = await self.channel.send(self.env['msg'].replace("/mention/", self.names))
      if message != None:
        await message.add_reaction(self.env['reaction'])
      now = datetime.datetime.now()
      day = day_week[now.weekday()]
      time_last = datetime.time(9, 45, 0)
      time_first = datetime.time(9, 30, 0)
      if day == "vendredi":
        time_last = datetime.time(9, 15, 0)
        time_first = datetime.time(9, 0, 0)
      if now.time() > time_first and time_last > now.time():
        target_time = datetime.datetime.combine(now.date(), time_last)
        second_until_target = (target_time - now).total_seconds()
      elif now.time() > time_last:
        return
      else:
        target_time = datetime.datetime.combine(now.date(), time_first)
        second_until_target = (target_time - now).total_seconds()
      await asyncio.sleep(second_until_target)

  async def check_reaction_add(self, payload: discord.RawReactionActionEvent):
    for chan in self.category.channels:
      if chan.id == payload.channel_id:
        if str(payload.emoji) == self.env["reaction"]:
          user = discord.utils.get(self.bot.get_all_members(), id=payload.user_id)
          await user.remove_roles(self.role)
          tmp = ""
          for name in self.names.split(" "):
            if not '@' in name or str(user.id) in name:
              continue
            tmp += name + " "
          if tmp != "":
            tmp = tmp[:-1]
          self.names = tmp


  def _get_env(self, guild: discord.Guild):
    if self.env["category"] != 0:
      self.category = discord.utils.get(guild.categories, id=int(self.env["category"]))
    if self.env["role"] != 0:
      self.role = discord.utils.get(guild.roles, id=int(self.env["role"]))

    
  def _save_env(self):
    with open(self.env_path, 'w', encoding='UTF-8') as file:
      file.write(json.dumps(self.env, indent=4, ensure_ascii=False))
  
  def _check_roles(self, user: discord.User | discord.Member) -> bool:
    for role in self.env["roles"]:
      for role_user in user.roles:
        if role == role_user.name:
          return True
    return False
