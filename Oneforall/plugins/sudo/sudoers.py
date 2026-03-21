from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid

from Oneforall import app
from Oneforall.misc import SUDOERS
from Oneforall.utils.database import add_sudo, remove_sudo
from Oneforall.utils.decorators.language import language
from Oneforall.utils.extraction import extract_user
from Oneforall.utils.inline import close_markup
from config import BANNED_USERS, OWNER_ID


# -------------------- ADD SUDO -------------------- #
@app.on_message(filters.command(["addsudo"]) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])

    user = await extract_user(message)

    if user.id in SUDOERS:
        return await message.reply_text(_["sudo_1"].format(user.mention))

    added = await add_sudo(user.id)

    if added:
        SUDOERS.add(user.id)
        await message.reply_text(_["sudo_2"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


# -------------------- REMOVE SUDO -------------------- #
@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])

    user = await extract_user(message)

    if user.id not in SUDOERS:
        return await message.reply_text(_["sudo_3"].format(user.mention))

    removed = await remove_sudo(user.id)

    if removed:
        SUDOERS.remove(user.id)
        await message.reply_text(_["sudo_4"].format(user.mention))
    else:
        await message.reply_text(_["sudo_8"])


# -------------------- SUDO LIST -------------------- #
@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"]) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):

    # ❌ Non-sudo users see fixed owner message
    if message.from_user.id not in SUDOERS:
        return await message.reply_text(
            "💔 <b>ᴏᴡɴᴇʀ:</b>\n"
            f"1➤ <code>{OWNER_ID}</code>",
            parse_mode="html"
        )

    text = _["sudo_5"]

    # ✅ Safe OWNER fetch
    try:
        owner = await app.get_users(OWNER_ID)
        owner_name = owner.mention or owner.first_name
    except PeerIdInvalid:
        owner_name = f"<code>{OWNER_ID}</code>"

    text += f"1➤ {owner_name}\n"

    count = 0
    header_added = False

    for user_id in SUDOERS:
        if user_id == OWNER_ID:
            continue

        try:
            user = await app.get_users(user_id)
            name = user.mention or user.first_name

            if not header_added:
                text += _["sudo_6"]
                header_added = True

            count += 1
            text += f"{count}➤ {name}\n"

        except PeerIdInvalid:
            # skip invalid users safely
            continue

    if count == 0:
        return await message.reply_text(_["sudo_7"])

    await message.reply_text(
        text,
        reply_markup=close_markup(_),
        parse_mode="html"
    )
