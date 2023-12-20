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

        audio_path = self.musics.get_path(audio_name)
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
    current_pseudo = bot.game_event.event_per_pseudo.index
    return filter(lambda pseudo : string_normalisation(user_input) in string_normalisation(pseudo), current_pseudo)


async def autocomplete_event(interaction: Interaction, user_input: str):
    current_event = [bot.game_event.translate_event(event).lower() for event in bot.game_event.event_per_pseudo.columns]
    return filter(lambda pseudo : string_normalisation(user_input) in string_normalisation(pseudo), current_event)


async def autocomplete_sound(interaction: Interaction, user_input: str):
    current_sounds = bot.musics.get_names()
    current_sounds.insert(0, bot.game_event.RANDOM)
    return filter(lambda sound : string_normalisation(user_input) in string_normalisation(sound), current_sounds)


@bot.slash_command(name="lancer")
async def start(interaction: Interaction):
    """Joue des sons selon les évènements du jeu."""
    if bot.is_running:
        await interaction.send("L'application est déjà lancée.")
        return

    await bot.play_music(interaction=interaction)

    if interaction.user.voice is None or interaction.user.voice.channel is None:
        return

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

    if bot.server_session is None:
        if interaction is not None:
            await interaction.send(f"Au revoir !")
        return

    voice_client = bot.server_session.voice_client
    await voice_client.disconnect()
    voice_client.cleanup()
    bot.server_session = None
    
    if interaction is not None:
        await interaction.send(f"Au revoir !")


@bot.slash_command(name="évènement")
async def event(interaction: Interaction):
    pass

@event.subcommand(name="pseudo")
async def pseudo(interaction: Interaction):
    pass


@event.subcommand(name="global")
async def global_event(interaction: Interaction):
    pass


@global_event.subcommand(name="liste")
async def global_event_list(interaction: Interaction):
    """Liste des des sons par évènements global."""
    event_global = bot.game_event.event_global

    if not event_global:
        await interaction.send("Aucun évènement global n'est ajouté.")
        return
    
    embed = Embed(
        title="Liste des sons par évènement global.",
        color=0x00ff00
    )
    for event_name, event_info in event_global.items():
        if not event_info:
            event_info = bot.game_event.RANDOM
        embed.add_field(name=bot.game_event.translate_global_event(event_name), value=event_info, inline=True)
 
    await interaction.send(embed=embed)


@global_event.subcommand(name="modifier")
async def change_global_event_sound(
    interaction: Interaction,
    event_name: str = nextcord.SlashOption(
        name="évènemement",
        description="Évènement global à modifier.",
        choices=bot.game_event.translate_events(bot.game_event.DEFAULT_GLOBAL_EVENT_SOUND.keys()),
        required=True,
        ),
    new_sound: str = nextcord.SlashOption(
        name="son",
        description="Nouveau son à associé à l'évènement.",
        autocomplete_callback=autocomplete_sound,
        required=True,
        ),
    ):
    """Modifier le son d'un évènement global."""
    if not bot.musics.has_sound(new_sound):
        await interaction.send(f"Le son **{new_sound}** n'a pas été trouvé.")
        return
 
    await interaction.send("cc")


@pseudo.subcommand(name="liste")
async def pseudo_list(interaction: Interaction):
    """Liste des sons par évènements pour chaque joueur ajouté."""
    event_per_pseudo = bot.game_event.event_per_pseudo

    if event_per_pseudo.empty:
        await interaction.send("Il n'y a encore aucun pseudo ajouté.")
        return

    embed = Embed(
        title="Liste des sons par pseudo et évènement",
        color=0x00ff00
    )
    embed.add_field(name="Pseudo", value="\n".join(event_per_pseudo.index), inline=True)

    random_name = bot.game_event.RANDOM
    for event_name in event_per_pseudo.columns:
        event_sounds = "\n".join(event_per_pseudo.loc[:, event_name].fillna(random_name).replace("", random_name))
        embed.add_field(name=bot.game_event.translate_event(event_name), value=event_sounds, inline=True)
 
    await interaction.send(embed=embed)


