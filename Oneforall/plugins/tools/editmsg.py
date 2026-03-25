def edit_message(update, context):
    message = update.message
    if message.text:
        # Check if the text content has changed
        if message.text != context.user_data.get('last_text', ''):
            # Delete the previous message if text content has actually been edited
            context.bot.delete_message(chat_id=message.chat_id, message_id=context.user_data.get('last_message_id'))
            context.user_data['last_text'] = message.text
            # Store the ID of the new message
            context.user_data['last_message_id'] = message.message_id
        else:
            # Ignore changes that are only reactions
            pass
    else:
        # Handle other types of content if necessary
        pass