def delete_message_if_edited(message):
    # Check if message has an edit date
    if message.edit_date:
        # Compare message text content with the edited version
        if message.text != message.edited_text:
            # Proceed to delete the message if it's a real edit
            message.delete()
