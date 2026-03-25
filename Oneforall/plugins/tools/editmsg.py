import asyncio
from pyrogram import filters
from pyrogram.types import Message

from Oneforall import app

# ───────── STATE ─────────

edit_protection_enabled: dict = {}

# ───────── COMMAND ─────────

@app.on_message(filters.command("editmsg", prefixes=["/", ".", "!", "@"]) & filters.group)
async def editmsg_command(_, message: Message):
    """Enable or disable message edit protection in the group"""
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) == 1:
        status = edit_protection_enabled.get(chat_id, False)
        await message.reply(
            f"📝 <b>Edit Message Protection:</b> <b>{status}</b>\n\n"
            "➤ <code>/editmsg on</code>\n"
            "➤ <code>/editmsg off</code>"
        )
        return
    
    arg = args[1].lower()
    
    if arg in ("on", "enable", "yes"):
        edit_protection_enabled[chat_id] = True
        await message.reply("✅ <b>Edit Protection Enabled - Messages will be deleted when edited</b>")
    
    elif arg in ("off", "disable", "no"):
        edit_protection_enabled[chat_id] = False
        await message.reply("🚫 <b>Edit Protection Disabled</b>")

# ───────── EDIT MESSAGE HANDLER ─────────

@app.on_edited_message(filters.group)
async def on_message_edited(_, message: Message):
    """Delete message when it's edited by any user"""
    chat_id = message.chat.id
    
    # Check if edit protection is enabled for this chat
    if not edit_protection_enabled.get(chat_id, False):
        return
    
    try:
        # Delete the edited message
        await message.delete()
        
        # Send a notification
        user = message.from_user
        mention = f'<a href="tg://user?id={user.id}"><b>{user.first_name}</b></a>'
        
        notif = await app.send_message(
            chat_id,
            f"🚫 {mention} <b>your message was deleted due to edit attempt</b>"
        )
        
        # Auto-delete notification after 5 seconds
        await asyncio.sleep(5)
        await notif.delete()
    
    except Exception as e:
        print(f"Error deleting edited message: {e}")