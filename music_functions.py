import discord
import os
import yt_dlp
import logging
import ffmpeg
import asyncio
import queue

class Music:
    def __init__(self):
        self.queue = queue.Queue()

    def convert_to_audio(self, video_file, audio_file):
        (
            ffmpeg.input(video_file)
            .output(audio_file, format="mp3", acodec="libmp3lame")
            .overwrite_output()
            .run()
        )
  
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


    async def play_next(self, ctx):
        if not self.queue.empty():
            url = self.queue.get()

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, method='fallback')
                await ctx.send(f"Playing: {info['title']}")
                
                # Play the audio and call play_next when finished
                ctx.voice_client.play(source)

        else:
            # Queue is empty, stop playing
            await ctx.voice_client.disconnect()


    # ENQUEUES song to playlist
    async def enqueue(self, ctx, url):
        # Add the URL to the queue
        self.queue.put(url)
        await ctx.send(f"Enqueued song")

        # Start playing if the bot is not already playing
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)
          
        #await ctx.voice_client.disconnect()
  
    def is_playing(self, ctx):
        return ctx.voice_client and ctx.voice_client.is_playing()

# Searches first 5 search options of given query
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
        message = ""
        urls = []
        for i, item in enumerate(info['entries'][:5]):
            duration_in_seconds = item['duration']
            minutes = duration_in_seconds // 60
            seconds = duration_in_seconds % 60
            message += f"{i+1}. {item['title']} (**{minutes:02d}:{seconds:02d}**)\n"
            urls.append(item['webpage_url'])
        sent_message = await ctx.send(message)
        for i in range(1, 6):
            await sent_message.add_reaction(str(i) + "\N{variation selector-16}\N{combining enclosing keycap}")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1\N{variation selector-16}\N{combining enclosing keycap}', '2\N{variation selector-16}\N{combining enclosing keycap}', '3\N{variation selector-16}\N{combining enclosing keycap}', '4\N{variation selector-16}\N{combining enclosing keycap}', '5\N{variation selector-16}\N{combining enclosing keycap}']
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
            index = int(str(reaction.emoji)[0]) - 1
            #await ctx.send(urls[index])
            return urls[index]
        except asyncio.TimeoutError:
            await ctx.send('You did not react in time.')
