import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from Oneforall import app

# ───────── STATE ─────────

edit_protection_enabled: dict = {}
message_content_cache: dict = {}

# ───────── COMMAND ─────────

@app.on_message(filters.command("editmsg", prefixes=["/", ".", "!", "@", "?"]) & filters.group)
async def editmsg_command(_, message: Message):
    """Send edit protection status with inline buttons"""
    chat_id = message.chat.id
    
    status = edit_protection_enabled.get(chat_id, False)
    status_text = "✅ <b>Enabled</b>" if status else "❌ <b>Disabled</b>"
    
    # Create inline buttons for ON/OFF
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ ON", callback_data=f"editmsg_on_{chat_id}"),
            InlineKeyboardButton("❌ OFF", callback_data=f"editmsg_off_{chat_id}")
        ]
    ])
    
    await message.reply(
        f"📝 <b>Edit Message Protection</b>\n\n"
        f"<b>Current Status:</b> {status_text}\n\n"
        f"<i>When enabled:</i>\n"
        f"• Messages with edited text will be deleted\n"
        f"• Reactions are ignored\n"
        f"• Notifications auto-delete after 5 seconds",
        reply_markup=keyboard
    )

# ───────── CALLBACK HANDLERS ─────────

@app.on_callback_query(filters.regex(r"editmsg_on_"))
async def editmsg_on_callback(_, callback_query: CallbackQuery):
    """Handle ON button press"""
    try:
        chat_id = int(callback_query.data.split("_")[-1])
        
        edit_protection_enabled[chat_id] = True
        
        # Create updated keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ON", callback_data=f"editmsg_on_{chat_id}"),
                InlineKeyboardButton("❌ OFF", callback_data=f"editmsg_off_{chat_id}")
            ]
        ])
        
        # Edit the message with new status
        await callback_query.edit_message_text(
            f"📝 <b>Edit Message Protection</b>\n\n"
            f"<b>Current Status:</b> ✅ <b>Enabled</b>\n\n"
            f"<i>When enabled:</i>\n"
            f"• Messages with edited text will be deleted\n"
            f"• Reactions are ignored\n"
            f"• Notifications auto-delete after 5 seconds",
            reply_markup=keyboard
        )
        
        await callback_query.answer("✅ Edit Protection Enabled", show_alert=False)
    
    except Exception as e:
        print(f"Error in editmsg_on_callback: {e}")
        await callback_query.answer("❌ Error occurred", show_alert=True)

@app.on_callback_query(filters.regex(r"editmsg_off_"))
async def editmsg_off_callback(_, callback_query: CallbackQuery):
    """Handle OFF button press"""
    try:
        chat_id = int(callback_query.data.split("_")[-1])
        
        edit_protection_enabled[chat_id] = False
        if chat_id in message_content_cache:
            del message_content_cache[chat_id]
        
        # Create updated keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ON", callback_data=f"editmsg_on_{chat_id}"),
                InlineKeyboardButton("❌ OFF", callback_data=f"editmsg_off_{chat_id}")
            ]
        ])
        
        # Edit the message with new status
        await callback_query.edit_message_text(
            f"📝 <b>Edit Message Protection</b>\n\n"
            f"<b>Current Status:</b> ❌ <b>Disabled</b>\n\n"
            f"<i>Edit protection is currently disabled.</i>",
            reply_markup=keyboard
        )
        
        await callback_query.answer("❌ Edit Protection Disabled", show_alert=False)
    
    except Exception as e:
        print(f"Error in editmsg_off_callback: {e}")
        await callback_query.answer("❌ Error occurred", show_alert=True)

# ───────── STORE ORIGINAL MESSAGES ─────────

@app.on_message(filters.group & ~filters.command(["editmsg"]))
async def cache_message(_, message: Message):
    """Store original message text and caption for comparison"""
    try:
        chat_id = message.chat.id
        msg_id = message.message_id
        
        # Only cache if protection is enabled
        if edit_protection_enabled.get(chat_id, False):
            text_content = message.text or message.caption or ""
            
            if chat_id not in message_content_cache:
                message_content_cache[chat_id] = {}
            
            message_content_cache[chat_id][msg_id] = text_content
    except Exception as e:
        print(f"Error caching message: {e}")

# ───────── EDIT MESSAGE HANDLER ─────────

@app.on_edited_message(filters.group)
async def on_message_edited(_, message: Message):
    """Delete message only if text content was edited, ignore reactions"""
    chat_id = message.chat.id
    msg_id = message.message_id
    
    # Check if edit protection is enabled
    if not edit_protection_enabled.get(chat_id, False):
        return
    
    try:
        # Get current content
        current_content = message.text or message.caption or ""
        
        # Get original content from cache
        if chat_id not in message_content_cache or msg_id not in message_content_cache[chat_id]:
            return
        
        original_content = message_content_cache[chat_id][msg_id]
        
        # Only delete if TEXT CONTENT actually changed
        if original_content != current_content:
            # Delete the edited message
            await message.delete()
            
            # Send notification
            user = message.from_user
            mention = f'<a href="tg://user?id={user.id}"><b>{user.first_name}</b></a>'
            
            notif = await app.send_message(
                chat_id,
                f"🚫 {mention} <b>your message was deleted due to edit</b>"
            )
            
            # Auto-delete notification after 5 seconds
            await asyncio.sleep(5)
            try:
                await notif.delete()
            except:
                pass
            
            # Remove from cache
            if msg_id in message_content_cache[chat_id]:
                del message_content_cache[chat_id][msg_id]
    
    except Exception as e:
        print(f"Error handling edited message: {e}")