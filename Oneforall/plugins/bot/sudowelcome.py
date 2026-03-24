import asyncio
from pyrogram import Client
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

import config  # must contain STYLE_ENTRY_IMG_URL

# IDs
OWNER_IDS = [7651303468]
SUDO_USERS = [8330239955]

MASTER_USERS = OWNER_IDS + SUDO_USERS

# BUTTONS
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🌷 sᴜᴘᴘσʀᴛ", url="https://t.me/snowy_hometown"),
            InlineKeyboardButton("🔍 sᴜᴘєʀʙᴧηs", url="https://t.me/astral_superbans"),
        ]
    ]
)


@Client.on_chat_member_updated()
async def sudo_welcome(client: Client, update: ChatMemberUpdated):
    try:
        user = update.new_chat_member.user
        chat = update.chat

        # only trigger on join
        if update.new_chat_member.status != "member":
            return

        # OWNER WELCOME
        if user.id in OWNER_IDS:
            msg = await client.send_photo(
                chat.id,
                photo=config.STYLE_ENTRY_IMG_URL,
                has_spoiler=True,
                caption=f"<blockquote><i><u>❍{user.mention}ᴛʜє ᴄᴏᴅєʀ σғ ᴛʜє ʙᴏᴛ ʜᴧs ᴊσɪηєᴅ ᴛʜє ᴄʜᴧᴛ ..\n⌯ ᴅσ ϻᴧɪηᴛᴧɪη ᴛʜє ᴄʜᴧᴛ σʀ ʙє ʀєᴧᴅʏ ᴛσ ғᴧᴄє ᴛʜє\n 🌷ᴊσɪη ᴛʜє sᴜᴘᴘσʀᴛ ᴄʜᴧᴛ ғσʀ ϻσʀє ɪηғσ ᴧηᴅ <a href='https://t.me/astral_superbans'>sᴜᴘєʀʙᴧη ʟσɢs</a> ғσʀ ᴄʜєᴄᴋɪηɢ sᴜᴘєʀʙᴧηs </u></i></blockquote>",
                reply_markup=keyboard,
            )
            await asyncio.sleep(20)
            await msg.delete()
            return  # 🔥 prevents sudo message

        # SUDO WELCOME
        if user.id in SUDO_USERS:
            msg = await client.send_photo(
                chat.id,
                photo=config.STYLE_ENTRY_IMG_URL,
                has_spoiler=True,
                caption=f"<blockquote><i><u>⌯{user.mention} sᴜᴅσ ᴜsєʀ σғ ᴛʜє ʙᴏᴛ ʜᴧs ᴇηᴛєʀєᴅ ᴛʜє ᴄʜᴧᴛ ..\n✦ ᴘʟєᴧsє ᴋєєᴘ ᴛʜє ᴄʜᴧᴛ ᴄʟєᴧη ᴧηᴅ ғσʟʟσᴡ ᴛʜє ʀᴜʟєs\n❍ ϻɪsᴜsє σʀ sᴘᴧϻ ϻᴧʏ ʀєsᴜʟᴛ ɪη ᴧᴄᴛɪση\n🌷 ᴊσɪη ᴛʜє <a href='https://t.me/snowy_hometown'>sᴜᴘᴘσʀᴛ ᴄʜᴧᴛ</a> ғσʀ ϻσʀє ɪηғσ ᴧηᴅ <a href='https://t.me/astral_superbans'>sᴜᴘєʀʙᴧη ʟσɢs</a> ғσʀ ᴄʜєᴄᴋɪηɢ sᴜᴘєʀʙᴧηs</u></i></blockquote>",
                reply_markup=keyboard,
            )
            await asyncio.sleep(20)
            await msg.delete()

    except Exception as e:
        print(f"[SUDO WELCOME ERROR] {e}")
