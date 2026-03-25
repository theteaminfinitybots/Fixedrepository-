import re
from pyrogram import filters
from pyrogram.types import Message
from Oneforall import app
from Oneforall.core.mongo import mongodb

# ───────── DATABASE ─────────

biolink_db = mongodb["biolink"]
biolink_status = biolink_db["status"]
biolink_whitelist = biolink_db["whitelist"]
biolink_warns = biolink_db["warns"]

# ───────── CONFIG ─────────

URL_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|@\w+)",
    re.IGNORECASE
)

WARN_LIMIT = 3

# ───────── FUNCTIONS ─────────

async def is_enabled(chat_id: int):
    data = await biolink_status.find_one({"chat_id": chat_id})
    return data and data.get("enabled", False)


async def is_whitelisted(chat_id: int, user_id: int):
    return await biolink_whitelist.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )


async def add_warn(chat_id: int, user_id: int):
    data = await biolink_warns.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )

    if not data:
        await biolink_warns.insert_one(
            {"chat_id": chat_id, "user_id": user_id, "count": 1}
        )
        return 1
    else:
        count = data["count"] + 1
        await biolink_warns.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": count}}
        )
        return count


# ───────── COMMANDS ─────────

@app.on_message(filters.command("biolink") & filters.group)
async def biolink_toggle(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /biolink on or off")

    chat_id = message.chat.id
    action = message.command[1].lower()

    if action == "on":
        await biolink_status.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": True}},
            upsert=True
        )
        await message.reply("🔗 BioLink Protection Enabled")

    elif action == "off":
        await biolink_status.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": False}},
            upsert=True
        )
        await message.reply("❌ BioLink Protection Disabled")


@app.on_message(filters.command("biofree") & filters.group)
async def biofree(_, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    else:
        return await message.reply("Reply or give user ID")

    await biolink_whitelist.update_one(
        {"chat_id": message.chat.id, "user_id": user_id},
        {"$set": {}},
        upsert=True
    )

    await message.reply(f"✅ User {user_id} whitelisted")


@app.on_message(filters.command("biounfree") & filters.group)
async def biounfree(_, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    else:
        return await message.reply("Reply or give user ID")

    await biolink_whitelist.delete_one(
        {"chat_id": message.chat.id, "user_id": user_id}
    )

    await message.reply(f"❌ User {user_id} removed from whitelist")


@app.on_message(filters.command("biofreelist") & filters.group)
async def biofreelist(_, message: Message):
    users = []
    async for user in biolink_whitelist.find(
        {"chat_id": message.chat.id}
    ):
        users.append(str(user["user_id"]))

    if not users:
        return await message.reply("No whitelisted users.")

    await message.reply("Whitelisted:\n" + "\n".join(users))


# ───────── MAIN HANDLER ─────────

@app.on_message(filters.group & ~filters.service)
async def check_bio_links(_, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    if not await is_enabled(chat_id):
        return

    if await is_whitelisted(chat_id, user.id):
        return

    try:
        full_user = await app.get_users(user.id)
        bio = full_user.bio or ""
    except:
        return

    if not URL_PATTERN.search(bio):
        return

    # ⚠️ USER HAS LINK IN BIO

    warn_count = await add_warn(chat_id, user.id)

    await message.delete()

    await message.reply(
        f"⚠️ {user.mention} Bio contains a link!\n"
        f"Warnings: {warn_count}/{WARN_LIMIT}"
    )

    if warn_count >= WARN_LIMIT:
        try:
            await app.restrict_chat_member(
                chat_id,
                user.id,
                permissions={}
            )
        except:
            pass
