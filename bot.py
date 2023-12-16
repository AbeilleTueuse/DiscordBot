# import os

# import nextcord
# from nextcord.ext import commands
# from nextcord import Interaction
# from dotenv import load_dotenv
# import asyncio

# from event.game_event import GameEvent
# from sound.musics import Musics


# GUILD_IDS = [1137767167413211216]
# load_dotenv()
# TOKEN = os.getenv("DISCORD_TOKEN")

# class MyBot(commands.Bot):
#     FFMPEG_EXECUTABLE = r"ffmpeg\bin\ffmpeg.exe"

#     def __init__(self):
#         super().__init__()
#         self.is_running = False
#         self.voice_channel = None
#         self.game_event = GameEvent()
#         self.musics = Musics()


#     async def on_ready(self):
#         print(f"{self.user} has connected to Discord!")

#         # general_channel = discord.utils.get(self.guild.channels, name="général")

#         # if general_channel:
#         #     await general_channel.send("Hello mother fucker")
#         # else:
#         #     print("Le salon général n'a pas été trouvé.")

#     async def detect_game_event(self):
#         screen = self.game_event.get_screen()

#         if self.game_event.boss_detection.play_music(screen):
#             await bot.play_music()

#         event = self.game_event.read_message.image_to_game_event(screen)

#         if event is not None:
#             if (
#                 (event == "abeille_death")
#                 or (event == "pierrick_death")
#                 or (event == "etchebest_death")
#                 or (event == "player_death")
#             ):
#                 await bot.play_music("il_est_decede")

#             elif event == "pierrick_invocation":
#                 await bot.play_music("les_meilleurs")

#             elif (
#                 (event == "abeille_invocation")
#                 or (event == "etchebest_invocation")
#                 or (event == "player_invocation")
#             ):
#                 await bot.play_music()

#             elif event == "fire_alight":
#                 await bot.play_music("lotr_one_ring")

#             elif event == "boss_begin":
#                 self.game_event.boss_detection.boss_is_alive = True
#                 await bot.play_music()

#             else:
#                 print(f"Event {event} isn't added.")

#     async def play_music(self, audio_name: str = None):
#         if self.voice_channel is None:
#             return

#         # if len(self.voice_channel.channel.members) == 1:
#         #     return

#         if self.voice_channel.is_playing():
#             return

#         audio_path = self.musics.path(audio_name)

#         self.voice_channel.play(
#             nextcord.FFmpegPCMAudio(
#                 source=audio_path
#             ),
#         )

#         while self.voice_channel.is_playing():
#             await asyncio.wait(1)

#     async def connect_to_voice_channel(
#         self, user: nextcord.member.Member
#     ):
#         if user.voice is None or user.voice.channel is None:
#             return

#         if self.voice_channel is None:
#             self.voice_channel = await user.voice.channel.connect()

#     async def disconnect_to_voice_channel(self):
#         await self.voice_channel.disconnect()


# bot = MyBot()


# @bot.event
# async def on_ready():
#     print(f'We have logged in as {bot.user}')


# @bot.slash_command(name="lancer", description="Joue des sons selon les évènements du jeu.", guild_ids=GUILD_IDS)
# async def start(interaction: Interaction):
#     if not bot.is_running:
#         bot.is_running = True

#         await bot.connect_to_voice_channel(interaction.user)
#         await bot.play_music()

#         await interaction.send("Le programme est lancé.")

#         while bot.is_running:
#             await bot.detect_game_event()
#             await asyncio.sleep(1)


# @bot.slash_command(name="rejoindre", description="Demande au bot de te rejoindre sur ton salon vocal.", guild_ids=GUILD_IDS)
# async def join_voice_channel(interaction: Interaction):
#     if bot.voice_channel is not None:
#         return

#     await bot.connect_to_voice_channel(interaction.user)
#     await bot.play_music()

#     if bot.voice_channel is not None:
#         await interaction.send("Je suis là !")
#     else:
#         await interaction.send("Je n'ai pas pu te rejoindre.")

# @bot.slash_command(name="stop", description="Arrête l'analyse du jeu et déconnecte le bot du salon vocal.", guild_ids=GUILD_IDS)
# async def disconnect_to_voice_channel(interaction: Interaction):
#     bot.is_running = False
#     await bot.play_music()
#     await bot.disconnect_to_voice_channel()

