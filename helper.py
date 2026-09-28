import os
import time
import asyncio
import subprocess
from pyrogram.types import Message

# Video se Duration, Width, Height nikalne ka function
def get_video_attributes(file_path):
    duration = 0
    width = 1280
    height = 720
    try:
        cmd = f'ffprobe -v error -show_entries format=duration -show_entries stream=width,height -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').splitlines()
        if len(output) >= 3:
            width = int(output[0])
            height = int(output[1])
            duration = int(float(output[2]))
        elif len(output) == 1:
            duration = int(float(output[0]))
    except Exception as e:
        print(f"Metadata error: {e}")
    return duration, width, height

# Auto Thumbnail generate karne ka function
def take_ss(video_path):
    thumb_path = f"{video_path}.jpg"
    try:
        cmd = f'ffmpeg -i "{video_path}" -ss 00:00:05 -vframes 1 "{thumb_path}" -y'
        subprocess.run(cmd, shell=True, check=True)
        if os.path.exists(thumb_path):
            return thumb_path
    except Exception as e:
        print(f"Thumbnail error: {e}")
    return None

# Real-time Upload Progress Bar (Speed, Size, ETA)
async def progress_bar(current, total, ud_type, message, start_time, title):
    now = time.time()
    diff = now - start_time
    if round(diff % 3.0) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        time_to_completion = round((total - current) / speed) if speed > 0 else 0
        
        tmp = f"**{ud_type} Status:**\n\n"
        tmp += f"📚 **Title:** `{title}`\n\n"
        tmp += f"📊 **Progress:** {percentage:.2f}%\n"
        tmp += f"🚀 **Speed:** {humanbytes(speed)}/s\n"
        tmp += f"💾 **Size:** {humanbytes(current)} / {humanbytes(total)}\n"
        tmp += f"⏱️ **ETA:** {time_formatter(time_to_completion)}\n"
        
        try:
            await message.edit(tmp)
        except Exception:
            pass

def humanbytes(size):
    if not size:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def time_formatter(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# Complete Video Sending Function
async def send_vid(bot, m, cc, filename, thumb, name, prog):
    await prog.edit("📤 **Starting Video Upload...**")
    start_time = time.time()
    
    # 1. Video Duration aur Resolution nikalein
    duration, width, height = get_video_attributes(filename)
    
    # 2. Auto Thumbnail Handle Karein
    generated_thumb = None
    if thumb == "/d" or not thumb or not os.path.exists(str(thumb)):
        generated_thumb = take_ss(filename)
        final_thumb = generated_thumb
    else:
        final_thumb = thumb

    try:
        await bot.send_video(
            chat_id=m.chat.id,
            video=filename,
            caption=cc,
            supports_streaming=True,
            duration=duration,
            width=width,
            height=height,
            thumb=final_thumb,
            progress=progress_bar,
            progress_args=("📤 Uploading", prog, start_time, name)
        )
    except Exception as e:
        await m.reply_text(f"⚠️ Upload Error: `{str(e)}`")
    finally:
        # File Cleanup
        if os.path.exists(filename):
            os.remove(filename)
        if generated_thumb and os.path.exists(generated_thumb):
            os.remove(generated_thumb)