@pseudo.subcommand(name="ajouter")
async def add_pseudo(
    interaction: Interaction,
    pseudo: str = nextcord.SlashOption(
        name="pseudo",
        description="Pseudo à ajouter.",
        required=True,
    ),
):
    """Ajoute un nouveau pseudo à la liste des évènements."""
    if bot.game_event.is_new_pseudo(pseudo):
        bot.game_event.add_pseudo(pseudo)
        await interaction.send(f"Le pseudo **{pseudo}** a été ajouté avec les sons par défaut.")
    else:
        await interaction.send(f"Le pseudo **{pseudo}** est déjà ajouté.")


@pseudo.subcommand(name="supprimer")
async def delete_pseudo(
    interaction: Interaction,
    pseudo: str = nextcord.SlashOption(
        name="pseudo",
        description="Pseudo à supprimer.",
        required=True,
        autocomplete_callback=autocomplete_pseudo
    ),
):
    """Supprime un pseudo de la liste des évènements."""
    if bot.game_event.is_new_pseudo(pseudo):
        await interaction.send(f"Le pseudo **{pseudo}** n'est pas présent dans la liste des pseudo ajoutés.")
    else:
        bot.game_event.delete_pseudo(pseudo)
        await interaction.send(f"Le pseudo **{pseudo}** a été supprimé.")


@pseudo.subcommand(name="modifier")
async def edit_pseudo(
    interaction: Interaction,
    pseudo: str = nextcord.SlashOption(
        name="pseudo",
        description="Pseudo à supprimer.",
        required=True,
        autocomplete_callback=autocomplete_pseudo,
    ),
    event: str = nextcord.SlashOption(
        name="évènement",
        description="Changer le son associé à cet évènement.",
        required=True,
        autocomplete_callback=autocomplete_event,
    ),
    sound_name: str = nextcord.SlashOption(
        name="son",
        description="Son à choisir.",
        autocomplete_callback=autocomplete_sound,
        required=True,
    ),
):
    """Modifie le son associé à un évènement et un pseudo."""
    
    if bot.game_event.is_new_pseudo(pseudo):
        await interaction.send(f"Le pseudo **{pseudo}** n'est pas présent dans la liste des pseudo ajoutés.")
        return
    
    event_translated = bot.game_event.untranslate_event(event.capitalize())

    if not bot.game_event.exists(event_translated):
        await interaction.send(f"L'évènement **{event}** n'existe pas.")
        return
    
    if sound_name == bot.game_event.RANDOM:
        sound_name = ""

    else:
        if not bot.musics.has_sound(sound_name):
            await interaction.send(f"Le son **{sound_name}** n'a pas été trouvé.")
            return
    
    bot.game_event.change_event(pseudo, event_translated, sound_name)
    await interaction.send(f"Le son associé à l'évènement **{event}** a été modifié pour le pseudo **{pseudo}**.")


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
    if bot.musics.has_sound(sound_name):
        await bot.play_music(interaction, sound_name)
        await interaction.send(f"Voilà le son **{sound_name}**.")
    else:
        await interaction.send(f"Le son **{sound_name}** n'existe pas.")


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
        if bot.musics.has_sound(filename):
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
    if bot.musics.has_sound(sound_name):
        bot.musics.remove(sound_name)
        await interaction.send(f"Le son **{sound_name}** a été supprimé.")
    else:
        await interaction.send(f"Le son **{sound_name}** n'est pas présent.")


@sound.subcommand(name="liste")
async def sound_list(interaction: Interaction):
    """Affiche la liste des sons disponibles avec leur probabilité."""
    embed = Embed(
        title="Liste des sons",
        color=0x00ff00
    )

    names = bot.musics.sound_info.index
    weights = bot.musics.get_probabilities()

    embed.add_field(name="Nom", value="\n".join(names), inline=True)
    embed.add_field(name="Poids", value="\n".join(weights), inline=True)

    await interaction.send(embed=embed)


@sound.subcommand(name="changer_poids")
async def change_weight(
    interaction: Interaction,
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
    if bot.musics.has_sound(sound_name):
        bot.musics.change_weight(sound_name, weight)
        embed = Embed(
            title="Changement de poids",
            description=f"Le poids du son **{sound_name}** est maintenant de **{str(weight).replace(".", ",")}**.",
            color=0x00ff00
        )
        await interaction.send(embed=embed)
    else:
        await interaction.send(f"Le son **{sound_name}** n'est pas présent.")


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
        if len(before.channel.members) <= 1:
            await stop(interaction=None)
            return
        await bot.play_music(voice_state=before)

bot.run(TOKEN)
