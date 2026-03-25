import re
import asyncio
from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.enums import ChatMemberStatus

from config import BANNED_USERS
from Oneforall import app
from Oneforall.core.mongo import mongodb

# ───────── DATABASE ─────────

db = mongodb["biolink"]
status_db = db["status"]
whitelist_db = db["whitelist"]
warns_db = db["warns"]

# ───────── CONFIG ─────────

URL_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|@\w+)",
    re.IGNORECASE
)

WARN_LIMIT = 3

# ───────── ADMIN CHECK (UPDATED) ─────────

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR
        )
    except:
        return False

# ───────── HELPERS ─────────

async def is_enabled(chat_id):
    data = await status_db.find_one({"chat_id": chat_id})
    return data and data.get("enabled", False)


async def is_whitelisted(chat_id, user_id):
    return await whitelist_db.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )


async def get_bio(user_id):
    try:
        full = await app.invoke(
            GetFullUser(id=await app.resolve_peer(user_id))
        )
        return full.full_user.about or ""
    except:
        return ""


async def add_warn(chat_id, user_id):
    data = await warns_db.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )

    if not data:
        await warns_db.insert_one(
            {"chat_id": chat_id, "user_id": user_id, "count": 1}
        )
        return 1
    else:
        count = data["count"] + 1
        await warns_db.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": count}}
        )
        return count


# ───────── COMMANDS (ADMIN ONLY) ─────────

@app.on_message(filters.command("biolink") & filters.group & ~BANNED_USERS)
async def biolink_toggle(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ <b>ᴀᴅᴍɪɴ ᴏɴʟʏ</b>")

    if len(message.command) < 2:
        return await message.reply_text("ᴜѕᴀɢᴇ: /biolink on | off")

    action = message.command[1].lower()

    if action == "on":
        await status_db.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": True}},
            upsert=True
        )
        await message.reply_text("🔗 <b>ʙɪᴏʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴇɴᴀʙʟᴇᴅ</b>")

    elif action == "off":
        await status_db.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": False}},
            upsert=True
        )
        await message.reply_text("❌ <b>ʙɪᴏʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ᴅɪѕᴀʙʟᴇᴅ</b>")


@app.on_message(filters.command("biofree") & filters.group & ~BANNED_USERS)
async def biofree(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ <b>ᴀᴅᴍɪɴ ᴏɴʟʏ</b>")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    else:
        return await message.reply_text("ʀᴇᴘʟʏ ᴏʀ ɢɪᴠᴇ ᴜѕᴇʀ ɪᴅ")

    await whitelist_db.update_one(
        {"chat_id": message.chat.id, "user_id": user_id},
        {"$set": {}},
        upsert=True
    )

    await message.reply_text("✅ <b>ᴜѕᴇʀ ᴡʜɪᴛᴇʟɪѕᴛᴇᴅ</b>")


@app.on_message(filters.command("biounfree") & filters.group & ~BANNED_USERS)
async def biounfree(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ <b>ᴀᴅᴍɪɴ ᴏɴʟʏ</b>")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    else:
        return await message.reply_text("ʀᴇᴘʟʏ ᴏʀ ɢɪᴠᴇ ᴜѕᴇʀ ɪᴅ")

    await whitelist_db.delete_one(
        {"chat_id": message.chat.id, "user_id": user_id}
    )

    await message.reply_text("❌ <b>ᴜѕᴇʀ ʀᴇᴍᴏᴠᴇᴅ</b>")


@app.on_message(filters.command("biofreelist") & filters.group & ~BANNED_USERS)
async def biofreelist(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ <b>ᴀᴅᴍɪɴ ᴏɴʟʏ</b>")

    users = []
    async for user in whitelist_db.find({"chat_id": message.chat.id}):
        users.append(str(user["user_id"]))

    if not users:
        return await message.reply_text("ɴᴏ ᴡʜɪᴛᴇʟɪѕᴛ ᴜѕᴇʀѕ")

    await message.reply_text(
        "📜 <b>ᴡʜɪᴛᴇʟɪѕᴛ ᴜѕᴇʀѕ :</b>\n" + "\n".join(users)
    )


# ───────── MAIN DETECTOR ─────────

@app.on_message(filters.group & ~filters.service & ~BANNED_USERS)
async def check_biolink(client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_enabled(chat_id):
        return

    if await is_admin(client, chat_id, user_id):
        return

    if await is_whitelisted(chat_id, user_id):
        return

    bio = await get_bio(user_id)

    if not bio:
        return

    if not URL_PATTERN.search(bio):
        return

    warn_count = await add_warn(chat_id, user_id)

    try:
        await message.delete()
    except:
        pass

    warn_msg = await message.reply_text(
        f"⚠️ {message.from_user.mention}\n"
        f"<b>ʙɪᴏ ᴄᴏɴᴛᴀɪɴѕ ʟɪɴᴋ</b>\n"
        f"ᴡᴀʀɴɪɴɢѕ: {warn_count}/{WARN_LIMIT}"
    )

    await asyncio.sleep(5)

    try:
        await warn_msg.delete()
    except:
        pass

    if warn_count >= WARN_LIMIT:
        try:
            await client.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions()
            )
        except:
            pass
