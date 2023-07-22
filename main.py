import discord
import os
import logging
import random
import asyncio
from gtts import gTTS
from discord import Color
from dotenv import load_dotenv, find_dotenv
from find_closest_name import find_closest_match
from keep_alive import keep_alive
from discord.ext import commands
import youtube_dl
#from music import play
#from opuslib import Encoder


# Modify the Music cog's play function to accept either a URL or a filename
async def play(self, ctx, *, url_or_filename):
    if not ctx.voice_client:
        await ctx.invoke(self.join)

    ctx.voice_client.stop()

    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format': 'bestaudio'}

    # Check if the input is a valid URL or a filename
    is_url = True
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(url_or_filename, download=False)
            url2 = info['formats'][0]['url']
        except:
            is_url = False

    # If the input is a valid URL, use youtube_dl to download the audio
    if is_url:
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        await ctx.send(f"Playing: {info['title']}")
    else:
        # Otherwise, assume it's a filename and play the local audio file
        source = await discord.FFmpegOpusAudio.from_probe(url_or_filename, **FFMPEG_OPTIONS)

    ctx.voice_client.play(source)


_ = load_dotenv(find_dotenv())  # Read local .env file

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True  # Enable voice state events

bot = commands.Bot(command_prefix='$', intents=intents)


logging.basicConfig(level=logging.INFO)  # Configure logging
logger = logging.getLogger(__name__)

colors = [Color.red(), Color.orange(), Color.gold(), Color.green(), Color.blue(), Color.purple()]  # Rainbow colors

# Update the path to the ffmpeg executable here
ffmpeg_executable = "ffmpeg-6.0-amd64-static/ffmpeg"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})') 


def get_closest_username(input_username, members):
    closest_username = discord.utils.find(
        lambda m: m.name.lower().startswith(input_username.lower()) or m.display_name.lower().startswith(
            input_username.lower()),
        members
    )
    return closest_username


async def rainbow_text_animation(rainbow_message, message, user_mention, delay=0.5):
    rainbow_text = ''
    for char in rainbow_message:
        if char.isalpha():
            color_code = random.choice(colors)
            rainbow_text += f'`{char}`' if color_code == 'white' else f'`{{{color_code}}}{char}`'
        else:
            rainbow_text += char
    rainbow_message = await message.channel.send('↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓')
    while True:  # Number of color iterations
        embed = discord.Embed(description=f'{user_mention} HELLO', color=Color.random())
        await rainbow_message.edit(embed=embed)
        await asyncio.sleep(delay)


@bot.command()
async def nay(ctx, *, input_username):
    words = input_username.split(' ')
    if len(words) >= 1:
        input_username = ' '.join(words[0:])  # Joining the words back together

        mentioned_users = ctx.guild.members
        closest_username = get_closest_username(input_username, mentioned_users)

        if closest_username:
            user_mention = f'{closest_username.mention}'
            rainbow_message = f'{user_mention}'
            await rainbow_text_animation(rainbow_message, ctx.message, user_mention)
        else:
            await ctx.send('No close match found.')
    else:
        await ctx.send('Invalid command format.')

@bot.command()
async def tts(ctx, *, tts_message):
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            vc = await voice_channel.connect()
        else:
            vc = ctx.guild.voice_client

        tts = gTTS(text=tts_message, lang='en', slow=False)
        tts.save('tts.mp3')  # Save the TTS audio to a file

        vc.play(discord.FFmpegPCMAudio('pony.mp3'))

        while vc.is_playing():
            await asyncio.sleep(1)

        await vc.disconnect()
    else:
        await ctx.send('You need to be in a voice channel to use $tts.')

@bot.command()
async def pony(ctx, *, url_or_filename):
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            vc = await voice_channel.connect()
        else:
            vc = ctx.guild.voice_client

        await play(ctx, url_or_filename)  # Call the play function with ctx instead of message
    else:
        await ctx.send('You need to be in a voice channel to use $pony.')

@bot.event
async def on_message(message):
    print("Message received:", message.content)  # Add this print statement
    if message.author == bot.user:
        return

    # Custom command handling
    if message.content.startswith('$test'):  # Replace $test with your actual custom command prefix
        # Handle $test command
        await message.channel.send('This is a test command!')

    # Other custom command handling can be added here...

    # Here you can add any other code to handle regular messages if needed

    await bot.process_commands(message)  # Process the built-in commands

@bot.command()
async def test(ctx):
    await ctx.send("Testing: Bot is responding!")

keep_alive()
my_secret = os.environ['TOKEN']
bot.run(my_secret)
