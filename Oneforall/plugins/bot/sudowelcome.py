import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import OWNER_ID, STYLE_ENTRY_IMG_URL
from Oneforall.misc import SUDOERS   # adjust import if needed


# COMMON KEYBOARD
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🌷 sᴜᴘᴘσʀᴛ", url="https://t.me/snowy_hometown"),
            InlineKeyboardButton("🔍 sᴜᴘєʀʙᴧηs", url="https://t.me/astral_superbans"),
        ]
    ]
)


async def sudo_owner_welcome(client, message, member):
    try:
        # OWNER WELCOME
        if member.id == OWNER_ID:
            msg = await message.reply_photo(
                photo=STYLE_ENTRY_IMG_URL,
                has_spoiler=True,
                caption=f"<blockquote><i><u>❍{member.mention}ᴛʜє ᴄᴏᴅєʀ σғ ᴛʜє ʙᴏᴛ ʜᴧs ᴊσɪηєᴅ ᴛʜє ᴄʜᴧᴛ ..\n⌯ ᴅσ ϻᴧɪηᴛᴧɪη ᴛʜє ᴄʜᴧᴛ σʀ ʙє ʀєᴧᴅʏ ᴛσ ғᴧᴄє ᴛʜє\n 🌷ᴊσɪη ᴛʜє sᴜᴘᴘσʀᴛ ᴄʜᴧᴛ ғσʀ ϻσʀє ɪηғσ ᴧηᴅ <a href='https://t.me/astral_superbans'>sᴜᴘєʀʙᴧη ʟσɢs</a> ғσʀ ᴄʜєᴄᴋɪηɢ sᴜᴘєʀʙᴧηs </u></i></blockquote>",
                reply_markup=keyboard,
            )
            await asyncio.sleep(20)
            await msg.delete()
            return  # 🔥 prevents sudo trigger

        # SUDO CHECK
        if isinstance(SUDOERS, (list, set)):
            is_sudo = member.id in SUDOERS
        else:
            is_sudo = member.id == SUDOERS

        # SUDO WELCOME
        if is_sudo:
            msg = await message.reply_photo(
                photo=STYLE_ENTRY_IMG_URL,
                has_spoiler=True,
                caption=f"<blockquote><i><u>⌯{member.mention} sᴜᴅσ ᴜsєʀ σғ ᴛʜє ʙᴏᴛ ʜᴧs ᴇηᴛєʀєᴅ ᴛʜє ᴄʜᴧᴛ ..\n✦ ᴘʟєᴧsє ᴋєєᴘ ᴛʜє ᴄʜᴧᴛ ᴄʟєᴧη ᴧηᴅ ғσʟʟσᴡ ᴛʜє ʀᴜʟєs\n❍ ϻɪsᴜsє σʀ sᴘᴧϻ ϻᴧʏ ʀєsᴜʟᴛ ɪη ᴧᴄᴛɪση\n🌷 ᴊσɪη ᴛʜє <a href='https://t.me/snowy_hometown'>sᴜᴘᴘσʀᴛ ᴄʜᴧᴛ</a> ғσʀ ϻσʀє ɪηғσ ᴧηᴅ <a href='https://t.me/astral_superbans'>sᴜᴘєʀʙᴧη ʟσɢs</a> ғσʀ ᴄʜєᴄᴋɪηɢ sᴜᴘєʀʙᴧηs</u></i></blockquote>",
                reply_markup=keyboard,
            )
            await asyncio.sleep(20)
            await msg.delete()

    except Exception as e:
        print(f"[SUDO WELCOME ERROR] {e}")
