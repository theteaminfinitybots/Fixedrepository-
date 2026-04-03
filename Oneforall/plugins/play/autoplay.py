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

async def auto_next(chat_id: int, last, _):
    try:
        # check if autoplay enabled
        if not await get_autoplay(chat_id):
            return

        query = last.get("title")

        if not query:
            return

        # improve search
        query = f"{query} song"

        # emoji requested by user
        await app.send_message(
            chat_id=last["chat_id"],
            text="🔍",
        )

        results = await YouTube.search(query)
        if not results:
            return

        data = random.choice(results)

        vidid = data["id"]

        try:
            details, track_id = await YouTube.track(vidid, True)
        except:
            return

        user_id = last.get("user_id", 0)
        user_name = "ᴀᴜᴛᴏᴘʟᴀʏ"
        original_chat_id = last.get("chat_id")

        await put_queue(
            chat_id,
            original_chat_id,
            f"vid_{vidid}",
            details["title"],
            details["duration_min"],
            user_name,
            vidid,
            user_id,
            "audio",
        )

        await app.send_message(
            chat_id=last["chat_id"],
            text="autoplayinh",
        )

        return True

    except Exception as e:
        print(f"AUTOPLAY ERROR: {e}")
        return False


# ───────── TOGGLE BUTTON ───────── #

@app.on_callback_query(filters.regex("AUTOPLAY_TOGGLE"))
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
        [[InlineKeyboardButton(btn_text, callback_data="AUTOPLAY_TOGGLE")]]
    )

    try:
        await CallbackQuery.message.edit_reply_markup(reply_markup=buttons)
    except:
        pass

    await CallbackQuery.answer(text, show_alert=True)
