import time
import asyncio
import random

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from Oneforall import app
from Oneforall.misc import _boot_
from Oneforall.plugins.sudo.sudoers import sudoers_list
from Oneforall.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Oneforall.utils.decorators.language import LanguageStart
from Oneforall.utils.formatters import get_readable_time
from Oneforall.utils.inline import help_pannel, private_panel, start_panel
from strings import get_string
from Oneforall.misc import SUDOERS


FORCE_CHANNEL_1 = config.FORCE_CHANNEL_1
FORCE_CHANNEL_2 = config.FORCE_CHANNEL_2

NEXT_IMG = [
    "https://graph.org/file/d22cec7c75e26f36edff7-0ce8cae0037d4aa0aa.jpg",
    "https://graph.org/file/c53dfca85e9e0b5bc9cd1-afa1339cd5d4e6522c.jpg",
]

STICKER = [
    "CAACAgUAAxkBAAEQEGVpSR-TuCKHP8D69SvDAAH2Gn7QjXEAAtIEAAKP9uhXzLPwoqMKxuQ2BA",
    "CAACAgUAAxkBAAEQEGVpSR-TuCKHP8D69SvDAAH2Gn7QjXEAAtIEAAKP9uhXzLPwoqMKxuQ2BA",
    "CAACAgUAAxkBAAEQEGVpSR-TuCKHP8D69SvDAAH2Gn7QjXEAAtIEAAKP9uhXzLPwoqMKxuQ2BA",
]

EMOJIOS = ["🚩", "🥀", "🪄", "🩷", "⚡", "❤️‍🩹", "🩶", "🩵", "💜", "🕊"]


# ==============================
# FORCE SUB
# ==============================

async def force_sub_private(message: Message):
    try:
        user_id = message.from_user.id

        member1 = await app.get_chat_member(f"@{FORCE_CHANNEL_1}", user_id)
        member2 = await app.get_chat_member(f"@{FORCE_CHANNEL_2}", user_id)

        if member1.status in ["left", "kicked"] or member2.status in ["left", "kicked"]:
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📢 Join Channel 1", url=f"https://t.me/{FORCE_CHANNEL_1}")],
                    [InlineKeyboardButton("📢 Join Channel 2", url=f"https://t.me/{FORCE_CHANNEL_2}")],
                    [InlineKeyboardButton("✅ I Have Joined", callback_data="check_sub")],
                ]
            )

            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption="🔒 **Access Denied!**\n\nYou must join both channels to use this bot.",
                reply_markup=buttons,
            )
            return True

    except Exception as e:
        print(e)

    return False


# ==============================
# PRIVATE START
# ==============================

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):

    if await force_sub_private(message):
        return

    await add_served_user(message.from_user.id)
    await message.react("🍓")

    accha = await message.reply_text(text=random.choice(EMOJIOS))
    await asyncio.sleep(1.3)
    await accha.edit("🔊 ᴘʟєᴧꜱє ᴡᴧɪᴛ... ʟєᴛ ᴛʜє ᴠɪʙєꜱ ʙєɢɪη 💫")
    await asyncio.sleep(0.2)
    await accha.edit("🎶✨ snowy ϻᴜꜱɪᴄ ꜱᴛᴧʀᴛɪηɢ ✨🎶")
    await asyncio.sleep(0.2)
    await accha.edit("__.ʜєʟʟσ ʜσω ᴧʀє ʏσᴜ 🩷 .__")
    await asyncio.sleep(0.2)
    await accha.delete()

    umm = await message.reply_sticker(sticker=random.choice(STICKER))
    await asyncio.sleep(2)
    await umm.delete()

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            return await message.reply_photo(
                random.choice(NEXT_IMG),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=help_pannel(_),
            )

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            return

    await message.reply_text(
        text=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(private_panel(_)),
    )


# ==============================
# CALLBACK
# ==============================

