# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

import base64
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from Bot import Config

logger = logging.getLogger(__name__)

def encode_payload(string):
    if not string:
        return ""
    return base64.urlsafe_b64encode(string.encode("utf-8")).decode("utf-8").rstrip("=")

@Client.on_message(filters.command("makepost"))
async def create_post(Client: Client, Message: Message):
    if message.from_user.id != Config.USER_ID:
        return

    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text("❌ please reply to a document/file to create a post.")
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text(
            "❌ **usage:** `/makepost <Manga Name> | <Caption>`\n"
            "Reply to the file you want to link.\n\n"
            "Example: `/makepost Naruto | Best series ever!`"
        )
        return

    content = args[1]
    if "|" in content:
        parts = content.split("|", 1)
        manga_name = parts[0].strip()
        caption_text = parts[1].strip()
    else:
        manga_name = content.strip()
        caption_text = "click the button below to read."

    file_id = message.reply_to_message.document.file_id
    encoded_id = encode_payload(file_id)
    
    bot_username = Client.me.username
    if not bot_username:
        try:
            me = await client.get_me()
            bot_username = me.username
        except:
            bot_username = "YourBotUserName" # Fallback

    link = f"https://t.me/{bot_username}?start=dl_{encoded_id}"
    
    text = (
        f"<blockquote><b>{manga_name}</b></blockquote>\n\n" 
        f"<blockquote>{caption_text}</blockquote>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 read manga", url=link)]
    ])
    
    await message.reply_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat