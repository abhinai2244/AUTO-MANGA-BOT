# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import Seishiro
from Plugins.helper import admin, get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
import asyncio


@Client.on_callback_query(filters.regex("^set_hyperlink_btn$"))
async def set_hyperlink_cb(client, callback_query):
    current = await Seishiro.get_config("hyperlink_enabled", False)
    new = not current
    await Seishiro.set_config("hyperlink_enabled", new)
    status = "Enabled" if new else "Disabled"
    await callback_query.answer(f"Hyperlinks {status}", show_alert=True)

@Client.on_callback_query(filters.regex("^set_regex_btn$"))
async def set_regex_cb(client, callback_query):
    text = get_styled_text(
        "<b>🔢 Set Regex Replacement</b>\n\n"
        "Send regex pattern to filter/replace in titles.\n"
        "Format: `pattern=replacement`\n"
        "<i>Send regex now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_regex"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_regex"))


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat