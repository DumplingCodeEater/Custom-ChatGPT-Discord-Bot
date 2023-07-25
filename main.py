import discord
import os
import logging
import random
import asyncio
import ffmpeg
from gtts import gTTS
from discord import Color
from dotenv import load_dotenv, find_dotenv
from keep_alive import keep_alive
from discord.ext import commands
from music_functions import Music, search_youtube


_ = load_dotenv(find_dotenv())  # Read local .env file

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True  # Enable voice state events

bot = commands.Bot(command_prefix='$', intents=intents)


logging.basicConfig(level=logging.INFO)  # Configure logging
logger = logging.getLogger(__name__)

colors = [Color.red(), Color.orange(), Color.gold(), Color.green(), Color.blue(), Color.purple()]  # Rainbow colors

# Initialize the Music class
music = Music()


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
        embed = discord.Embed(description=f'{user_mention} UR MOM IS GAY', color=Color.random())
        await rainbow_message.edit(embed=embed)
        await asyncio.sleep(delay)


@bot.command(help="Play a rainbow animation with the provided username.")
async def nay(ctx, *, input_username):
    if input_username:
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

@bot.command(help="Play a text-to-speech message in the voice channel you are in.")
async def tts(ctx, *, tts_message):
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            vc = await voice_channel.connect()
        else:
            vc = ctx.guild.voice_client

        tts = gTTS(text=tts_message, lang='en', slow=False)
        if os.path.exists("tts.mp3"):
                os.remove("tts.mp3")
        tts.save('tts.mp3')  # Save the TTS audio to a file

        vc.play(discord.FFmpegPCMAudio('tts.mp3'))

        while vc.is_playing():
            await asyncio.sleep(1)

        await vc.disconnect()
    else:
        await ctx.send('You need to be in a voice channel to use $tts.')

@bot.command(help="Play a downloaded audio file or a YouTube URL in the voice channel you are in.")
async def urlplay_downloaded(ctx, *, url_or_filename):
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            vc = await voice_channel.connect()
        else:
            vc = ctx.guild.voice_client

        await music.play(ctx=ctx, url_or_filename=url_or_filename)  # Call the play function with ctx instead of message
    else:
        await ctx.send('You need to be in a voice channel to use $pony.')


@bot.command(help="Play a YouTube video or audio from the provided URL.")
async def urlplay(ctx, *, url):
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            vc = await voice_channel.connect()
        else:
            vc = ctx.guild.voice_client

        await music.enqueue(ctx=ctx, url=url)  # Call the play function with ctx instead of message
    else:
        await ctx.send('You need to be in a voice channel to use $pony.')


@bot.command(help="Search for a YouTube video or audio and queue it in the playlist.")
async def search(ctx, *, query):
    url = await search_youtube(ctx=ctx, query=query)

    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            vc = await voice_channel.connect()
        else:
            vc = ctx.guild.voice_client

        # Use the play2 method of the Music class
        await music.enqueue(ctx=ctx, url=url)
    else:
        await ctx.send('You need to be in a voice channel to use $pony.')



@bot.command(help="Pause the currently playing song.")
async def pause(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Paused ⏸️")
    else:
        await ctx.send("Nothing is playing to pause.")


@bot.command(help="Resume the currently paused song.")
async def resume(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Resumed ⏯️")
    else:
        await ctx.send("Nothing is paused to resume.")



@bot.command(help="A test command to play 'pony.mp3' in the voice channel you are in.")
async def test(ctx):
    # Send a test message
    await ctx.channel.send('This is a test command!')


    # Create the audio source
    source = discord.FFmpegOpusAudio('pony.mp3')
    
    
    # Join the voice channel if not already connected
    if not ctx.voice_client:
        vc = await ctx.author.voice.channel.connect()
    else:
        vc = ctx.voice_client

    # Play the audio
    vc.play(source)

    # Log that the audio playback has started
    logging.info("Audio playback started")

    # Wait until the audio is finished playing
    while vc.is_playing():
        await asyncio.sleep(1)

    # Log that the audio playback has finished
    logging.info("Audio playback finished")

    # Disconnect from the voice channel after playback is complete
    await vc.disconnect()

    # Log that the bot has disconnected from the voice channel
    logging.info("Bot disconnected from the voice channel")
    


  
@bot.event
async def on_message(message):
    print("Message received:", message.content)  # Add this print statement
    if message.author == bot.user:
        return

    # Other custom command handling can be added here...

    # Here you can add any other code to handle regular messages if needed

    await bot.process_commands(message)  # Process the built-in commands



keep_alive()
my_secret = os.environ['TOKEN']
bot.run(my_secret)

