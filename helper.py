import os
import time
import asyncio
import subprocess
from pyrogram.types import Message

async def download(url, name):
    # Google drive ya direct download ke liye
    cmd = f'wget "{url}" -O "{name}"'
    subprocess.run(cmd, shell=True)
    return name

async def download_video(url, cmd, name):
    # yt-dlp command run karne ke liye
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    # Check karein konsi file bani hai (.mp4, .mkv, etc.)
    for file in os.listdir('.'):
        if file.startswith(name) and not file.endswith('.aria2'):
            return file
    return f"{name}.mp4"

async def send_vid(bot, m: Message, cc, filename, thumb, name, prog):
    try:
        thumb_path = None if thumb == "/d" else thumb
        
        await bot.send_video(
            chat_id=m.chat.id,
            video=filename,
            caption=cc,
            supports_streaming=True,
            thumb=thumb_path
        )
    except Exception as e:
        await m.reply_text(f"⚠️ **Upload Failed:** {str(e)}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
        if thumb_path and os.path.exists(thumb_path) and thumb_path != "thumb.jpg":
            os.remove(thumb_path)