#     await interaction.send("Au revoir.")

# bot.run(TOKEN)

import os

import nextcord
from nextcord.ext import commands
from nextcord import Interaction, Embed
import asyncio

from event.game_event import GameEvent
from sound.musics import Musics


class MyBot(commands.Bot):
    FFMPEG_EXECUTABLE = r"ffmpeg\bin\ffmpeg.exe"

    def __init__(self, intents: nextcord.Intents):
        super().__init__(intents=intents)
        self.is_running = False
        self.server_session: ServerSession | None = None
        self.game_event = GameEvent()
        self.musics = Musics()

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")

    async def detect_game_event(self, interaction: Interaction):
        screen = self.game_event.get_screen()

        if self.game_event.boss_detection.play_music(screen):
            await bot.play_music(interaction)

        event = self.game_event.read_message.image_to_game_event(screen)

        if event is not None:
            if (
                (event == "abeille_death")
                or (event == "pierrick_death")
                or (event == "etchebest_death")
                or (event == "player_death")
            ):
                await bot.play_music(interaction, "il_est_decede")

            elif event == "pierrick_invocation":
                await bot.play_music(interaction, "les_meilleurs")

            elif (
                (event == "abeille_invocation")
                or (event == "etchebest_invocation")
                or (event == "player_invocation")
            ):
                await bot.play_music(interaction)

            elif event == "fire_alight":
                await bot.play_music(interaction, "lotr_one_ring")

            elif event == "boss_begin":
                self.game_event.boss_detection.boss_is_alive = True
                await bot.play_music(interaction)

            else:
                print(f"Event {event} isn't added.")

    async def _connect_to_voice_channel(self, channel: nextcord.channel.VoiceChannel):
        voice_client = await channel.connect()

        if voice_client.is_connected():
            server_session = ServerSession(voice_client)
            self.server_session = server_session
            return server_session

    async def disconnect_to_voice_channel(self):
        if self.voice_channel is None:
            return

        await self.voice_channel.disconnect()
        self.voice_channel = None

    async def get_session(self, interaction: Interaction | None = None, voice_state: nextcord.member.VoiceState | None = None):
        if interaction is not None:
            voice_state = interaction.user.voice

        if self.server_session is None:
            if voice_state is None:
                await interaction.send(
                    f"Tu dois d'abord être connecté à un serveur vocal."
                )
                return

            server_session = await self._connect_to_voice_channel(voice_state.channel)

        else:
            server_session = bot.server_session

            if bot.server_session.voice_client.channel != voice_state.channel:
                await server_session.voice_client.move_to(
                    voice_state.channel
                )

        return server_session

    async def play_music(self, interaction: Interaction | None = None, audio_name: str = None, voice_state: nextcord.member.VoiceState | None = None):
        server_session = await bot.get_session(interaction, voice_state=voice_state)
        
        if server_session is None:
            return

        audio_path = self.musics.path(audio_name)
        self.server_session.add_to_queue(audio_path)
        if (
            not self.server_session.voice_client.is_playing()
            and len(self.server_session.queue) == 1
        ):
            await self.server_session.start_playing()


class ServerSession:
    def __init__(self, voice_client):
        self.voice_client: nextcord.VoiceClient = voice_client
        self.queue = []

    def add_to_queue(self, audio_path: str):
        self.queue.append(nextcord.FFmpegPCMAudio(source=audio_path))

    async def start_playing(self):
        self.voice_client.play(
            self.queue[0],
            after=lambda error=None: self.after_playing(error),
        )

    async def after_playing(self, error):
        if error:
            raise error
        else:
            if self.queue:
                await self.play_next()

    async def play_next(self):
        self.queue.pop(0)
        if self.queue:
            await self.voice_client.play(
                self.queue[0], after=lambda error=None: self.after_playing(error)
            )


intents = nextcord.Intents.all()
bot = MyBot(intents=intents)


