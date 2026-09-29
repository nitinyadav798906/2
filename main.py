import os
import re
import sys
import json
import time
import asyncio
import random
import shutil

from logs import logging
import helper as helper
from vars import API_ID, API_HASH, BOT_TOKEN

from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait

# Bot client setup
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=16
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

# External Downloader Setup (Aria2c for fast downloading)
SPEED_FLAGS = '--external-downloader aria2c --external-downloader-args "-x 16 -s 16 -k 1M"' if shutil.which("aria2c") else '--concurrent-fragments 16'

async def show_random_emojis(message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻‍❄️', '☁️', '🚹', '🚺', '🐠', '🦋']
    try:
        return await message.reply_text(' '.join(random.choices(emojis, k=1)))
    except Exception:
        return None

@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text("Please upload the cookies file (.txt format).", quote=True)
    try:
        input_message: Message = await client.listen(m.chat.id, timeout=60)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        downloaded_path = await input_message.download()
        with open(downloaded_path, "r", encoding="utf-8") as uploaded_file:
            cookies_content = uploaded_file.read()

        with open(cookies_file_path, "w", encoding="utf-8") as target_file:
            target_file.write(cookies_content)

        if os.path.exists(downloaded_path):
            os.remove(downloaded_path)

        await input_message.reply_text("✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`.")
    except asyncio.TimeoutError:
        await m.reply_text("⏰ Timeout! Please try again.")
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
        "𝐇𝐞𝐥𝐥𝐨 𝐃𝐞𝐚𝐫 👋!\n\n➠ 𝐈 𝐚𝐦 𝐚 𝐓𝐞𝐱𝐭 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭\n\n"
        "➠ Can Extract Videos & PDFs From Your Text File and Upload to Telegram!\n\n"
        "➠ For Guide Use Command /help 📖\n\n➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : 𝙎𝘼Iℕ🇮 𝘽𝙊𝙏𝙎 🦁"
    )
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=random_image_url,
        caption=caption,
        reply_markup=keyboard
    )

