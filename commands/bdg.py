import os
import json
import discord
from discord import app_commands
from src.bdg_scrapper import get_scores

class Bdg(app_commands.Group):
    def __init__(self, client, env_path):
        super().__init__()
        self.client = client
        self.env_path = env_path
        self.waiting = {}  # (user_id, channel_id): interaction
        self.env = None

        with open(self.env_path, 'r', encoding='UTF-8') as file:
            self.env = json.load(file)


    @app_commands.command(name="salon", description="Permet d'indiquer le salon textuel dans lequel les règles sont.")
    async def salon(self, interaction: discord.Interaction, channel: discord.TextChannel):  
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Vous n'avez pas le role nécessaire pour lancer cette commande", ephemeral=True)
            return
        try:
            await interaction.response.send_message("Le channel a été mis à jour")
            self.env["bdg_channel"] = channel.id
            self._save_env()
        except:
            await interaction.response.send_message("Veuillez me donner un salon textuel seulement.")

    @app_commands.command(name="scores", description="Permet de récupérer sous forme de texte, les scores provenant de screenshot.")
    async def image_command(self, interaction: discord.Interaction):
        """
        Prépare à recevoir une image dans le prochain message de l'utilisateur dans ce salon.
        """
        if not self.env["bdg_channel"] == interaction.channel.id:
            await interaction.response.send_message("Vous n'êtes pas dans le bon channel pour lancer cette commande", ephemeral=True)
            return

        self.waiting[(interaction.user.id, interaction.channel_id)] = interaction
        await interaction.response.send_message("Envoyez maintenant l'image dans ce salon.")

    async def handle_message(self, message: discord.Message):
        key = (message.author.id, message.channel.id)
        if key not in self.waiting:
            return False
        interaction = self.waiting.pop(key)
        if not message.attachments:
            await message.channel.send("Aucune image détectée. Veuillez réessayer la commande et envoyer une image.")
            return True
        attachment = message.attachments[0]
        results = []
        for attachment in message.attachments:
            if not attachment.content_type or not attachment.content_type.startswith("image"):
                await message.channel.send("Le fichier n'est pas une image.")
                return True
            os.makedirs("tmp", exist_ok=True)
            path = os.path.join("tmp", attachment.filename)
            try:
                await attachment.save(path)
                scores_names = get_scores(path)
                for elt in scores_names:
                    if not elt in results:
                        results.append(elt)
                os.remove(path)
            except Exception as e:
                await message.channel.send(f"Erreur lors de la lectures: {e}")
        results.sort(key=lambda x: x[1])
        await message.channel.send(f"Au sein des images, nous avons les scores suivant :")
        tmp = ""
        only_score = ""
        results.reverse()
        for name, score in results:
            tmp += f"{name}: {score}\n"
            only_score += f"{score}\n"
        with open("tmp/scores.txt", "w", encoding="utf-8") as f:
            f.write(only_score)
        
        await message.channel.send(content=tmp, file=discord.File("tmp/scores.txt"))
        return True
    
    def _save_env(self):
        with open(self.env_path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.env, indent=4, ensure_ascii=False))