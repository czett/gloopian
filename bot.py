import discord
from discord.ext import commands
from responses import handle_response
from dotenv import load_dotenv
import os, random, time, asyncio
from discord.ui import Button, View
import asyncio
import tempfile, edge_tts
import requests
from groq import Client
from datetime import datetime

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Client(api_key=groq_api_key)

# Ordner für Sounds
PUBLIC_SOUNDS_DIR = "sounds/public"
SECRET_SOUNDS_DIR = "sounds/secret"

def load_sounds():
    """Lädt Sounds aus den beiden Ordnern und gibt zwei Dictionaries zurück"""
    audio_files = {}
    hidden_files = {}

    # Öffentliche Sounds
    if os.path.exists(PUBLIC_SOUNDS_DIR):
        for file in os.listdir(PUBLIC_SOUNDS_DIR):
            if file.lower().endswith((".mp3", ".wav", ".ogg")):
                key = os.path.splitext(file)[0]  # Dateiname ohne Endung
                audio_files[key] = os.path.join(PUBLIC_SOUNDS_DIR, file)

    # Versteckte Sounds
    if os.path.exists(SECRET_SOUNDS_DIR):
        for file in os.listdir(SECRET_SOUNDS_DIR):
            if file.lower().endswith((".mp3", ".wav", ".ogg")):
                key = os.path.splitext(file)[0]
                hidden_files[key] = os.path.join(SECRET_SOUNDS_DIR, file)

    return audio_files, hidden_files

# Globale Dictionaries initialisieren
audio_files, hidden_files = load_sounds()

async def try_delete_message(ctx):
    """Versucht die User-Nachricht zu löschen, ignoriert Fehler."""
    try:
        await ctx.message.delete()
    except (discord.Forbidden, discord.HTTPException):
        pass

async def tts_play(ctx, text: str, voice="de-DE-ConradNeural"):
    if ctx.author.voice is None:
        await ctx.send("Du musst in einem Sprachkanal sein!")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    if not ctx.voice_client:
        await ctx.send("Fehler beim Verbinden zum Voice-Channel.")
        return

    # TTS erzeugen (männliche Stimme)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        filepath = tmpfile.name
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)

    ctx.voice_client.stop()
    audio_source = discord.FFmpegPCMAudio(
        executable="C:\\Users\\reala\\Desktop\\Colin\\coding\\FFmpeg\\bin\\ffmpeg.exe",
        source=filepath
    )
    ctx.voice_client.play(audio_source)

@bot.event
async def on_ready():
  print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  response = handle_response(message.content)
  if response:
    await message.channel.send(response)

  await bot.process_commands(message)

@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, new_nickname: str = None):
  if new_nickname is None:
    await ctx.send("Please provide a nickname to change to.")
    return

  try:
    await member.edit(nick=new_nickname)
    await ctx.send(
        f"Nickname for {member.mention} has been changed to **{new_nickname}**."
    )
  except discord.Forbidden:
    await ctx.send("I do not have permission to change this user's nickname.")
  except discord.HTTPException:
    await ctx.send("Failed to change the nickname due to an error.")

@bot.command()
async def join(ctx):
  await try_delete_message(ctx)
  channel = ctx.author.voice.channel
  vc = await channel.connect()

@bot.command()
async def innerjoin(ctx):
  channel = ctx.author.voice.channel
  vc = await channel.connect()

@bot.command()
async def play(ctx, option="", stay="y"):
    await try_delete_message(ctx)
    # Beide Dicts zusammenführen → alle Sounds sind spielbar
    all_sounds = {**audio_files, **hidden_files}

    if not option:
        await ctx.send("'?play <soundname>' oder '?sounds' für die sichtbare Liste")
        return

    if option not in all_sounds:
        await ctx.send(f"Den Sound '{option}' gibt es nicht. Benutze '?sounds' für die sichtbaren Sounds.")
        return

    filepath = all_sounds[option]

    if ctx.author.voice is None:
        await ctx.send("Du musst in einem Sprachkanal sein!")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    ctx.voice_client.stop()
    audio_source = discord.FFmpegPCMAudio(
        executable="C:\\Users\\reala\\Desktop\\Colin\\coding\\FFmpeg\\bin\\ffmpeg.exe",
        source=filepath
    )

    if stay.lower() == "n":
        async def leave_channel():
            if ctx.voice_client is not None:
                await ctx.voice_client.disconnect()
        ctx.voice_client.play(audio_source, after=lambda e: bot.loop.create_task(leave_channel()))
    else:
        ctx.voice_client.play(audio_source)

@bot.command()
async def leave(ctx):
  await try_delete_message(ctx)
  await ctx.voice_client.disconnect()

@bot.command()
async def sounds(ctx):
    await try_delete_message(ctx)
    sound_list = "\n".join(f"- {name}" for name in audio_files.keys())
    await ctx.send(f"**Verfügbare Sounds:**\n{sound_list}")

def run_discord_bot():
  load_dotenv()
  TOKEN = os.getenv("DISCORD_TOKEN")
  bot.run(TOKEN)

@bot.command()
async def tts(ctx, *, text: str):
    await try_delete_message(ctx)
    await tts_play(ctx, text)

@bot.command()
async def clock(ctx):
    await try_delete_message(ctx)
    jetzt = datetime.now().strftime("%H:%M")
    await tts_play(ctx, f"Es ist jetzt {jetzt} Uhr.")

@bot.command()
async def hop(ctx):
    await try_delete_message(ctx)
    if ctx.author.voice is None:
        await ctx.send("Du musst in einem Sprachkanal sein!")
        return

    channel = ctx.author.voice.channel
    vc = ctx.voice_client

    if vc is not None:
        await vc.disconnect()
        await asyncio.sleep(1)
        await channel.connect()
    else:
        await channel.connect()