@app.on_callback_query(filters.regex("check_sub"))
async def check_subscription(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    member1 = await app.get_chat_member(f"@{FORCE_CHANNEL_1}", user_id)
    member2 = await app.get_chat_member(f"@{FORCE_CHANNEL_2}", user_id)

    if member1.status not in ["left", "kicked"] and member2.status not in ["left", "kicked"]:
        await callback_query.message.delete()
        await callback_query.message.reply_text("✅ Subscription Verified!\n\nNow send /start again.")
    else:
        await callback_query.answer("❌ You have not joined both channels!", show_alert=True)


# ==============================
# GROUP WELCOME
# ==============================

@app.on_message(filters.new_chat_members, group=-1)
async def welcome_handler(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
                continue

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🌷 sᴜᴘᴘσʀᴛ", url="https://t.me/snowy_hometown"),
                        InlineKeyboardButton("🔍 sᴜᴘєʀʙᴧηs", url="https://t.me/astral_superbans"),
                    ]
                ]
            )

            try:
                # OWNER WELCOME
                if member.id == config.OWNER_ID:
                    msg = await message.reply_photo(
                        photo=config.STYLE_ENTRY_IMG_URL,
                        has_spoiler=True,
                        caption=f"<blockquote><i><u>❍{member.mention}ᴛʜє ᴄᴏᴅєʀ σғ ᴛʜє ʙᴏᴛ ʜᴧs ᴊσɪηєᴅ ᴛʜє ᴄʜᴧᴛ ..\n⌯ ᴅσ ϻᴧɪηᴛᴧɪη ᴛʜє ᴄʜᴧᴛ σʀ ʙє ʀєᴧᴅʏ ᴛσ ғᴧᴄє ᴛʜє\n 🌷ᴊσɪη ᴛʜє sᴜᴘᴘσʀᴛ ᴄʜᴧᴛ ғσʀ ϻσʀє ɪηғσ ᴧηᴅ <a href='https://t.me/astral_superbans'>sᴜᴘєʀʙᴧη ʟσɢs</a> ғσʀ ᴄʜєᴄᴋɪηɢ sᴜᴘєʀʙᴧηs </u></i></blockquote>",
                        reply_markup=keyboard,
                    )
                    await asyncio.sleep(20)
                    await msg.delete()
                    continue

                # SUDO CHECK
                if isinstance(SUDOERS, (list, set)):
                    is_sudo = member.id in SUDOERS
                else:
                    is_sudo = member.id == SUDOERS

                # SUDO WELCOME
                if is_sudo:
                    msg = await message.reply_photo(
                        photo=config.STYLE_ENTRY_IMG_URL,
                        has_spoiler=True,
                        caption=f"<blockquote><i><u>⌯{member.mention} sᴜᴅσ ᴜsєʀ σғ ᴛʜє ʙᴏᴛ ʜᴧs ᴇηᴛєʀєᴅ ᴛʜє ᴄʜᴧᴛ ..\n✦ ᴘʟєᴧsє ᴋєєᴘ ᴛʜє ᴄʜᴧᴛ ᴄʟєᴧη ᴧηᴅ ғσʟʟσᴡ ᴛʜє ʀᴜʟєs\n❍ ϻɪsᴜsє σʀ sᴘᴧϻ ϻᴧʏ ʀєsᴜʟᴛ ɪη ᴧᴄᴛɪση\n🌷 ᴊσɪη ᴛʜє <a href='https://t.me/snowy_hometown'>sᴜᴘᴘσʀᴛ ᴄʜᴧᴛ</a> ғσʀ ϻσʀє ɪηғσ ᴧηᴅ <a href='https://t.me/astral_superbans'>sᴜᴘєʀʙᴧη ʟσɢs</a> ғσʀ ᴄʜєᴄᴋɪηɢ sᴜᴘєʀʙᴧηs</u></i></blockquote>",
                        reply_markup=keyboard,
                    )
                    await asyncio.sleep(20)
                    await msg.delete()

            except Exception as e:
                print(f"[WELCOME ERROR] {e}")

        except Exception as e:
            print(f"[MAIN LOOP ERROR] {e}")
