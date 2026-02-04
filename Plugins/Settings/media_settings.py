# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from Database.database import Seishiro
from Plugins.helper import admin, get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
import asyncio
import logging

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^(set_caption_btn|view_caption_cb)$"))
async def caption_settings_callback(client, callback_query):
    data = callback_query.data
    if data == "set_caption_btn":
        text = get_styled_text(
            "<b>📝 Set Caption</b>\n\n"
            "Sends the caption text you want to use.\n"
            "Variables: `{manga_name}`, `{chapter}`\n\n"
            "<i>Send text now...</i>"
        )
        user_states[callback_query.from_user.id] = {"state": "waiting_caption"}
        await edit_msg_with_pic(callback_query.message, text, None) # No buttons shown in this snippet but usually there are
    elif data == "view_caption_cb":
        pass

@Client.on_message(filters.command("set_caption") & filters.private & admin)
async def set_caption_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("usage: /set_caption <text>")
    text = message.text.split(None, 1)[1]
    await Seishiro.set_caption(text)
    await message.reply("<blockquote><b>✅ caption updated</b></blockquote>")

@Client.on_message(filters.command("set_banner") & filters.private & admin)
async def set_banner_cmd(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("reply to a photo to set banner.")
    file_id = message.reply_to_message.photo.file_id
    await Seishiro.set_config("banner_image", file_id)
    await message.reply("<blockquote><b>✅ banner image updated</b></blockquote>")


async def get_banner_menu(client):
    b1 = await Seishiro.get_config("banner_image_1")
    b2 = await Seishiro.get_config("banner_image_2")
    
    status_1 = "Set" if b1 else "None"
    status_2 = "Set" if b2 else "None"
    
    text = get_styled_text(
        f"<b>Banner Setting</b>\n\n"
        f"➥ Frist Banner: {status_1}\n"
        f"➥ Last Banner: {status_2}"
    )
    
    buttons = [
        [
            InlineKeyboardButton("set / change - 1", callback_data="set_banner_1"),
            InlineKeyboardButton("delete - 1", callback_data="del_banner_1")
        ],
        [InlineKeyboardButton("show banner - 1", callback_data="show_banner_1")],
        
        [
            InlineKeyboardButton("set / change - 2", callback_data="set_banner_2"),
            InlineKeyboardButton("delete - 2", callback_data="del_banner_2")
        ],
        [InlineKeyboardButton("show banner - 2", callback_data="show_banner_2")],
        
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu"),
            InlineKeyboardButton("❄ close ❄", callback_data="stats_close")
        ]
    ]
    return text, InlineKeyboardMarkup(buttons)

@Client.on_callback_query(filters.regex("^set_banner_btn$"))
async def set_banner_cb(client, callback_query):
    text, markup = await get_banner_menu(client)
    await edit_msg_with_pic(callback_query.message, text, markup)

@Client.on_callback_query(filters.regex("^set_banner_(1|2)$"))
async def set_banner_input_cb(client, callback_query):
    num = callback_query.data.split("_")[-1]
    text = get_styled_text(
        f"<i>Send Banner {num} image now...</i>\n"
        f"<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": f"waiting_banner_{num}"}
    
    buttons = [
        [InlineKeyboardButton("❌ cancel", callback_data="cancel_input")],
        [InlineKeyboardButton("⬅ back", callback_data="settings_menu")]
    ]
    
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, f"waiting_banner_{num}"))

@Client.on_callback_query(filters.regex("^del_banner_(1|2)$"))
async def del_banner_cb(client, callback_query):
    num = callback_query.data.split("_")[-1]
    await Seishiro.set_config(f"banner_image_{num}", None)
    await callback_query.answer(f"Banner {num} deleted!", show_alert=True)
    await set_banner_cb(client, callback_query)

# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^show_banner_(1|2)$"))
async def show_banner_cb(client, callback_query):
    num = callback_query.data.split("_")[-1]
    file_id = await Seishiro.get_config(f"banner_image_{num}")
    if file_id:
        await callback_query.message.reply_photo(file_id, caption=f"banner {num}")
    else:
        await callback_query.answer("no banner set.", show_alert=True)

@Client.on_callback_query(filters.regex("^set_caption_btn$"))
async def set_caption_cb(client, callback_query):
    curr = await Seishiro.get_caption()
    curr_disp = "set" if curr else "None"
    
    text = get_styled_text(
        "<b>caption</b>\n\n"
        "<b>format:</b>\n"
        "➥ {manga_title}: manga name\n"
        "➥ {chapter_num}: chapter number\n"
        "➥ {file_name}: file name\n\n"
        f"➥ Your Value: {curr_disp}"
    )
    
    buttons = [
        [
            InlineKeyboardButton("set / change", callback_data="set_caption_input"),
            InlineKeyboardButton("delete", callback_data="del_caption_btn")
        ],
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu"),
            InlineKeyboardButton("❄ close ❄", callback_data="stats_close")
        ]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex("^set_caption_input$"))
async def caption_input_cb(client, callback_query):
    text = get_styled_text(
        "<i>Send new caption text now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_caption"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_caption"))

@Client.on_callback_query(filters.regex("^del_caption_btn$"))
async def del_caption_cb_ui(client, callback_query):
    await Seishiro.set_caption(None)
    await callback_query.answer("Caption deleted!", show_alert=True)
    await set_caption_cb(client, callback_query)


@Client.on_callback_query(filters.regex("^set_(channel_stickers|update_sticker)_btn$"))
async def sticker_placeholder(client, callback_query):
    key = callback_query.data
    text = get_styled_text(
        f"<b>👾 Set {key.replace('set_', '').replace('_btn', '').replace('_', ' ').title()}</b>\n\n"
        "Send the sticker ID or Sticker now.\n"
        "<i>Send sticker now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": f"waiting_{key}"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, f"waiting_{key}"))

@Client.on_callback_query(filters.regex("^set_update_text_btn$"))
async def update_text_cb(client, callback_query):
    text = get_styled_text(
        "<b>📝 Set Update Text</b>\n\n"
        "Send the text for updates.\n"
        "<i>Send text now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_update_text"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_update_text"))

@Client.on_callback_query(filters.regex("^set_thumb_btn$"))
async def set_thumb_cb(client, callback_query):
    text = get_styled_text(
        "<b>🖼️ Set Thumbnail</b>\n\n"
        "Send the photo to use as default thumbnail.\n"
        "<i>Send photo now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_thumb"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_thumb"))



# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat