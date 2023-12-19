import os
import sys

import nextcord
from nextcord.ext import commands
from nextcord import Interaction, Embed
import asyncio
from dotenv import load_dotenv

from event.game_event import GameEvent
from sound.musics import Musics
from utils.utils import string_normalisation

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


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

    async def _connect_to_voice_channel(self, channel: nextcord.channel.VoiceChannel):
        voice_client = await channel.connect()

        if voice_client.is_connected():
            server_session = ServerSession(voice_client)
            self.server_session = server_session
            return server_session

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

            if (voice_state is not None) and (bot.server_session.voice_client.channel != voice_state.channel):
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


async def autocomplete_pseudo(interaction: Interaction, user_input: str):
    current_pseudo = bot.game_event.get_event_per_pseudo().keys()
    return filter(lambda pseudo : string_normalisation(user_input) in string_normalisation(pseudo), current_pseudo)


async def autocomplete_sound(interaction: Interaction, user_input: str):
    current_sounds = bot.musics.names()
    return filter(lambda sound : string_normalisation(user_input) in string_normalisation(sound), current_sounds)


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
        await bot.detect_game_event()
        await asyncio.sleep(1)


@bot.slash_command(name="stop")
async def stop(interaction: Interaction):
    """Arrête l'analyse du jeu et déconnecte le bot du salon vocal."""

    if not bot.is_running and interaction is not None:
        await interaction.send("L'application n'a pas été lancée.")
        return

    bot.is_running = False

    if bot.server_session is None and interaction is not None:
        await interaction.send(f"Au revoir !")
        return

    voice_client = bot.server_session.voice_client
    await voice_client.disconnect()
    voice_client.cleanup()
    bot.server_session = None
    
    if interaction is not None:
        await interaction.send(f"Au revoir !")


@bot.slash_command(name="relancer")
async def restart(interaction: Interaction):
  """Arrête le bot et le relance."""
  await stop(interaction)
  await interaction.send("Le bot va être relancé...")
  os.execv(sys.executable, ['python'] + sys.argv)


@bot.slash_command(name="évènement")
async def event(interaction: Interaction):
    pass

@event.subcommand(name="pseudo")
async def pseudo(interaction: Interaction):
    pass


@pseudo.subcommand(name="liste")
async def pseudo_list(interaction: Interaction):
    """Liste des joueurs ajoutés dans la détection des évènements."""
    pseudo = list(bot.game_event.get_event_per_pseudo().keys())

    if not pseudo:
        await interaction.send("Il n'y a encore aucun pseudo ajouté.")
        return

    embed = Embed(
        title="Liste des pseudo",
        color=0x00ff00
    )
    embed.add_field(name="Pseudo", value="\n".join(pseudo))
    await interaction.send(embed=embed)


@pseudo.subcommand(name="ajouter")
async def add_pseudo(
    interaction: Interaction,
    pseudo: str = nextcord.SlashOption(
        name="pseudo",
        description="Pseudo à ajouter.",
        required=True,
)):
    """Ajoute un nouveau pseudo à la liste des évènements."""
    if bot.game_event.pseudo_is_added(pseudo):
        await interaction.send(f"Le pseudo {pseudo} est déjà ajouté.")
    else:
        bot.game_event.add_pseudo(pseudo)
        await interaction.send(f"Le pseudo {pseudo} a été ajouté.")


@pseudo.subcommand(name="supprimer")
async def delete_pseudo(
    interaction: Interaction,
    pseudo: str = nextcord.SlashOption(
        name="pseudo",
        description="Pseudo à supprimer.",
        required=True,
        autocomplete_callback=autocomplete_pseudo
)):
    """Supprime un pseudo de la liste des évènements."""
    if bot.game_event.pseudo_is_added():
        bot.game_event.delete_pseudo(pseudo)
        await interaction.send(f"Le pseudo {pseudo} a été supprimé.")
    else:
        await interaction.send(f"Le pseudo {pseudo} n'est pas présent dans la liste des pseudo ajoutés.")


@bot.slash_command(name="son")
async def sound(interaction: Interaction):
    pass


@sound.subcommand(name="aléatoire")
async def random_sound(interaction: Interaction):
    """Joue un son au hasard."""
    await bot.play_music(interaction=interaction)
    await interaction.send("Voilà un son aléatoire.")


@sound.subcommand(name="écouter")
async def play_sound(
    interaction: Interaction,
    sound_name: str = nextcord.SlashOption(
        name="son",
        description="Nom du son à jouer.",
        autocomplete_callback=autocomplete_sound,
        required=True,
    ),
):
    """Joue le son choisi."""
    await bot.play_music(interaction, sound_name)
    await interaction.send(f"Voilà le son **{sound_name}**.")


@sound.subcommand(name="ajouter")
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


@sound.subcommand(name="supprimer")
async def delete_sound(
    interaction: Interaction,
    sound_name: str = nextcord.SlashOption(
        name="son",
        description="Nom du son à supprimer.",
        autocomplete_callback=autocomplete_sound,
        required=True,
    ),
):
    """Supprime un son."""
    bot.musics.remove(sound_name)
    await interaction.send(f"Le son **{sound_name}** a été supprimé.")


@sound.subcommand(name="liste")
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


@sound.subcommand(name="changer_poids")
async def change_weight(
    interaction: nextcord.Interaction,
    sound_name: str = nextcord.SlashOption(
        name="son",
        description="Nom du son à modifier.",
        autocomplete_callback=autocomplete_sound,
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
        if len(before.channel.members) == 1:
            await stop(interaction=None)
            return
        await bot.play_music(voice_state=before)

bot.run(TOKEN)