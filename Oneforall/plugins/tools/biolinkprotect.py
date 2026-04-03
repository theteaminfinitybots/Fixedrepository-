import re
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from Oneforall import app
from Oneforall.utils.database import is_biolink, biolink_on, biolink_off

@app.on_message(filters.command("linkprotect") & filters.group)
async def linkprotect_toggle(client, message: Message):
    if not message.from_user:
        return

    # Check if the user is an administrator or owner
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await message.reply_text("Only admins can use this command.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /linkprotect [on|off]")

    state = message.command[1].lower()
    if state == "on":
        await biolink_on(message.chat.id)
        await message.reply_text("Biolink protection enabled.")
    elif state == "off":
        await biolink_off(message.chat.id)
        await message.reply_text("Biolink protection disabled.")
    else:
        await message.reply_text("Usage: /linkprotect [on|off]")

@app.on_message(filters.group & ~filters.bot & ~filters.service, group=10)
async def biolink_protect_handler(client, message: Message):
    if not await is_biolink(message.chat.id):
        return

    if not message.from_user:
        return

    try:
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return
    except:
        pass

    try:
        user_info = await client.get_users(message.from_user.id)
        bio = user_info.bio

        if bio:
            # Check for links or usernames in bio
            if re.search(r"(https?://|www\.|t\.me/|@\w+)", bio, re.IGNORECASE):
                try:
                    await message.delete()
                except:
                    pass
    except:
        pass
