import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("El token de Discord no está configurado. Asegúrate de tener un archivo .env con DISCORD_TOKEN.")
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def play(ctx, url):
    if ctx.author.voice is None:
        return await ctx.send("⚠️ ¡Debes estar en un canal de voz!")

    voice_channel = ctx.author.voice.channel

    # Conexión al canal de voz
    if ctx.voice_client is None:
        await voice_channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        filename = ydl.prepare_filename(info)
        # Cambiar la extensión del archivo a .mp3
        filename = filename.replace('.webm', '.mp3')
        # Cambiar la extensión del archivo a .mp3
        filename = 'song.mp3'

        title = info.get('title', 'Título desconocido')  # esto evita el KeyError

    voice_client = ctx.voice_client

    if not voice_client.is_playing():
        voice_client.play(discord.FFmpegPCMAudio(filename),
                          after=lambda e: print(f"Reproducción finalizada: {e}"))
        await ctx.send(f"🎶 Reproduciendo: {title}")
    else:
        await ctx.send("⚠️ Ya se está reproduciendo otra canción.")

@bot.command()
async def playLarge(ctx, url):
    if ctx.author.voice is None:
        return await ctx.send("⚠️ ¡Debes estar en un canal de voz!")

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await voice_channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info['url']
            title = info.get('title', 'Título desconocido')

        voice_client = ctx.voice_client

        if not voice_client.is_playing():
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
            voice_client.play(
                discord.FFmpegPCMAudio(stream_url, **ffmpeg_options),
                after=lambda e: print(f"Reproducción finalizada: {e}")
            )
            await ctx.send(f"🎶 Reproduciendo: {title}")
        else:
            await ctx.send("⚠️ Ya se está reproduciendo otra canción.")
    except Exception as e:
        await ctx.send(f"❌ Error al intentar reproducir el audio: {str(e)}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Se detuvo la música y el bot salió del canal de voz.")
    else:
        await ctx.send("❌ El bot no está conectado a ningún canal de voz.")

bot.run(TOKEN)
