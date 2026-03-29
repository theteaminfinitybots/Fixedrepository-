import random
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from Oneforall import app, YouTube
from Oneforall.utils.database import is_autoplay, set_autoplay
from Oneforall.utils.stream.queue import put_queue
from Oneforall.misc import db


# ───────── SMALL CAPS FUNCTION ───────── #

def small_caps(text: str) -> str:
    normal = "abcdefghijklmnopqrstuvwxyz"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    table = str.maketrans(normal, small)
    return text.lower().translate(table)


# ───────── AUTOPLAY NEXT ───────── #

async def auto_next(chat_id: int, client):
    try:
        autoplay = await is_autoplay(chat_id)
        if not autoplay:
            return

        if not db.get(chat_id):
            return

        last = db[chat_id][0]
        query = last.get("title")

        if not query:
            return

        # better search query
        query = f"{query} song"

        results = await YouTube.search(query)

        if not results:
            return

        data = random.choice(results)

        title = data["title"]
        vidid = data["id"]
        duration = data["duration"]

        await put_queue(
            chat_id,
            last["chat_id"],
            f"vid_{vidid}",
            title,
            duration,
            "ᴀᴜᴛᴏᴘʟᴀʏ",
            vidid,
            0,
            "audio",
        )

        await client.send_message(
            chat_id=last["chat_id"],
            text=small_caps(f"autoplaying: {title}"),
        )

    except Exception as e:
        print(f"AUTOPLAY ERROR: {e}")


# ───────── TOGGLE BUTTON HANDLER ───────── #

@app.on_callback_query(filters.regex("AUTO_TOGGLE"))
async def autoplay_toggle(_, CallbackQuery: CallbackQuery):
    chat_id = CallbackQuery.message.chat.id

    current = await is_autoplay(chat_id)

    if current:
        await set_autoplay(chat_id, False)
        status = False
        text = small_caps("autoplay disabled")
    else:
        await set_autoplay(chat_id, True)
        status = True
        text = small_caps("autoplay enabled")

    # dynamic button
    button_text = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏɴ" if status else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏꜰꜰ"

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton(button_text, callback_data="AUTO_TOGGLE")]]
    )

    try:
        await CallbackQuery.message.edit_reply_markup(reply_markup=buttons)
    except:
        pass

    await CallbackQuery.answer(text, show_alert=True)


# ───────── BUTTON FUNCTION (USE IN play.py) ───────── #

async def get_autoplay_button(chat_id):
    status = await is_autoplay(chat_id)
    text = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏɴ" if status else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ: ᴏꜰꜰ"

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text, callback_data="AUTO_TOGGLE")]]
    )