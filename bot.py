# bot.py
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio

from event.game_event import GameEvent
from sound.musics import Musics

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


class MyBot(commands.Bot):
    FFMPEG_EXECUTABLE = r"ffmpeg\bin\ffmpeg.exe"

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.guild = None
        self.is_running = False
        self.voice_channel = None
        self.game_event = GameEvent()
        self.musics = Musics()

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
        self.guild = self.guilds[0]
        # general_channel = discord.utils.get(self.guild.channels, name="général")

        # if general_channel:
        #     await general_channel.send("Hello mother fucker")
        # else:
        #     print("Le salon général n'a pas été trouvé.")

    async def detect_game_event(self):
        screen = self.game_event.get_screen()

        if self.game_event.boss_detection.play_music(screen):
            await bot.play_music(self.musics.random_choice())

        event = self.game_event.read_message.image_to_game_event(screen)

        if event is not None:
            if event == "player_death":
                await bot.play_music(self.musics.random_choice())
            elif event == "player_invocation":
                await bot.play_music(self.musics.random_choice())
            elif event == "fire_alight":
                await bot.play_music(self.musics["lotr"])

    async def play_music(self, audio_path: str):
        if self.voice_channel is None:
            return
        
        if len(self.voice_channel.channel.members) == 1:
            return
        
        if self.voice_channel.is_playing():
            return

        self.voice_channel.play(
            discord.FFmpegPCMAudio(
                executable=self.FFMPEG_EXECUTABLE, source=audio_path
            ),
        )

    async def connect_to_voice_channel(
        self, voice_channel: discord.channel.VoiceChannel
    ):
        if self.voice_channel is None:
            self.voice_channel = await voice_channel.connect()

    async def disconnect_to_voice_channel(self):
        if self.voice_channel is None:
            return

        await self.voice_channel.disconnect()
        self.voice_channel = None


intents = discord.Intents.all()
bot = MyBot(command_prefix="/", intents=intents)


@bot.command(name="start")
async def connect_to_voice_channel(ctx: commands.context.Context):
    if not bot.is_running:
        bot.is_running = True
        author = ctx.author

        if author.voice is None or author.voice.channel is None:
            return

        await bot.connect_to_voice_channel(author.voice.channel)
        await bot.play_music(bot.musics.random_choice())

        while bot.is_running:
            await bot.detect_game_event()
            await asyncio.sleep(1)


@bot.command(name="join")
async def join_voice_channel(ctx: commands.context.Context):
    if bot.voice_channel is not None:
        return

    author = ctx.author
    if author.voice is None or author.voice.channel is None:
        return

    await bot.connect_to_voice_channel(author.voice.channel)
    await bot.play_music(bot.musics.random_choice())


@bot.command(name="stop")
async def disconnect_to_voice_channel(ctx):
    bot.is_running = False
    await bot.play_music(bot.musics.random_choice())
    await bot.disconnect_to_voice_channel()


@bot.command(name="random")
async def random_sound(ctx: commands.context.Context):
    author = ctx.author

    if author.voice is None or author.voice.channel is None:
        return

    await bot.connect_to_voice_channel(author.voice.channel)
    await bot.play_music(bot.musics.random_choice())


@bot.command(name="add")
async def add_sound(ctx: commands.context.Context):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Faut mettre le fichier avec la commande connard")
        return
    
    attachment = ctx.message.attachments[0]
    filename = attachment.filename

    if filename.endswith(bot.musics.ALLOWED_EXTENSION):
        if filename.split(".")[0] in bot.musics:
            await ctx.send(f"Le fichier {filename} est déjà présent.")

        else:
            await attachment.save(os.path.join(bot.musics.SOUND_PATH, filename))
            bot.musics.add(filename)
            await ctx.send(f"Le fichier {filename} a été ajouté à la liste des sons.")
            
    else:
        await ctx.send(f"Seules les extensions {bot.musics.ALLOWED_EXTENSION} sont autorisées débile")


@bot.event
async def on_voice_state_update(
    member: discord.member.Member,
    before: discord.member.VoiceState,
    after: discord.member.VoiceState,
):
    if member.id == bot.application_id:
        return

    if before.channel is None and after.channel is not None:
        await bot.connect_to_voice_channel(after.channel)
        if after.channel.id == bot.voice_channel.channel.id:
            await bot.play_music(bot.musics.random_choice())
    elif (
        before.channel is not None
        and after.channel is None
        and bot.voice_channel is not None
    ):
        if before.channel.id == bot.voice_channel.channel.id:
            await bot.play_music(bot.musics.random_choice())


bot.run(TOKEN)