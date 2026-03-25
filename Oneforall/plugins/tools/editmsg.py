from pyrogram import Client, filters

# Create a Pyrogram Client
app = Client('my_bot')

# Dictionary to store original messages
original_messages = {}

@app.on_message(filters.command('editmsg'))
async def edit_message_cmd(client, message):
    # Check if message payload is 'on' or 'off'
    command = message.command[1] if len(message.command) > 1 else None
    if command == 'on':
        await message.reply("Editing messages is now enabled.")
    elif command == 'off':
        await message.reply("Editing messages is now disabled.")
    else:
        await message.reply("Usage: /editmsg [on/off]")

@app.on_edit_message()
async def handle_edit(client, message):
    # Ignore edits that are reactions
    if message.text:
        # Get the original message if exists
        original_msg = original_messages.get(message.chat.id)
        if original_msg is not None:
            # Perform your logic here (e.g., logging the edit)
            log_edit(original_msg, message.text)

        # Store the edited message as the original
        original_messages[message.chat.id] = message.text

async def log_edit(original_text, edited_text):
    # Log the original and edited messages
    print(f"Message edited from '{original_text}' to '{edited_text}'")

# Start the bot
app.run()