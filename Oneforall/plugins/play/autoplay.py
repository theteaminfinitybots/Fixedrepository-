import random
from pyrogram import filters
from pyrogram.types import CallbackQuery

from config import BANNED_USERS
from Oneforall import app, YouTube
from Oneforall.utils.stream.stream import stream

# ───────── AUTOPLAY STORAGE ─────────
AUTO_PLAY = {}

# Sample songs
AUTO_SONGS = [
    "lofi hip hop",
    "arijit singh songs",
    "kk hits",
    "atif aslam songs",
    "english pop hits",
    "sad songs hindi",
]

# ───────── CALLBACK HANDLER ─────────
@app.on_callback_query(filters.regex("AUTO_PLAY_TOGGLE") & ~BANNED_USERS)
async def autoplay_toggle(client, CallbackQuery: CallbackQuery):
    chat_id = CallbackQuery.message.chat.id
    user_id = CallbackQuery.from_user.id

    if chat_id in AUTO_PLAY:
        AUTO_PLAY.pop(chat_id)
        await CallbackQuery.answer("❌ Autoplay Disabled", show_alert=True)
        return

    AUTO_PLAY[chat_id] = True
    await CallbackQuery.answer("✅ Autoplay Enabled", show_alert=True)

    # Start autoplay instantly
    await start_autoplay(CallbackQuery)


# ───────── START AUTOPLAY ─────────
async def start_autoplay(CallbackQuery):
    chat_id = CallbackQuery.message.chat.id

    if chat_id not in AUTO_PLAY:
        return

    try:
        query = random.choice(AUTO_SONGS)
        details, track_id = await YouTube.track(query)

        await stream(
            None,
            CallbackQuery.message,
            CallbackQuery.from_user.id,
            details,
            chat_id,
            "Autoplay",
            CallbackQuery.message.chat.id,
            streamtype="youtube",
        )

    except Exception as e:
        print(f"AUTOPLAY ERROR: {e}")


# ───────── AUTO NEXT TRACK ─────────
async def auto_next(chat_id, message):
    if chat_id not in AUTO_PLAY:
        return

    try:
        query = random.choice(AUTO_SONGS)
        details, track_id = await YouTube.track(query)

        await stream(
            None,
            message,
            0,
            details,
            chat_id,
            "Autoplay",
            message.chat.id,
            streamtype="youtube",
        )

    except Exception as e:
        print(f"AUTOPLAY NEXT ERROR: {e}")