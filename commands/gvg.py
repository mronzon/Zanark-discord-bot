import os
import json
import discord
from discord import app_commands

class Gvg(app_commands.Group):
    def __init__(self, client, env_path):
        super().__init__()
        self.client = client
        self.env_path = env_path
        self.waiting = {}  # (user_id, channel_id): interaction
        self.data = []
        self.env = None
        self.possible_hero = []


        with open(self.env_path, 'r', encoding='UTF-8') as file:
            self.env = json.load(file)
        self.data_path = os.path.join("ressources", "data_gvg.json")
        if os.path.exists(self.data_path):
          with open(self.data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        else:
          self.data = []
        
        self.get_possible_hero()


    @app_commands.command(name="salon", description="Permet d'indiquer le salon textuel dans lequel les compos sont envoyées.")
    async def salon(self, interaction: discord.Interaction, channel: discord.TextChannel):  
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Vous n'avez pas le role nécessaire pour lancer cette commande", ephemeral=True)
            return
        try:
            await interaction.response.send_message("Le channel a été mis à jour")
            self.env["gvg_channel"] = channel.id
            self._save_env()
        except:
            await interaction.response.send_message("Veuillez me donner un salon textuel seulement.")

    @app_commands.command(name="adddata", description="Permet de rajouter les données récupéré des précédentes guerre de guilde.")
    async def addData(self, interaction: discord.Interaction, json_file: discord.Attachment):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Vous n'avez pas le role nécessaire pour lancer cette commande", ephemeral=True)
            return
        if not json_file.filename.endswith(".json"):
          await interaction.response.send_message("Seuls les fichiers `.json` sont acceptés.", ephemeral=True)
          return
        try:
          # Download the file to a temporary location
          temp_path = f"tmp/temp_{json_file.filename}"
          await json_file.save(temp_path)
          with open(temp_path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
          os.remove(temp_path)
          if not (
            isinstance(new_data, list) and
            all(
              isinstance(item, dict) and
              set(item.keys()) == {
                "attack", "attack_relic", "defense", "defense_relic", "victory", "situation"
              } and
              isinstance(item["attack"], str) and
              isinstance(item["attack_relic"], str) and
              isinstance(item["defense"], str) and
              isinstance(item["defense_relic"], str) and
              isinstance(item["victory"], bool) and
              isinstance(item["situation"], str)
              for item in new_data
            )
          ):
            await interaction.response.send_message(
              "Le fichier JSON doit être une liste d'objets avec les champs requis.", ephemeral=True
            )
            return
          self.data = self.data + new_data
          with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
          self.get_possible_hero()
          await interaction.response.send_message(f"Les données provenant du fichier {json_file.filename} ont été ajoutées avec succès.")
        except Exception as e:
          await interaction.response.send_message(f"Erreur lors de l'ajout des données : {e}", ephemeral=True)
    
    @app_commands.command(name="getdata", description="Permet de récupéré les données présent au sein du bot.")
    async def getData(self, interaction: discord.Interaction):
      if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas le role nécessaire pour lancer cette commande", ephemeral=True)
        return
      data_path = os.path.join("ressources", "data_gvg.json")
      if os.path.exists(data_path):
        await interaction.response.send_message(
          file=discord.File(data_path)
        )
      else:
        await interaction.response.send_message(
          "Le fichier 'ressources/data_gvg.json' n'existe pas.",
          ephemeral=True
        )

    @app_commands.command(name="bestteam", description="Sélectionnez 5 héros pour obtenir la meilleure équipe correspondante.")
    async def getbestteam(self, interaction: discord.Interaction):
        if not self.env["gvg_channel"] == interaction.channel.id:
            await interaction.response.send_message("Vous n'êtes pas dans le bon channel pour lancer cette commande", ephemeral=True)
            return
        class HeroSelect(discord.ui.Select):
            def __init__(self, heroes, idx, selected_heroes, row):
                options = [
                    discord.SelectOption(label=hero, value=hero, default=(hero in selected_heroes))
                    for hero in heroes
                ]
                super().__init__(
                    placeholder=f"Sélectionnez des héros (menu {idx+1})",
                    min_values=0,
                    max_values=min(5, len(options)),
                    options=options,
                    custom_id=f"hero_select_{idx}",
                    row=row
                )

        class HeroSelectView(discord.ui.View):
            def __init__(self, all_heroes, parent):
                super().__init__(timeout=120)
                self.all_heroes = all_heroes
                self.selected_heroes = set()
                self.selects = []
                self.parent = parent  # Référence à l'instance de Gvg
                self.hero_chunks = [all_heroes[i:i+25] for i in range(0, len(all_heroes), 25)]
                for idx, chunk in enumerate(self.hero_chunks):
                    row = idx % 5  # 5 menus max par ligne
                    select = HeroSelect(chunk, idx, self.selected_heroes, row)
                    select.callback = self.make_callback(idx)
                    self.selects.append(select)
                    self.add_item(select)
                # Place le bouton sur la dernière ligne disponible
                self.submit_button = self.SubmitButton(self, row=min(len(self.hero_chunks), 4))
                self.add_item(self.submit_button)
            
            def make_callback(self, idx):
                async def callback(interaction_select):
                    all_selected = set()
                    for i, select in enumerate(self.selects):
                        if i == idx:
                            all_selected.update(interaction_select.data['values'])
                        else:
                            all_selected.update(select.values)
                    self.selected_heroes = all_selected
                    for i, select in enumerate(self.selects):
                        for option in select.options:
                            option.default = option.value in self.selected_heroes
                    await interaction_select.response.defer()  # Ajouté pour éviter l'échec d'interaction
                return callback

            class SubmitButton(discord.ui.Button):
                def __init__(self, view, row):
                    super().__init__(style=discord.ButtonStyle.success, label="Valider", row=row)
                    self.view_ref = view
                async def callback(self, interaction_button):
                    if len(self.view_ref.selected_heroes) != 5:
                        await interaction_button.response.send_message(
                            "Vous devez sélectionner exactement 5 héros.", ephemeral=True
                        )
                        return
                    selected_heroes = set(self.view_ref.selected_heroes)
                    matching_entries = []
                    for entry in self.view_ref.parent.data:
                        defense_heroes = set(entry["defense"].split("|"))
                        if defense_heroes == selected_heroes:
                            matching_entries.append(entry)
                    if not matching_entries:
                        await interaction_button.response.edit_message(
                            content="Aucune équipe trouvée pour cette défense.", view=None
                        )
                        return
                    from collections import defaultdict
                    attack_stats = defaultdict(lambda: {"win": 0, "total": 0, "example": None, "relics": set()})
                    for entry in matching_entries:
                        attack_heroes = entry["attack"].split("|")
                        attack_key = "|".join(sorted(attack_heroes))
                        if entry["victory"]:
                            attack_stats[attack_key]["win"] += 1
                        attack_stats[attack_key]["total"] += 1
                        if attack_stats[attack_key]["example"] is None:
                            attack_stats[attack_key]["example"] = entry["attack"]
                        # Ajout des reliques
                        attack_stats[attack_key]["relics"].add(entry.get("attack_relic", ""))
                    # Calculer le winrate et filtrer > 50%
                    attack_list = []
                    for attack_key, stats in attack_stats.items():
                        winrate = stats["win"] / stats["total"] if stats["total"] > 0 else 0
                        if winrate > 0.5:
                            attack_list.append({
                                "attack": stats["example"],
                                "win": stats["win"],
                                "total": stats["total"],
                                "winrate": winrate,
                                "relics": stats["relics"]
                            })
                    if not attack_list:
                        await interaction_button.response.edit_message(
                            content="Aucune équipe d'attaque avec un winrate > 50% pour cette défense.", view=None
                        )
                        return
                    # Trier par nombre d'apparitions puis winrate
                    attack_list.sort(key=lambda x: (x["total"], x["winrate"]), reverse=True)
                    # Menu winrate
                    winrate_options = [50, 60, 70, 80, 90, 100]
                    class WinrateSelect(discord.ui.Select):
                        def __init__(self):
                            options = [
                                discord.SelectOption(label=f">= {w}%", value=str(w)) for w in winrate_options
                            ]
                            super().__init__(
                                placeholder="Filtrer par winrate...",
                                min_values=1,
                                max_values=1,
                                options=options
                            )
                        async def callback(self, interaction_select):
                            seuil = int(self.values[0])
                            filtered = [a for a in attack_list if a["winrate"] >= seuil/100]
                            # Générer le message texte formaté
                            title = f"🔥 Équipes d'attaque avec winrate ≥ {seuil}% contre\n{ ' | '.join(selected_heroes) }\n"
                            msg = title
                            if not filtered:
                                msg += f"\nAucune équipe d'attaque avec un winrate ≥ {seuil}% pour cette défense."
                            else:
                                for a in filtered:
                                    relics_str = ', '.join(sorted(r for r in a['relics'] if r))
                                    attack_line = f"📌 {a['attack']}"
                                    if relics_str:
                                        attack_line += f" (reliques: {relics_str})"
                                    winrate_str = f"🏆 {a['win']}/{a['total']} victoires — {a['winrate']*100:.1f}%"
                                    msg += f"\n{attack_line}\n{winrate_str}\n"
                            # Supprimer les anciens followup
                            if not hasattr(self.view, 'followup_messages'):
                                self.view.followup_messages = []
                            for old_msg in self.view.followup_messages:
                                try:
                                    await old_msg.delete()
                                except Exception:
                                    pass
                            self.view.followup_messages = []
                            # Découper si trop long
                            def split_message(text, max_len=2000):
                                parts = []
                                while len(text) > max_len:
                                    idx = text.rfind('\n', 0, max_len)
                                    if idx == -1:
                                        idx = max_len
                                    parts.append(text[:idx])
                                    text = text[idx:].lstrip('\n')
                                if text:
                                    parts.append(text)
                                return parts
                            msgs = split_message(msg)
                            await interaction_select.response.edit_message(content=msgs[0], view=self.view)
                            for m in msgs[1:]:
                                sent = await interaction_select.followup.send(m)
                                self.view.followup_messages.append(sent)
                    # Affichage initial (winrate > 50%)
                    seuil = 50
                    filtered = attack_list[:5]
                    title = f"🔥 Équipes d'attaque avec winrate > 50% contre\n{ ' | '.join(selected_heroes) }\n"
                    msg = title
                    if not filtered:
                        msg += f"\nAucune équipe d'attaque avec un winrate > 50% pour cette défense."
                    else:
                        for a in filtered:
                            relics_str = ', '.join(sorted(r for r in a['relics'] if r))
                            attack_line = f"📌 {a['attack']}"
                            if relics_str:
                                attack_line += f" (reliques: {relics_str})"
                            winrate_str = f"🏆 {a['win']}/{a['total']} victoires — {a['winrate']*100:.1f}%"
                            msg += f"\n{attack_line}\n{winrate_str}\n"
                    if len(attack_list) > 5:
                        msg += f"\n...et {len(attack_list)-5} autres. Utilisez le menu pour filtrer."
                    def split_message(text, max_len=2000):
                        parts = []
                        while len(text) > max_len:
                            idx = text.rfind('\n', 0, max_len)
                            if idx == -1:
                                idx = max_len
                            parts.append(text[:idx])
                            text = text[idx:].lstrip('\n')
                        if text:
                            parts.append(text)
                        return parts
                    msgs = split_message(msg)
                    view = discord.ui.View()
                    view.add_item(WinrateSelect())
                    await interaction_button.response.edit_message(
                        content=msgs[0],
                        view=view
                    )
                    for m in msgs[1:]:
                        await interaction_button.followup.send(m)
        view = HeroSelectView(self.possible_hero, self)
        await interaction.response.send_message(
            f"Veuillez sélectionner au maximum 5 héros",
            view=view
        )


    def _save_env(self):
        with open(self.env_path, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(self.env, indent=4, ensure_ascii=False))
    
    def get_possible_hero(self):
        for elt in self.data:
            heros = elt["attack"].split('|') + elt["defense"].split('|') 
            for hero in heros:
                if hero == "None":
                    continue
                if not hero in self.possible_hero:
                    self.possible_hero.append(hero)