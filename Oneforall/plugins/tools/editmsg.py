from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import CallbackQuery

# Message Cache to store original content
message_cache = {}  

@Client.on_message(filters.command('editmsg'))
def edit_message_command(client, message):
    # Reply to the user with inline keyboard
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('ON', callback_data='edit_on'), InlineKeyboardButton('OFF', callback_data='edit_off')]
    ])
    message.reply_text("Choose edit mode:", reply_markup=keyboard)

@Client.on_callback_query()
def button_click(client, callback_query: CallbackQuery):
    original_message = callback_query.message
    message_cache[original_message.id] = original_message.text

    if callback_query.data == 'edit_on':
        original_message.reply_text('Edit mode is ON.')
    elif callback_query.data == 'edit_off':
        original_message.reply_text('Edit mode is OFF.')
    # Auto-delete message after 5 seconds
    original_message.delete()  

@Client.on_message(filters.text & ~Filters.command)
def handle_edit_message(client, message):
    original_content = message_cache.get(message.id, None)
    if original_content is not None and original_content != message.text:
        # Only delete if text content changes
        message.delete()
        message.reply_text('Message edited!')
        message_cache[message.id] = message.text

        # Auto-delete notification after 5 seconds
        client.delete_messages(message.chat.id, message.id, wait_time=5)

if __name__ == '__main__':
    Client.run()