@bot.slash_command(name="lancer")
async def start(interaction: Interaction):
    """Joue des sons selon les évènements du jeu."""
    if bot.is_running:
        await interaction.send("L'application est déjà lancée.")
        return

    await bot.play_music(interaction=interaction)

    bot.is_running = True
    await interaction.send(f"L'application est lancée.")

    while bot.is_running:
        await bot.detect_game_event(interaction)
        await asyncio.sleep(1)


@bot.slash_command(name="stop")
async def stop(interaction: Interaction):
    """Arrête l'analyse du jeu et déconnecte le bot du salon vocal."""

    if not bot.is_running:
        await interaction.send("L'application n'a pas été lancée.")
        return

    bot.is_running = False

    if bot.server_session is None:
        await interaction.send(f"Au revoir !")
        return

    voice_client = bot.server_session.voice_client
    await voice_client.disconnect()
    voice_client.cleanup()
    bot.server_session = None
    await interaction.send(f"Au revoir !")


@bot.slash_command(name="aléatoire")
async def random_sound(interaction: Interaction):
    """Joue un son au hasard."""
    await bot.play_music(interaction=interaction)
    await interaction.send("Voilà un son aléatoire.")


@bot.slash_command(name="écouter")
async def play_sound(
    interaction: Interaction,
    sound_name: str = nextcord.SlashOption(
        name="son",
        description="Nom du son à jouer.",
        choices=bot.musics.names(),
        required=True,
    ),
):
    """Joue le son choisi."""
    await bot.play_music(interaction, sound_name)
    await interaction.send(f"Voilà le son **{sound_name}**.")


@bot.slash_command(name="ajouter")
async def add_sound(
    interaction: Interaction,
    attachment: nextcord.Attachment = nextcord.SlashOption(
        name="fichier",
        description="Fichier du son à ajouter.",
        required=True,
    ),
):
    """Ajoute un son."""
    filename = attachment.filename

    if filename.endswith(bot.musics.ALLOWED_EXTENSION):
        if filename.split(".")[0] in bot.musics.sound_files:
            await interaction.send(f"Le fichier {filename} est déjà présent.")

        else:
            await attachment.save(os.path.join(bot.musics.SOUND_PATH, filename))
            bot.musics.add(filename)
            await interaction.send(
                f"Le fichier {filename} a été ajouté à la liste des sons."
            )

    else:
        await interaction.send(
            f"Seules les extensions {bot.musics.ALLOWED_EXTENSION} sont autorisées débile"
        )


@bot.slash_command(name="supprimer")
async def add_sound(
    interaction: Interaction,
    sound_name: str = nextcord.SlashOption(
        name="son",
        description="Nom du son à supprimer.",
        choices=bot.musics.names(),
        required=True,
    ),
):
    """Supprime un son."""
    bot.musics.remove(sound_name)
    await interaction.send(f"Le son **{sound_name}** a été supprimé.")


@bot.slash_command(name="liste")
async def sound_list(interaction: Interaction):
    """Affiche la liste des sons disponibles avec leur probabilité."""
    embed = Embed(
        title="Liste des sons",
        color=0x00ff00
    )

    names = bot.musics.names()
    weights = bot.musics.prob()

    embed.add_field(name="Nom", value="\n".join(names), inline=True)
    embed.add_field(name="Poids", value="\n".join(weights), inline=True)

    await interaction.send(embed=embed)


@bot.slash_command(name="changer_poids")
async def change_weight(
    interaction: nextcord.Interaction,
    sound_name: str = nextcord.SlashOption(
        name="son",
        description="Nom du son à modifier.",
        choices=bot.musics.names(),
        required=True,
    ), 
    weight: float = nextcord.SlashOption(
        name="poids",
        description="Nouveau poids.",
        required=True,
    )
):
    """Change la probabilité d'apparaître d'un son."""
    bot.musics.change_weight(sound_name, weight)
    embed = Embed(
        title="Changement de poids",
        description=f"Le poids du son **{sound_name}** est maintenant de **{str(weight).replace(".", ",")}**.",
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
        await bot.play_music(voice_state=after)
    elif before.channel is not None and after.channel is None:
        await bot.play_music(voice_state=before)


bot.run("MTE4NDA1MTMxNzc1MzI2MjA4MA.GpFltY.yLkb2CgoUlfkP4Okh8ompkzaO243yASkO3vHH0")