import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from yt_dlp import YoutubeDL

# Add your API credentials here
API_ID = '23119127'
API_HASH = '12101cd9bd354903c734bdec6faafe2c'
BOT_TOKEN = '5934094650:AAEOlEZyrox0nqefqcdPyMGH9Gk9hTS80mI'

# Create the Pyrogram client
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)

# Directory for downloaded audio files
if not os.path.exists("downloads"):
    os.makedirs("downloads")


# Download YouTube video as audio
def download_audio(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


# Start the bot
@app.on_message(filters.command("play") & filters.private)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide a YouTube link.")
        return

    url = message.command[1]
    await message.reply("Downloading audio...")
    
    try:
        audio_file = download_audio(url)
        await message.reply(f"Downloaded: {audio_file}")

        # Join the voice chat and start playing
        chat_id = message.chat.id
        await pytgcalls.join_group_call(chat_id, audio_file)
        await message.reply("Playing music in the voice chat.")

    except Exception as e:
        await message.reply(f"Error: {e}")


# Handle pytgcalls updates
@pytgcalls.on_stream_end()
async def on_stream_end(client: Client, update: Update):
    chat_id = update.chat_id
    await pytgcalls.leave_group_call(chat_id)
    print(f"Stream ended in {chat_id}")


# Run the app and pytgcalls
if __name__ == "__main__":
    pytgcalls.start()
    app.run()
