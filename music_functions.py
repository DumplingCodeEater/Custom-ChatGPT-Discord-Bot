import discord
import os
import yt_dlp
import logging
import ffmpeg
import asyncio
import queue
from discord.ext import commands

"""
Represents a song object using the Youtube video's title, URL, and duration
"""
class Song:
  def __init__(self, title, url, duration):
        self.title = title
        self.url = url
        self.duration = duration

"""
Manages the audio music playback, including queueing, playing, and looping songs
"""
class Music:
    def __init__(self):
        self.queue = queue.Queue()
        self.playing_list = False
        self.loop_queue = False  # New attribute to store loop state

    # Toggles the loop state of the queue
    def toggle_loop_queue(self):
        self.loop_queue = not self.loop_queue
        return self.loop_queue

    # Converts a video file to an audio file using ffmpeg
    def convert_to_audio(self, video_file, audio_file):
        (
            ffmpeg.input(video_file)
            .output(audio_file, format="mp3", acodec="libmp3lame")
            .overwrite_output()
            .run()
        )
    
    # Plays a song from a URL or a local file
    async def play(self, ctx, *, url_or_filename):
        if not ctx.voice_client:
            await ctx.invoke(ctx.bot.get_command("join"))

        ctx.voice_client.stop()

        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': 'bestaudio'}

        is_url = True
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url_or_filename, download=False)
                url2 = info['formats'][0]['url']
            except:
                is_url = False

        if is_url:
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")

            if os.path.exists("temp_audio.mp3"):
                os.remove("temp_audio.mp3")

            video_file = "temp_video.mp4"
            audio_file = "temp_audio.mp3"

            ydl_opts = {
                'outtmpl': video_file,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_or_filename])

            self.convert_to_audio(video_file, audio_file)

            source = discord.FFmpegOpusAudio(audio_file)
            await ctx.send(f"Playing: {info['title']}")
        else:
            source = discord.FFmpegOpusAudio(url_or_filename)

        ctx.voice_client.play(source)

  
    # Plays the next song in the queue
    async def play_next(self, ctx):
        if not self.queue.empty():
            song = self.queue.get()  # Get the next Song instance from the queue
            print('This is the queue object: ' + str(self.queue))
    
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song.url, download=False)  # Extract the URL from the Song instance
                url2 = info['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, method='fallback')
                await ctx.send(f"Playing: {info['title']}")
    
                # Check if the bot is connected to a voice channel
                if not ctx.voice_client:
                    await ctx.invoke(ctx.bot.get_command("join"))
    
                # Play the audio and schedule the next song to play
                ctx.voice_client.play(source, after=lambda e: ctx.bot.loop.create_task(self.play_next(ctx)))
    
        else:
            # Queue is empty, stop playing and disconnect from the voice channel
            await ctx.voice_client.disconnect()



    # ENQUEUES song to playlist
    async def enqueue(self, ctx, song):
        # Add the URL to the queue
        if song is None:
          return
        self.queue.put(song)
        await ctx.send(f"Enqueued song: {song.title}")

        # Start playing if the bot is not already playing
        # if not ctx.voice_client.is_playing():
        #     await self.play_next(ctx)
          
        #await ctx.voice_client.disconnect()
  
    def is_playing(self, ctx):
        return ctx.voice_client and ctx.voice_client.is_playing()
      
    def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    # Enqueues the video audio from an entire playlist from Youtube
    async def enqueue_youtube_playlist(self, ctx, url):
        ydl_opts = {
            'dump_single_json': True,
            'format': 'bestaudio/best',
            'extract_flat': 'in_playlist',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
            if 'entries' in playlist_info:
                playlist_songs = playlist_info['entries']
    
                if playlist_songs:
                    for song_info in playlist_songs:
                        try:
                            # Extracts song title, URL, and duration from the playlist
                            song_title = song_info['title']
                            song_url = song_info['url']
                            song_duration = song_info['duration']
    
                            # Creates a Song instance for each song in the playlist
                            song = Song(title=song_title, url=song_url, duration=song_duration)
    
                            # Enqueues each song from the playlist
                            await self.enqueue(ctx=ctx, song=song)
                        except KeyError as e:
                            # Handles the KeyError by printing an error message and continuing to the next song
                            print(f"Skipping song due to missing key: {e}")
            else:
                await ctx.send("Couldn't extract playlist information.")

    async def enqueue_url(self, ctx, url):
        ydl_opts = {
            'dump_single_json': True,
            'format': 'bestaudio/best',
        }
    
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            song_info = ydl.extract_info(url, download=False)
            try:
                # Extract song title, URL, and duration from the song_info
                song_title = song_info['title']
                song_url = song_info['url']
                song_duration = song_info['duration']
    
                # Create a Song instance for the song
                song = Song(title=song_title, url=song_url, duration=song_duration)
    
                # Enqueue the single song
                await self.enqueue(ctx=ctx, song=song)
            except KeyError as e:
                # Handle the KeyError by sending an error message
                await ctx.send(f"Error: Missing key '{e}'. The provided URL may not be a valid YouTube video or audio.")

# Searches YouTube for songs matching the query and returns the top 5 results
async def search_youtube(ctx, query):
    ydl_opts = {
        'dump_json': True,
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{query}", download=False)
        songs = []  # List to store instances of the Song class
        for i, item in enumerate(info['entries'][:5]):
            song = Song(title=item['title'], url=item['webpage_url'], duration=item['duration'])
            songs.append(song)

    # Display the 5 searches as a selection menu on Discord
    embed = discord.Embed(title=f"Search results for '{query}'", description="Choose a song by clicking its corresponding number in the reactions:", color=discord.Color.blue())
    for i, song in enumerate(songs):
        embed.add_field(name=f"{i+1}. {song.title}", value=f"Duration: {song.duration // 60}:{song.duration % 60 :02d}", inline=False)
    sent_message =await ctx.send(embed=embed)

    for i in range(1, 6):
        await sent_message.add_reaction(str(i) + "\N{variation selector-16}\N{combining enclosing keycap}")
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['1\N{variation selector-16}\N{combining enclosing keycap}', '2\N{variation selector-16}\N{combining enclosing keycap}', '3\N{variation selector-16}\N{combining enclosing keycap}', '4\N{variation selector-16}\N{combining enclosing keycap}', '5\N{variation selector-16}\N{combining enclosing keycap}']
    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        index = int(str(reaction.emoji)[0]) - 1
        return songs[index]  # Return the selected Song instance
    except asyncio.TimeoutError:
        await ctx.send('You did not react in time.')
