import os
import random
import re
import aiofiles
import aiohttp

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch

from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


def clear(text):
    words = text.split(" ")
    title = ""
    for word in words:
        if len(title) + len(word) < 50:
            title += " " + word
    return title.strip()


async def gen_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"

    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub("\W+", " ", result.get("title", "Unknown")).title()
            duration = result.get("duration", "0:00")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "0 Views")
            channel = result.get("channel", {}).get("name", "Unknown")

        # download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # base image
        base = Image.open(f"cache/thumb{videoid}.png").convert("RGB")
        base = changeImageSize(1280, 720, base)

        # 🔥 create blurred background
        bg = base.copy().filter(ImageFilter.GaussianBlur(25))
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.6)

        # glass overlay
        overlay = Image.new("RGBA", bg.size, (255, 255, 255, 40))
        bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

        draw = ImageDraw.Draw(bg)

        # fonts (make sure to add font file)
        font_big = ImageFont.truetype("assets/font.ttf", 60)
        font_small = ImageFont.truetype("assets/font2.ttf", 35)
        font_tiny = ImageFont.truetype("assets/font2.ttf", 28)

        # 🎯 circular thumbnail
        thumb_size = 300
        thumb = base.resize((thumb_size, thumb_size))

        mask = Image.new("L", (thumb_size, thumb_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, thumb_size, thumb_size), fill=255)

        thumb.putalpha(mask)

        # position
        thumb_x = 80
        thumb_y = int((720 - thumb_size) / 2)

        bg.paste(thumb, (thumb_x, thumb_y), thumb)

        # 📝 TEXT
        title_text = clear(title)
        text_x = 420
        text_y = 250

        draw.text((text_x, text_y), title_text, font=font_big, fill="white")

        # subtitle
        draw.text(
            (text_x, text_y + 80),
            f"{channel} • {views}",
            font=font_small,
            fill=(200, 200, 200),
        )

        # ⏱ progress bar
        bar_x = text_x
        bar_y = text_y + 150
        bar_width = 650

        draw.line((bar_x, bar_y, bar_x + bar_width, bar_y), fill=(180, 180, 180), width=6)
        draw.ellipse(
            (bar_x + 100, bar_y - 6, bar_x + 112, bar_y + 6),
            fill="white",
        )

        # duration
        draw.text((bar_x, bar_y + 15), "0:00", font=font_tiny, fill="white")
        draw.text(
            (bar_x + bar_width - 80, bar_y + 15),
            duration,
            font=font_tiny,
            fill="white",
        )

        # 🎧 branding
        branding = "˹ ɪɴꜰɪɴɪᴛʏ ✘ ɴᴇᴛᴡᴏʀᴋ˼ 🎧"
        draw.text(
            (600, 650),
            branding,
            font=font_tiny,
            fill=(220, 220, 220),
            anchor="mm",
        )

        # save
        os.remove(f"cache/thumb{videoid}.png")
        bg.convert("RGB").save(f"cache/{videoid}.png")

        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
