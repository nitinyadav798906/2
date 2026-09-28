import os
import re
import sys
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
import helper as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

# Bot client setup
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")
m_file_path = "main.py"

BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot")]])
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot"),
            InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl"),
        ],
    ]
)

image_urls = [
    "https://tinypic.host/images/2025/02/07/IMG_20250207_224444_975.jpg",
    "https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png",
]

async def show_random_emojis(message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻‍❄️', '☁️', '🚹', '🚺', '🐠', '🦋']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message

@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text("Please upload the cookies file (.txt format).", quote=True)
    try:
        input_message: Message = await client.listen(m.chat.id)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        downloaded_path = await input_message.download()
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text("✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`.")
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["sky"]))
async def sky_txt_filter(client: Client, message: Message):
    editable = await message.reply_text("<blockquote>📂 **Send the .txt file** to extract only Title, `.m3u8`, and `.mp4` links.</blockquote>")
    
    input_msg: Message = await bot.listen(message.chat.id)
    if not input_msg.document or not input_msg.document.file_name.endswith(".txt"):
        await editable.edit("🚨 **Error:** Please send a valid `.txt` file.")
        return

    file_path = await input_msg.download()
    await input_msg.delete(True)
    await editable.edit("🔄 **Processing file, filtering links...**")

    filtered_lines = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            match = re.search(r'https?://\S+', line_str)
            if match:
                url = match.group(0)
                
                if ".m3u8" in url.lower() or ".mp4" in url.lower():
                    title_part = line_str[:match.start()].strip()
                    title_part = re.sub(r'[:|\-–]+$', '', title_part).strip()
                    
                    if title_part:
                        filtered_lines.append(f"{title_part}: {url}")
                    else:
                        filtered_lines.append(url)

        os.remove(file_path)

        if not filtered_lines:
            await editable.edit("⚠️ **No `.m3u8` or `.mp4` links found in the file.**")
            return

        output_filename = f"filtered_{input_msg.document.file_name}"
        output_path = os.path.join("downloads", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered_lines))

        await editable.delete(True)
        await message.reply_document(
            document=output_path,
            caption=f"✅ **Filtered File Ready!**\n\n📌 **Total Extracted Links:** `{len(filtered_lines)}`\n🎯 **Contains:** Title + `.m3u8` / `.mp4` URLs only."
        )
        
        if os.path.exists(output_path):
            os.remove(output_path)

    except Exception as e:
        await editable.edit(f"⚠️ **Error:** `{str(e)}`")
        if os.path.exists(file_path):
            os.remove(file_path)

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    editable = await message.reply_text("<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** to convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("🚨 **error**: Send valid text data")
        return

    text_data = input_message.text.strip()
    await input_message.delete()
    
    await editable.edit("**🔄 Send file name or send /d for default filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()
    await editable.delete()

    custom_file_name = 'txt_file' if raw_textn == '/d' else raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n\nYou can now download your content! 📥")
    os.remove(txt_file)

@bot.on_message(filters.command(["y2t"]))
async def youtube_to_txt(client, message: Message):
    editable = await message.reply_text("Send YouTube Website/Playlist link to convert into a .txt file")

    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': cookies_file_path if os.path.exists(cookies_file_path) else None
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            title = result.get('title', 'youtube_playlist' if 'entries' in result else 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(f"<pre><code>🚨 Error occurred: {str(e)}</code></pre>")
            return

    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry.get('url', '')
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result.get('url', '')
        videos.append(f"{video_title}: {url}")

    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<pre><code>{title}.txt</code></pre>\n'
    )
    os.remove(txt_file)

@bot.on_message(filters.command("getcookies") & filters.private)
async def getcookies_handler(client: Client, m: Message):
    try:
        await client.send_document(
            chat_id=m.chat.id,
            document=cookies_file_path,
            caption="Here is the `youtube_cookies.txt` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command("mfile") & filters.private)
async def getmfile_handler(client: Client, m: Message):
    try:
        await client.send_document(
            chat_id=m.chat.id,
            document=m_file_path,
            caption="Here is the `main.py` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["stop"]))
async def restart_handler(_, m):
    await m.reply_text("**🚦STOPPED🚦**", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, message: Message):
    random_image_url = random.choice(image_urls)
    caption = (
        "𝐇𝐞𝐥𝐥𝐨 𝐃𝐞𝐚𝐫 👋!\n\n➠ 𝐈 𝐚𝐦 𝐚 𝐓𝐞𝐱𝐭 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭\n\n➠ Can Extract Videos & PDFs From Your Text File and Upload to Telegram!\n\n➠ For Guide Use Command /help 📖\n\n➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : 𝙎𝘼Iℕ🇮 𝘽𝙊𝙏𝙎 🦁"
    )
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=random_image_url,
        caption=caption,
        reply_markup=keyboard
    )

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(f"<blockquote>The ID of this chat is:</blockquote>\n`{chat_id}`")

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    text = (
        f"╭────────────────╮\n"
        f"│✨ **__Your Telegram Info__**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else ''}`\n"
        f"├🔹**User ID :** @{update.from_user.username}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    await update.reply_text(        
        text=text,
        disable_web_page_preview=True,
        reply_markup=BUTTONSCONTACT
    )

@bot.on_message(filters.command(["help"]))
async def help_handler(client: Client, m: Message):
    await bot.send_message(m.chat.id, text=(
        f"╭━━━━━━━✦✧✦━━━━━━━╮\n"
        f"💥 𝙎𝘼Iℕ🇮 𝘽𝙊𝙏𝙎 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        f"╰━━━━━━━✦✧✦━━━━━━━╯\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
        f"📌 𝗠𝗮𝗶𝗻 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:\n\n"  
        f"➥ /start – Bot Status Check\n"
        f"➥ /drm – Extract from .txt (Auto)\n"
        f"➥ /sky – Filter TXT (Only Title + .m3u8/.mp4)\n"
        f"➥ /y2t – YouTube → .txt Converter\n"  
        f"➥ /t2t – Text → .txt Generator\n" 
        f"➥ /stop – Cancel Running Task\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰ \n" 
        f"⚙️ 𝗧𝗼𝗼𝗹𝘀 & 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀: \n\n" 
        f"➥ /cookies – Update YT Cookies\n" 
        f"➥ /id – Get Chat/User ID\n"  
        f"➥ /info – User Details\n"  
        f"➥ /logs – View Bot Activity\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"  
        f"💡 𝗡𝗼𝘁𝗲:\n\n"  
        f"• Send any link for auto-extraction\n"  
        f"• Supports batch processing\n\n"  
        f"╭────────⊰◆⊱────────╮\n"   
        f" ➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : [𝙎𝘼Iℕ🇮 𝘽𝙊𝙏𝙎](https://t.me/saini_contact_bot) 💻\n"
        f"╰────────⊰◆⊱────────╯\n"
        )
    )

@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    try:
        if os.path.exists("logs.txt"):
            sent = await m.reply_text("**📤 Sending logs...**")
            await m.reply_document(document="logs.txt")
            await sent.delete()
        else:
            await m.reply_text("⚠️ `logs.txt` not found.")
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

@bot.on_message(filters.command(["drm"]))
async def drm_txt_handler(bot: Client, m: Message):
    editable = await m.reply_text("**🔹Hi I am Powerful TXT Downloader📥 Bot.\n🔹Send me the txt file and wait.**")
    input_msg: Message = await bot.listen(editable.chat.id)
    x = await input_msg.download()
    await input_msg.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    
    pdf_count, img_count, zip_count, other_count = 0, 0, 0, 0
    
    try:    
        with open(x, "r") as f:
            content = f.read().splitlines()
        
        links = []
        for i in content:
            if "://" in i:
                url = i.split("://", 1)[1]
                links.append(i.split("://", 1))
                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif ".zip" in url:
                    zip_count += 1
                else:
                    other_count += 1
        os.remove(x)
    except Exception:
        await m.reply_text("<pre><code>🔹Invalid file input.</code></pre>")
        if os.path.exists(x):
            os.remove(x)
        return
    
    await editable.edit(f"**🔹Total 🔗 links found are {len(links)}\n\n🔹Img : {img_count}  🔹PDF : {pdf_count}\n🔹ZIP : {zip_count}  🔹Other : {other_count}\n\n🔹Send From where you want to download (e.g. 1).**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
            
    await editable.edit("**🔹Enter Your Batch Name\n🔹Send 1 to use default.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    b_name = file_name.replace('_', ' ') if raw_text0 == '1' else raw_text0

    await editable.edit("**╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏ🇱🇺🇹🇮🇴🇳❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`🦋🇸‌🇦‌🇮‌🇳‌🇮‌🦋`]⚡⌋━━➣**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete(True)
    
    res_dict = {"144": "256x144", "240": "426x240", "360": "640x360", "480": "854x480", "720": "1280x720", "1080": "1920x1080"}
    res = res_dict.get(raw_text2, "UN")

    await editable.edit("**🔹Enter Your Name\n🔹Send 1 to use default**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    CR = '[𝄟⃝‌🐬🇳‌ɪᴋʜɪʟ𝄟⃝🐬](https://t.me/+MdZ2996M2G43MWFl)' if raw_text3 == '1' else raw_text3

    await editable.edit("**🔹Enter Your Token/Header\n🔹Send /anything to skip**")
    input4: Message = await bot.listen(editable.chat.id)
    await input4.delete(True)

    await editable.edit("**🔹Send Video Thumb URL or photo\n🔹Send /d or No to skip**")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text if input6.text else ""
    await input6.delete(True)

    if input6.photo:
        thumb = await input6.download()
    elif raw_text6.startswith(("http://", "https://")):
        getstatusoutput(f"wget '{raw_text6}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "/d"
        
    await editable.delete()
    await m.reply_text(f"__**🎯Target Batch : {b_name}**__")

    failed_count = 0
    try:
        start_index = int(raw_text) - 1
    except ValueError:
        start_index = 0

    count = start_index + 1

    for i in range(start_index, len(links)):
        Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
        url = "https://" + Vxy
        link0 = "https://" + Vxy

        name1 = re.sub(r'[()_\t:/\+#|@*\.]', '', links[i][0]).replace("https", "").replace("http", "").strip()
        name = f'{name1[:60]}' if name1 else f"Video_{count}"

        if "youtu" in url:
            ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
        elif "embed" in url:
            ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
        else:
            ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
        
        if "xhcdn.com" in url or ".m3u8" in url:
            cmd = f'yt-dlp --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" --referer "https://www.xvideos.com/" --no-check-certificates --hls-use-mpegts -f "bestvideo+bestaudio/best" "{url}" -o "{name}.mp4"'
        elif "jw-prod" in url:
            cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
        elif "webvideos.classplusapp." in url:
            cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
        elif "youtube.com" in url or "youtu.be" in url:
            cookie_arg = f'--cookies {cookies_file_path}' if os.path.exists(cookies_file_path) else ''
            cmd = f'yt-dlp {cookie_arg} -f "{ytf}" "{url}" -o "{name}.mp4"'
        else:
            cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

        try:
            cc = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🎞️ Title :** `{name1}`\n**├── Extension :** .mp4\n**├── Resolution :** [{res}]\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'

            if "drive" in url:
                try:
                    ka = await helper.download(url, name)
                    await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc)
                    count += 1
                    if os.path.exists(ka):
                        os.remove(ka)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    continue    

            else:
                remaining_links = len(links) - count
                progress = (count / len(links)) * 100
                emoji_message = await show_random_emojis(m)
                Show = f"🚀𝐏ρη𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%\n┃\n" \
                       f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                       f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {remaining_links}\n" \
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                       f"**⚡DᴏWNʟᴏAᴅIɴGSᴛAʀTᴇD...⏳**\n┃\n" \
                       f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                       f"╰━📚𝐁𝐚𝐭𝐜𝐡 » {b_name}\n" \
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                       f"📚𝐓𝐢𝐭𝐥𝐞 » {name}\n┃\n" \
                       f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                       f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                       f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                       f"🛑**Send** /stop **to stop process**\n┃\n" \
                       f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [𝙎𝘼Iℕ🇮 𝘽𝙊𝙏𝙎🐦](https://t.me/+MdZ2996M2G43MWFl)"
                
                prog = await m.reply_text(Show, disable_web_page_preview=True)
                res_file = await helper.download_video(url, cmd, name)
                filename = res_file
                await emoji_message.delete()
                await prog.delete(True)
                await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                count += 1
                await asyncio.sleep(1)
            
        except Exception as e:
            await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}\n\n<pre><i><b>Failed Reason: {str(e)}</b></i></pre>', disable_web_page_preview=True)
            count += 1
            failed_count += 1
            continue

    await m.reply_text(f"⋅ ─ Total failed links: {failed_count} ─ ⋅")
    await m.reply_text(f"✨ **BATCH** » {b_name}✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")

@bot.on_message(filters.text & filters.private)
async def text_handler(bot: Client, m: Message):
    if m.from_user.is_bot:
        return
    
    links = m.text.strip()
    match = re.search(r'https?://\S+', links)
    if not match:
        return
    
    link = match.group(0)
        
    editable = await m.reply_text("<pre><code>**🔹Processing your link...\n🔁Please wait...⏳**</code></pre>")

    await editable.edit("╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏ🇱🇺🇹🇮🇴🇳❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`🦋🇸‌🇦‌🇮‌🇳‌🇮‌🦋`]⚡⌋━━➣ ")
    input2: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete(True)
    
    res_dict = {"144": "256x144", "240": "426x240", "360": "640x360", "480": "854x480", "720": "1280x720", "1080": "1920x1080"}
    res = res_dict.get(raw_text2, "UN")
          
    await editable.edit("<pre><code>Enter Token/Header\nSend /anything to skip</code></pre>")
    input4: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    await input4.delete(True)
    await editable.delete(True)
     
    thumb = "/d"
    try:
        url = link.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")

        name1 = re.sub(r'[()_\t:/\+#|@*\.]', '', links).replace("https", "").replace("http", "").strip()
        name = f'{name1[:60]}' if name1 else "Downloaded_Video"

        if "youtu" in url:
            ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
        elif "embed" in url:
            ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
        else:
            ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
        
        if "xhcdn.com" in url or ".m3u8" in url:
            cmd = f'yt-dlp --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" --referer "https://www.xvideos.com/" --no-check-certificates --hls-use-mpegts -f "bestvideo+bestaudio/best" "{url}" -o "{name}.mp4"'
        elif "jw-prod" in url:
            cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
        elif "webvideos.classplusapp." in url:
            cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
        elif "youtube.com" in url or "youtu.be" in url:
            cookie_arg = f'--cookies {cookies_file_path}' if os.path.exists(cookies_file_path) else ''
            cmd = f'yt-dlp {cookie_arg} -f "{ytf}" "{url}" -o "{name}.mp4"'
        else:
            cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

        try:
            cc = f'🎞️𝐓𝐢𝐭𝐥𝐞 » `{name} [{res}].mp4`\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » SAINI BOTS'
            
            show_message = await show_random_emojis(m)
            Show = f"**⚡DᴏWNʟᴏAᴅIɴGSᴛAʀTᴇD...⏳**\n\n" \
                   f"📚𝐓𝐢𝐭𝐥𝐞 » `{name}`\n" \
                   f"🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » `{quality}`\n" \
                   f'🔗𝐋𝐢𝐧𝐤 » <a href="{link}">**Original Link**</a>\n' \
                   f'🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n\n' \
                   f"🛑**Send** /stop **to stop process**\n" \
                   f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [𝙎𝘼Iℕ🇮 𝘽𝙊𝙏𝙎🐦](https://t.me/+MdZ2996M2G43MWFl)"
            
            prog = await m.reply_text(Show, disable_web_page_preview=True)
            res_file = await helper.download_video(url, cmd, name)
            filename = res_file
            await show_message.delete()
            await prog.delete(True)
            await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
            
        except Exception as e:
            await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{name}`\n**Url** =>> {link}\n\n<pre><i><b>Failed Reason: {str(e)}</b></i></pre>', disable_web_page_preview=True)

    except Exception as e:
        await m.reply_text(str(e))

bot.run()
