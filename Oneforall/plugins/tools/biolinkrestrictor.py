import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus

from Oneforall import app

# ───────── STATE ─────────

edit_protection_enabled = {}
message_cache = {}  # {chat_id: {msg_id: text}}
whitelist = {}      # {chat_id: set(user_ids)}

# ───────── ADMIN CHECK ─────────

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR
        )
    except:
        return False

# ───────── KEYBOARD ─────────

def get_keyboard(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ON", callback_data=f"edit_on_{chat_id}"),
            InlineKeyboardButton("❌ OFF", callback_data=f"edit_off_{chat_id}")
        ]
    ])

# ───────── COMMAND PANEL ─────────

@app.on_message(filters.command("editmsg") & filters.group)
async def editmsg_command(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ <b>ᴀᴅᴍɪɴ ᴏɴʟʏ</b>")

    chat_id = message.chat.id
    status = edit_protection_enabled.get(chat_id, False)

    status_text = "✅ <b>ᴇɴᴀʙʟᴇᴅ</b>" if status else "❌ <b>ᴅɪѕᴀʙʟᴇᴅ</b>"

    await message.reply_text(
        f"📝 <b>ᴇᴅɪᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ</b>\n\n"
        f"<b>ѕᴛᴀᴛᴜѕ :</b> {status_text}\n\n"
        f"❖ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇѕ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ\n"
        f"❖ ᴡʜɪᴛᴇʟɪѕᴛ ᴜѕᴇʀѕ ɪɢɴᴏʀᴇᴅ\n"
        f"❖ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇѕ",
        reply_markup=get_keyboard(chat_id)
    )

# ───────── CALLBACKS ─────────

@app.on_callback_query(filters.regex(r"edit_on_"))
async def edit_on(client, query: CallbackQuery):

    chat_id = int(query.data.split("_")[-1])

    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ", show_alert=True)

    edit_protection_enabled[chat_id] = True

    await query.edit_message_text(
        "📝 <b>ᴇᴅɪᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ</b>\n\n"
        "<b>ѕᴛᴀᴛᴜѕ :</b> ✅ ᴇɴᴀʙʟᴇᴅ",
        reply_markup=get_keyboard(chat_id)
    )

@app.on_callback_query(filters.regex(r"edit_off_"))
async def edit_off(client, query: CallbackQuery):

    chat_id = int(query.data.split("_")[-1])

    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ", show_alert=True)

    edit_protection_enabled[chat_id] = False
    message_cache.pop(chat_id, None)

    await query.edit_message_text(
        "📝 <b>ᴇᴅɪᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ</b>\n\n"
        "<b>ѕᴛᴀᴛᴜѕ :</b> ❌ ᴅɪѕᴀʙʟᴇᴅ",
        reply_markup=get_keyboard(chat_id)
    )

# ───────── WHITELIST COMMANDS ─────────

@app.on_message(filters.command("editfree") & filters.group)
async def add_whitelist(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ <b>ᴀᴅᴍɪɴ ᴏɴʟʏ</b>")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    else:
        return await message.reply_text("ʀᴇᴘʟʏ ᴏʀ ɢɪᴠᴇ ɪᴅ")

    whitelist.setdefault(message.chat.id, set()).add(user_id)

    await message.reply_text("✅ ᴜѕᴇʀ ᴀᴅᴅᴇᴅ ᴛᴏ ᴡʜɪᴛᴇʟɪѕᴛ")

@app.on_message(filters.command("editunfree") & filters.group)
async def remove_whitelist(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ <b>ᴀᴅᴍɪɴ ᴏɴʟʏ</b>")

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    else:
        return await message.reply_text("ʀᴇᴘʟʏ ᴏʀ ɢɪᴠᴇ ɪᴅ")

    whitelist.get(message.chat.id, set()).discard(user_id)

    await message.reply_text("❌ ᴜѕᴇʀ ʀᴇᴍᴏᴠᴇᴅ")

@app.on_message(filters.command("editfreelist") & filters.group)
async def list_whitelist(_, message: Message):

    users = whitelist.get(message.chat.id, set())

    if not users:
        return await message.reply_text("ɴᴏ ᴡʜɪᴛᴇʟɪѕᴛ ᴜѕᴇʀѕ")

    text = "\n".join([str(u) for u in users])

    await message.reply_text(f"📜 <b>ᴡʜɪᴛᴇʟɪѕᴛ :</b>\n{text}")

# ───────── CACHE ─────────

@app.on_message(filters.group & ~filters.service)
async def cache_message(_, message: Message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not edit_protection_enabled.get(chat_id):
        return

    if user_id in whitelist.get(chat_id, set()):
        return

    text = message.text or message.caption
    if not text:
        return

    message_cache.setdefault(chat_id, {})[message.id] = text

    if len(message_cache[chat_id]) > 200:
        message_cache[chat_id].pop(next(iter(message_cache[chat_id])))

# ───────── EDIT DETECTION ─────────

@app.on_edited_message(filters.group)
async def detect_edit(client, message: Message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not edit_protection_enabled.get(chat_id):
        return

    if await is_admin(client, chat_id, user_id):
        return

    if user_id in whitelist.get(chat_id, set()):
        return

    if chat_id not in message_cache:
        return

    msg_id = message.id
    if msg_id not in message_cache[chat_id]:
        return

    if message_cache[chat_id][msg_id] == (message.text or message.caption or ""):
        return

    try:
        await message.delete()
    except:
        return

    warn = await message.reply_text(
        f"🚫 {message.from_user.mention}\n<b>ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ʀᴇᴍᴏᴠᴇᴅ</b>"
    )

    await asyncio.sleep(4)

    try:
        await warn.delete()
    except:
        pass

    message_cache[chat_id].pop(msg_id, None)
