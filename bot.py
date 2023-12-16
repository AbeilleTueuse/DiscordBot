# bot.py
import os

import nextcord
from nextcord.ext import commands
from nextcord.interactions import Interaction
from nextcord import Embed
from dotenv import load_dotenv
import asyncio

from event.game_event import GameEvent
from sound.musics import Musics

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [1137767167413211216]


class MyBot(commands.Bot):
    FFMPEG_EXECUTABLE = r"ffmpeg\bin\ffmpeg.exe"

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.voice_channel = None
        self.game_event = GameEvent()
        self.musics = Musics()
        

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")

        # general_channel = discord.utils.get(self.guild.channels, name="général")

        # if general_channel:
        #     await general_channel.send("Hello mother fucker")
        # else:
        #     print("Le salon général n'a pas été trouvé.")

    async def detect_game_event(self):
        screen = self.game_event.get_screen()

        if self.game_event.boss_detection.play_music(screen):
            await bot.play_music()

        event = self.game_event.read_message.image_to_game_event(screen)

        if event is not None:
            if (
                (event == "abeille_death")
                or (event == "pierrick_death")
                or (event == "etchebest_death")
                or (event == "player_death")
            ):
                await bot.play_music("il_est_decede")

            elif event == "pierrick_invocation":
                await bot.play_music("les_meilleurs")

            elif (
                (event == "abeille_invocation")
                or (event == "etchebest_invocation")
                or (event == "player_invocation")
            ):
                await bot.play_music()

            elif event == "fire_alight":
                await bot.play_music("lotr_one_ring")

            elif event == "boss_begin":
                self.game_event.boss_detection.boss_is_alive = True
                await bot.play_music()

            else:
                print(f"Event {event} isn't added.")

    async def play_music(self, audio_name: str = None):
        print(self.voice_channel)
        if self.voice_channel is None:
            return

        if len(self.voice_channel.channel.members) == 1:
            return

        if self.voice_channel.is_playing():
            return

        audio_path = self.musics.path(audio_name)

        self.voice_channel.play(
            nextcord.FFmpegPCMAudio(
                source=audio_path
            ),
        )

    async def connect_to_voice_channel(
        self, user: nextcord.member.Member
    ):
        if user.voice is None or user.voice.channel is None:
            return
        
        if self.voice_channel is None:
            self.voice_channel = await user.voice.channel.connect()

    async def disconnect_to_voice_channel(self):
        if self.voice_channel is None:
            return

        await self.voice_channel.disconnect()
        self.voice_channel = None


bot = MyBot()


@bot.slash_command(name="lancer", description="Joue des sons selon les évènements du jeu.", guild_ids=GUILD_IDS)
async def start(interaction: Interaction):
    if not bot.is_running:
        bot.is_running = True

        await bot.connect_to_voice_channel(interaction.user)
        await bot.play_music()

        while bot.is_running:
            await bot.detect_game_event()
            await asyncio.sleep(1)


@bot.slash_command(name="rejoindre", description="Demande au bot de te rejoindre sur ton salon vocal.", guild_ids=GUILD_IDS)
async def join_voice_channel(interaction: Interaction):
    if bot.voice_channel is not None:
        return

    await bot.connect_to_voice_channel(interaction.user)
    await bot.play_music()


@bot.slash_command(name="stop", description="Arrête l'analyse du jeu et déconnecte le bot du salon vocal.", guild_ids=GUILD_IDS)
async def disconnect_to_voice_channel(interaction):
    bot.is_running = False
    await bot.play_music()
    await bot.disconnect_to_voice_channel()


@bot.slash_command(name="aléatoire", description="Joue un son au hasard.", guild_ids=GUILD_IDS)
async def random_sound(interaction: Interaction):
    await bot.connect_to_voice_channel(interaction.user)
    await bot.play_music()


@bot.slash_command(name="jouer", description="Joue le son choisi.", guild_ids=GUILD_IDS)
async def play_sound(interaction: Interaction, sound_name: str):
    await bot.connect_to_voice_channel(interaction.user)
    await bot.play_music(sound_name)


@bot.slash_command(name="ajouter", description="Ajoute le son en pièce-jointe.", guild_ids=GUILD_IDS)
async def add_sound(interaction: Interaction):
    if len(interaction.message.attachments) == 0:
        await interaction.send("Faut mettre le fichier avec la commande connard")
        return

    attachment = interaction.message.attachments[0]
    filename = attachment.filename

    if filename.endswith(bot.musics.ALLOWED_EXTENSION):
        if filename.split(".")[0] in bot.musics.sound_files:
            await interaction.send(f"Le fichier {filename} est déjà présent.")

        else:
            await attachment.save(os.path.join(bot.musics.SOUND_PATH, filename))
            bot.musics.add(filename)
            await interaction.send(f"Le fichier {filename} a été ajouté à la liste des sons.")

    else:
        await interaction.send(
            f"Seules les extensions {bot.musics.ALLOWED_EXTENSION} sont autorisées débile"
        )


@bot.slash_command(name="liste_sons", description="Affiche la liste des sons disponibles avec leur probabilité.", guild_ids=GUILD_IDS)
async def sound_list(interaction: Interaction):
    embed = Embed(
        title="Liste des sons",
        color=0x00ff00
    )

    names = bot.musics.names()
    weights = bot.musics.prob()

    embed.add_field(name="Nom", value="\n".join(names), inline=True)
    embed.add_field(name="Poids", value="\n".join(weights), inline=True)

    await interaction.send(embed=embed)
    

@bot.slash_command(name="changer_poids", description="Change la probabilité d'apparaître d'un son.", guild_ids=GUILD_IDS)
async def change_weight(interaction: Interaction, name: str, weight: str | float):
    if name not in bot.musics.sound_files:
        embed = Embed(
            title="Erreur",
            description=f"Le son **{name}** n'est pas présent dans la liste des sons. Utilisez la commande **/sound_list** pour voir la liste    des sons disponibles.",
            color=0xFF0000
        )
    else:
        try:
            weight = float(weight.replace(",", "."))
        except ValueError:
            embed = Embed(
                title="Erreur",
                description=f"**{weight}** n'est pas un poids valide, tu dois mettre un nombre enculé.",
                color=0xFF0000
            )
        else:
            bot.musics.change_weight(name, weight)
            embed = Embed(
                title="Changement de poids",
                description=f"Le poids du son **{name}** est maintenant de **{str(weight).replace(".", ",")}**.",
                color=0x00ff00
            )

    await interaction.send(embed=embed)


@bot.event
async def on_voice_state_update(
    member: nextcord.member.Member,
    before: nextcord.member.VoiceState,
    after: nextcord.member.VoiceState,
):
    if member.id == bot.application_id:
        return

    if before.channel is None and after.channel is not None:
        await bot.connect_to_voice_channel(member)
        if after.channel.id == bot.voice_channel.channel.id:
            await bot.play_music()
    elif (
        before.channel is not None
        and after.channel is None
        and bot.voice_channel is not None
    ):
        if before.channel.id == bot.voice_channel.channel.id:
            await bot.play_music()


bot.run(TOKEN)
