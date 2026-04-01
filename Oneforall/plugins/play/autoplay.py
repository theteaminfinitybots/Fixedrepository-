import random
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from Oneforall import app, YouTube
from Oneforall.utils.database import get_autoplay, set_autoplay
from Oneforall.utils.stream.queue import put_queue
from Oneforall.misc import db


# ───────── SMALL CAPS ───────── #

def sc(text: str) -> str:
    normal = "abcdefghijklmnopqrstuvwxyz"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    return text.lower().translate(str.maketrans(normal, small))


# ───────── AUTOPLAY NEXT ───────── #

async def auto_next(chat_id: int, client):
    try:
        # check if autoplay enabled
        if not await get_autoplay(chat_id):
            return

        # check queue exists
        if not db.get(chat_id):
            return

        last = db[chat_id][0]
        query = last.get("title")

        if not query:
            return

        # improve search
        query = f"{query} song"

        results = await YouTube.search(query)
        if not results:
            return

        data = random.choice(results)

        title = data["title"]
        vidid = data["id"]

        # 🔥 FIX: get playable stream link
        n, link = await YouTube.video(vidid, True)

        if n == 0:
            return

        duration = data.get("duration", "0:00")

        # 🔥 FIX: use link instead of vid id
        await put_queue(
            chat_id,
            last["chat_id"],
            link,
            title,
            duration,
            "ᴀᴜᴛᴏᴘʟᴀʏ",
            vidid,
            0,
            "audio",
        )

        await client.send_message(
            chat_id=last["chat_id"],
            text=sc(f"autoplaying: {title}"),
        )

    except Exception as e:
        print(f"AUTOPLAY ERROR: {e}")


# ───────── TOGGLE BUTTON ───────── #

@app.on_callback_query(filters.regex("AUTO_TOGGLE"))
async def autoplay_toggle(_, CallbackQuery: CallbackQuery):
    chat_id = CallbackQuery.message.chat.id

    current = await get_autoplay(chat_id)

    if current:
        await set_autoplay(chat_id, False)
        status = False
        text = sc("autoplay disabled")
    else:
        await set_autoplay(chat_id, True)
        status = True
        text = sc("autoplay enabled")

    # dynamic button text
    btn_text = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏɴ" if status else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏꜰꜰ"

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton(btn_text, callback_data="AUTO_TOGGLE")]]
    )

    try:
        await CallbackQuery.message.edit_reply_markup(reply_markup=buttons)
    except:
        pass

    await CallbackQuery.answer(text, show_alert=True)