@bot.command()
async def wetter(ctx):
    await try_delete_message(ctx)
    url = "https://api.open-meteo.com/v1/forecast?latitude=51.5142&longitude=7.4653&current_weather=true"
    r = requests.get(url).json()

    if "current_weather" in r and "temperature" in r["current_weather"]:
        temp = r["current_weather"]["temperature"]
        await tts_play(ctx, f"In Dortmund sind es {temp} Grad Celsius.")
    else:
        await ctx.send("gerade gibts kein wetter")

@bot.command()
async def luftdruck(ctx):
    await try_delete_message(ctx)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=51.5142&longitude=7.4653"
        "&current=surface_pressure"
    )
    r = requests.get(url).json()

    current = r.get("current", {})
    pressure = current.get("surface_pressure")

    if pressure is not None:
        await tts_play(ctx, f"Der Luftdruck in Dortmund beträgt {pressure} Hektopascal.")
    else:
        await ctx.send("es gibt im moment keinen Luftdruck")

from datetime import date

@bot.command()
async def michlgeburtstag(ctx):
    await try_delete_message(ctx)
    heute = date.today()
    ziel = date(heute.year, 5, 13)

    if heute > ziel:
        ziel = date(heute.year + 1, 5, 13)

    tage = (ziel - heute).days
    await tts_play(ctx, f"Es sind noch {tage} Tage bis Herr Michl Geburtstag hat.")

@bot.command()
async def johannesauto(ctx):
    await try_delete_message(ctx)
    heute = date.today()
    ziel = date(heute.year, 12, 3)

    if heute > ziel:
        ziel = date(heute.year + 1, 5, 13)

    tage = (ziel - heute).days
    await tts_play(ctx, f"Es sind noch {tage} Tage bis Johannes Auto fahren darf.")

# globales Dictionary für Gedächtnis
chat_memory = {}  # key: user_id oder channel_id, value: Liste von Nachrichten

@bot.command()
async def ai(ctx, *, prompt: str):
    await try_delete_message(ctx)
    user_id = ctx.author.id

    # Memory initialisieren, falls noch nicht vorhanden
    if user_id not in chat_memory:
        chat_memory[user_id] = []

    # Prüfen, ob "--text" im Prompt ist
    text_only = False
    if prompt.endswith("-t"):
        text_only = True
        prompt = prompt.rsplit("-t", 1)[0].strip()  # Flag entfernen

    # Fester Prompt-Prefix für Gloopian
    prefix = (
        "Du bist Gloopian, eine hilfreiche, intelligente AI mit einem leichten lockeren Humor. "
        "Antworten sollen korrekt, klar und verständlich sein, dürfen aber manchmal locker oder humorvoll klingen. "
        "Schreibe keine unnötigen Einleitungen oder deinen Namen. "
        "Antworten können je nach Frage kurz oder ausführlich sein, aber nicht länger als nötig. "
        "Bei einfachen Fragen darfst du ein bisschen Smalltalk einfließen lassen. "
        "Gib nur den reinen Text der Antwort, nichts sonst."
    )

    # Vorherige Konversation anhängen
    conversation = "\n".join(chat_memory[user_id][-10:])  # nur die letzten 10 Nachrichten
    full_prompt = prefix + conversation + f"\nUser: {prompt}"

    # Groq Anfrage
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="gemma2-9b-it",
            temperature=0,
        )

        answer = completion.choices[0].message.content

        # Antwort senden, je nach Flag
        if text_only:
            await ctx.send(answer)
        else:
            await tts_play(ctx, answer)

        # Chat speichern
        chat_memory[user_id].append(f"User: {prompt}")
        chat_memory[user_id].append(f"Gloopian: {answer}")

    except Exception as e:
        await ctx.send(f"Fehler bei Groq-Anfrage: {e}")

@bot.command()
async def commands(ctx):
    # Versuche, die User-Nachricht zu löschen
    try:
        await ctx.message.delete()
    except (discord.Forbidden, discord.HTTPException):
        pass

    # Liste aller Commands
    commands_list = [
        "?ai <prompt> [-t] - Gloopian antwortet im Call. Mit -t am Ende nur als Text, ohne TTS",
        "?play <soundname> [stay=y/n] - Spielt einen Sound ab",
        "?sounds - Zeigt alle sichtbaren Sounds",
        "?tts <text> - Spricht den Text im Voice-Channel",
        "?join - Bot tritt deinem Voice-Channel bei",
        "?leave - Bot verlässt den Voice-Channel",
        "?nick <user> <nickname> - Nickname ändern (mit Berechtigung)",
        "?clock - Ansage der aktuellen Uhrzeit",
        "?hop - Bot verlässt und betritt Voice-Channel erneut",
        "?wetter - Aktuelles Wetter abrufen",
        "?luftdruck - Aktuellen Luftdruck abrufen",
        "?meow - Meow",
        "?michlgeburtstag - Tage bis Michl Geburtstag",
        "?johannesauto - Tage bis Johannes Auto fahren darf"
    ]

    help_message = "**Verfügbare Commands:**\n" + "\n".join(commands_list)
    await ctx.send(help_message)

@bot.command()
async def meow(ctx):
    await try_delete_message(ctx)
    meows = ", ".join(["miau"] * random.randint(1, 10))

    await tts_play(ctx, meows)

try:
    run_discord_bot()
except Exception as e:
    print(f"Ein Fehler ist aufgetreten: {e}")
    input("Drücke Enter zum Beenden...")
