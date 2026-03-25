from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

# Dictionary to hold original messages for edit protection
original_messages = {}

# Enable/disable edit protection for group
edit_protection_enabled = False

def editmsg_command(update: Update, context: CallbackContext) -> None:
    global edit_protection_enabled
    edit_protection_enabled = not edit_protection_enabled  # Toggle protection
    status = 'enabled' if edit_protection_enabled else 'disabled'
    update.message.reply_text(f'Edit protection is now {status}.')

def cache_original_message(update: Update) -> None:
    if edit_protection_enabled:
        original_messages[update.message.chat.id] = update.message.text  # Cache original text

def edited_message_handler(update: Update, context: CallbackContext) -> None:
    if edit_protection_enabled:
        chat_id = update.message.chat.id
        if chat_id in original_messages and update.message.text != original_messages[chat_id]:
            # Text has changed, delete original message and notify
            context.bot.delete_message(chat_id, update.message.message_id)
            update.message.reply_text('Message edited, original deleted.', reply_to_message_id=update.message.message_id)

            # Auto-delete notification after 5 seconds
            context.job_queue.run_once(lambda context: context.bot.delete_message(chat_id, update.message.message_id + 1), 5)

def main() -> None:
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

    updater = Updater('YOUR_TOKEN_HERE', use_context=True)

    # Setup command and message handlers
    updater.dispatcher.add_handler(CommandHandler('editmsg', editmsg_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, cache_original_message))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, edited_message_handler))

    updater.start_polling()
    updater.idle()