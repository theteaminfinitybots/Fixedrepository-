import asyncio
from datetime import datetime
from logging import getLogger
from typing import Dict, Set

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.raw import functions

from Oneforall import app
from Oneforall.utils.database import get_assistant
from Oneforall.core.mongo import mongodb

LOGGER = getLogger(__name__)

# ───────── CONFIG ─────────

VC_LOG_CHANNEL_ID = -1003634796457   # ✅ PUT YOUR VC LOG CHANNEL ID HERE

prefixes = [".", "!", "/", "@", "?", "'"]

# ───────── STATE ─────────

vc_active_users: Dict[int, Set[int]] = {}
active_vc_chats: Set[int] = set()
vc_logging_status: Dict[int, bool] = {}

vcloggerdb = mongodb.vclogger


# ───────── SMALL CAPS ─────────

def to_small_caps(text: str):
    mapping = {
        "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ","f":"ꜰ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ",
        "k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ","p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ",
        "u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ",
        "A":"ᴀ","B":"ʙ","C":"ᴄ","D":"ᴅ","E":"ᴇ","F":"ꜰ","G":"ɢ","H":"ʜ","I":"ɪ","J":"ᴊ",
        "K":"ᴋ","L":"ʟ","M":"ᴍ","N":"ɴ","O":"ᴏ","P":"ᴘ","Q":"ǫ","R":"ʀ","S":"s","T":"ᴛ",
        "U":"ᴜ","V":"ᴠ","W":"ᴡ","X":"x","Y":"ʏ","Z":"ᴢ"
    }
    return "".join(mapping.get(c, c) for c in text)


# ───────── DATABASE ─────────

async def load_vc_logger_status():
    async for doc in vcloggerdb.find({}):
        vc_logging_status[doc["chat_id"]] = doc["status"]
        if doc["status"]:
            asyncio.create_task(check_and_monitor_vc(doc["chat_id"]))


async def save_vc_logger_status(chat_id: int, status: bool):
    await vcloggerdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, "status": status}},
        upsert=True
    )


async def get_vc_logger_status(chat_id: int) -> bool:
    if chat_id in vc_logging_status:
        return vc_logging_status[chat_id]
    doc = await vcloggerdb.find_one({"chat_id": chat_id})
    return doc["status"] if doc else False


# ───────── COMMAND ─────────

@app.on_message(filters.command("vclogger", prefixes=prefixes) & filters.group)
async def vclogger_command(_, message: Message):
    chat_id = message.chat.id
    args = message.text.split()

    if len(args) == 1:
        status = await get_vc_logger_status(chat_id)
        await message.reply(
            f"🎧 <b>VC Logger:</b> <b>{to_small_caps(str(status))}</b>\n\n"
            "➤ <code>/vclogger on</code>\n"
            "➤ <code>/vclogger off</code>"
        )
        return

    arg = args[1].lower()

    if arg in ("on", "enable", "yes"):
        vc_logging_status[chat_id] = True
        await save_vc_logger_status(chat_id, True)
        asyncio.create_task(check_and_monitor_vc(chat_id))
        await message.reply("✅ <b>VC Logger Enabled</b>")

    elif arg in ("off", "disable", "no"):
        vc_logging_status[chat_id] = False
        await save_vc_logger_status(chat_id, False)
        active_vc_chats.discard(chat_id)
        vc_active_users.pop(chat_id, None)
        await message.reply("🚫 <b>VC Logger Disabled</b>")


# ───────── VC CORE ─────────

async def get_group_call_participants(userbot, peer):
    try:
        full = await userbot.invoke(
            functions.channels.GetFullChannel(channel=peer)
        )
        if not full.full_chat.call:
            return []

        call = full.full_chat.call
        res = await userbot.invoke(
            functions.phone.GetGroupParticipants(
                call=call,
                ids=[],
                sources=[],
                offset="",
                limit=100
            )
        )
        return res.participants
    except Exception:
        return []


async def monitor_vc_chat(chat_id: int):
    userbot = await get_assistant(chat_id)
    if not userbot:
        return

    while chat_id in active_vc_chats and await get_vc_logger_status(chat_id):
        peer = await userbot.resolve_peer(chat_id)
        participants = await get_group_call_participants(userbot, peer)

        new_users = {p.peer.user_id for p in participants if hasattr(p.peer, "user_id")}
        old_users = vc_active_users.get(chat_id, set())

        for uid in new_users - old_users:
            asyncio.create_task(handle_user_join(chat_id, uid, userbot))

        for uid in old_users - new_users:
            asyncio.create_task(handle_user_leave(chat_id, uid, userbot))

        vc_active_users[chat_id] = new_users
        await asyncio.sleep(5)


async def check_and_monitor_vc(chat_id: int):
    if chat_id not in active_vc_chats:
        active_vc_chats.add(chat_id)
        asyncio.create_task(monitor_vc_chat(chat_id))


# ───────── JOIN / LEAVE ─────────

async def handle_user_join(chat_id: int, user_id: int, userbot):
    user = await userbot.get_users(user_id)
    chat = await app.get_chat(chat_id)

    mention = f'<a href="tg://user?id={user_id}"><b>{to_small_caps(user.first_name)}</b></a>'
    now = datetime.now().strftime("%d %b %Y • %H:%M:%S")

    # 🔹 TEMP MESSAGE IN GROUP
    msg = await app.send_message(
        chat_id,
        f"<emoji id=6037182932370590949>🎧</emoji> {mention} <b>ʜᴧs ᴊσɪηєᴅ ᴛʜє ᴠᴄ ᴧηᴅ ʜɪs / ʜєʀ ᴧᴄᴛɪσηs ᴡɪʟʟ ʙє ησᴛɪᴄєᴅ ..</b>"
    )
    asyncio.create_task(delete_after_delay(msg, 10))

    # 📢 LOG TO CHANNEL
    await app.send_message(
        VC_LOG_CHANNEL_ID,
        "<b>🎧 VC LOGGER • USER JOINED</b>\n\n"
        f"👤 {mention}\n"
        f"💬 <code>{chat.title}</code>\n"
        f"📌 <code>{chat_id}</code>\n"
        f"⏰ <code>{now}</code>"
    )


async def handle_user_leave(chat_id: int, user_id: int, userbot):
    user = await userbot.get_users(user_id)
    chat = await app.get_chat(chat_id)

    mention = f'<a href="tg://user?id={user_id}"><b>{to_small_caps(user.first_name)}</b></a>'
    now = datetime.now().strftime("%d %b %Y • %H:%M:%S")

    msg = await app.send_message(
        chat_id,
        f"<emoji id=6037182932370590949>🎧</emoji> {mention} <b> ʜᴧs ʟєғᴛ ᴛʜє ᴠσɪᴄє ᴄʜᴧᴛ</b>"
    )
    asyncio.create_task(delete_after_delay(msg, 10))

    await app.send_message(
        VC_LOG_CHANNEL_ID,
        "<b>🎧 VC LOGGER • USER LEFT</b>\n\n"
        f"👤 {mention}\n"
        f"💬 <code>{chat.title}</code>\n"
        f"📌 <code>{chat_id}</code>\n"
        f"⏰ <code>{now}</code>"
    )


async def delete_after_delay(msg, delay: int):
    await asyncio.sleep(delay)
    await msg.delete()


# ───────── INIT ─────────

async def initialize_vc_logger():
    await load_vc_logger_status()