@bot.on_message(filters.command(["drm"]))
async def drm_txt_handler(bot: Client, m: Message):
    editable = await m.reply_text("**🔹Hi I am Powerful TXT Downloader📥 Bot.\n🔹Send me the txt file and wait.**")
    try:
        input_msg: Message = await bot.listen(editable.chat.id, timeout=120)
        x = await input_msg.download()
        await input_msg.delete(True)
    except asyncio.TimeoutError:
        await editable.edit("⏰ **Timeout! File not received.**")
        return

    file_name, _ = os.path.splitext(os.path.basename(x))
    pdf_count, img_count, zip_count, other_count = 0, 0, 0, 0
    links = []

    try:        
        with open(x, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().splitlines()
        
        for line in content:
            if "://" in line:
                if ":" in line and not line.startswith("http"):
                    parts = line.split(":", 1)
                    title = parts[0].strip()
                    url = parts[1].strip()
                else:
                    title = "Video"
                    url = line.strip()

                links.append((title, url))

                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif ".zip" in url:
                    zip_count += 1
                else:
                    other_count += 1

        if os.path.exists(x):
            os.remove(x)
    except Exception:
        await m.reply_text("<pre><code>🔹Invalid file input.</code></pre>")
        if os.path.exists(x):
            os.remove(x)
        return

    if not links:
        await editable.edit("⚠️ **No valid links found in the text file.**")
        return

    try:
        await editable.edit(f"**🔹Total 🔗 links found are {len(links)}\n\n🔹Img : {img_count}  🔹PDF : {pdf_count}\n🔹ZIP : {zip_count}  🔹Other : {other_count}\n\n🔹Send Index number from where you want to start (e.g. 1).**")
        input0: Message = await bot.listen(editable.chat.id, timeout=60)
        raw_text = input0.text
        await input0.delete(True)
                
        await editable.edit("**🔹Enter Your Batch Name\n🔹Send 1 to use default.**")
        input1: Message = await bot.listen(editable.chat.id, timeout=60)
        raw_text0 = input1.text
        await input1.delete(True)
        b_name = file_name.replace('_', ' ') if raw_text0 == '1' else raw_text0

        await editable.edit("**╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏ🇱🇺🇹🇮🇴🇳❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`🦋🇸‌🇦‌🇮‌🇳‌🇮‌🦋`]⚡⌋━━➣**")
        input2: Message = await bot.listen(editable.chat.id, timeout=60)
        raw_text2 = input2.text
        quality = f"{raw_text2}p"
        await input2.delete(True)
        
        res_dict = {"144": "256x144", "240": "426x240", "360": "640x360", "480": "854x480", "720": "1280x720", "1080": "1920x1080"}
        res = res_dict.get(raw_text2, "UN")

        await editable.edit("**🔹Enter Credit Name\n🔹Send 1 to use default**")
        input3: Message = await bot.listen(editable.chat.id, timeout=60)
        raw_text3 = input3.text
        await input3.delete(True)
        CR = 'SKYSTAR' if raw_text3 == '1' else raw_text3

        await editable.edit("**🔹Enter Your Token/Header\n🔹Send /anything to skip**")
        input4: Message = await bot.listen(editable.chat.id, timeout=60)
        await input4.delete(True)

        await editable.edit("**🔹Send Video Thumb URL or photo\n🔹Send /d or No to skip**")
        input6 = await bot.listen(editable.chat.id, timeout=60)
        raw_text6 = input6.text if input6.text else ""
        await input6.delete(True)

        if input6.photo:
            thumb = await input6.download()
        elif raw_text6.startswith(("http://", "https://")):
            os.system(f"wget '{raw_text6}' -O 'thumb.jpg'")
            thumb = "thumb.jpg"
        else:
            thumb = "/d"
            
        await editable.delete()
    except asyncio.TimeoutError:
        await editable.edit("⏰ **Timeout! Batch process cancelled.**")
        return

    await m.reply_text(f"__**🎯 Target Batch : {b_name}**__")

    failed_count = 0
    try:
        start_index = int(raw_text) - 1
    except ValueError:
        start_index = 0

    count = start_index + 1

    for i in range(start_index, len(links)):
        emoji_message = None
        prog = None
        
        try:
            raw_title, raw_url = links[i]
            Vxy = raw_url.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = Vxy if Vxy.startswith("http") else "https://" + Vxy
            link0 = url

            name1 = re.sub(r'[()_\t:/\+#|@*\.]', '', raw_title).strip()
            name = f'{name1[:60]}' if name1 else f"Video_{count}"

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            
            if "xhcdn.com" in url or ".m3u8" in url:
                cmd = f'yt-dlp {SPEED_FLAGS} --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" --referer "https://www.xvideos.com/" --no-check-certificates --hls-use-mpegts -f "bestvideo+bestaudio/best" "{url}" -o "{name}.mp4"'
            elif "jw-prod" in url:
                cmd = f'yt-dlp {SPEED_FLAGS} -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
                cmd = f'yt-dlp {SPEED_FLAGS} --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cookie_arg = f'--cookies {cookies_file_path}' if os.path.exists(cookies_file_path) else ''
                cmd = f'yt-dlp {SPEED_FLAGS} {cookie_arg} -f "{ytf}" "{url}" -o "{name}.mp4"'
            else:
                cmd = f'yt-dlp {SPEED_FLAGS} -f "{ytf}" "{url}" -o "{name}.mp4"'

            cc = f'——— ✦ {str(count).zfill(3)} ✦ ———\n\n📦 **Title :** `{name1}`\n├── **Extension :** .mp4\n├── **Resolution :** [{res}]\n\n📚 **Course :** {b_name}\n\n🌟 **Extracted By :** {CR}'

            if "drive" in url:
                while True:
                    try:
                        ka = await helper.download(url, name)
                        await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc)
                        count += 1
                        if os.path.exists(ka):
                            os.remove(ka)
                        break
                    except FloodWait as e:
                        await asyncio.sleep(e.x + 1)
                    except Exception as ex:
                        raise ex
            else:
                remaining_links = len(links) - count
                progress = (count / len(links)) * 100
                emoji_message = await show_random_emojis(m)
                
                Show = f"🚀 **Progress:** {progress:.2f}%\n" \
                       f"🔗 **Index:** {count}/{len(links)}\n" \
                       f"🖇️ **Remaining:** {remaining_links}\n" \
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                       f"⚡ **Downloading & Fast Uploading...⏳**\n" \
                       f"💃 **Credit:** {CR}\n" \
                       f"📚 **Batch:** {b_name}\n" \
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                       f"📚 **Title:** {name}\n" \
                       f"🍁 **Quality:** {quality}\n" \
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                       f"🛑 Send /stop to cancel"
                
                prog = await m.reply_text(Show, disable_web_page_preview=True)
                
                res_file = await helper.download_video(url, cmd, name)
                
                if emoji_message:
                    try: await emoji_message.delete()
                    except Exception: pass
                
                # Handling FloodWait during Send Video
                uploaded = False
                while not uploaded:
                    try:
                        await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                        uploaded = True
                    except FloodWait as e:
                        await asyncio.sleep(e.x + 2)
                    except Exception as e:
                        raise e
                
                if os.path.exists(res_file):
                    os.remove(res_file)
                
                count += 1
                await asyncio.sleep(1.5)  # Safe delay to prevent rate limit

        except Exception as e:
            await m.reply_text(
                f'⚠️ **Downloading Failed** ⚠️\n'
                f'**Name** =>> `{str(count).zfill(3)} {name1}`\n'
                f'**Url** =>> {link0}\n\n'
                f'<pre><i><b>Failed Reason: {str(e)}</b></i></pre>', 
                disable_web_page_preview=True
            )
            count += 1
            failed_count += 1
            if emoji_message:
                try: await emoji_message.delete()
                except Exception: pass
            if prog:
                try: await prog.delete()
                except Exception: pass
            await asyncio.sleep(1)
            continue

    if thumb != "/d" and os.path.exists(thumb):
        os.remove(thumb)

    await m.reply_text(f"⋅ ─ Total failed links: {failed_count} ─ ⋅")
    await m.reply_text(f"✨ **BATCH** » {b_name}✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")

bot.run()
