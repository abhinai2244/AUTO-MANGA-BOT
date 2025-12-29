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


@Client.on_callback_query(filters.regex("^set_format_btn$"))
async def set_format_cb(client, callback_query):
    text = get_styled_text(
        "<b>📂 Set File Name Format</b>\n\n"
        "Current Format: " + await Seishiro.get_format() + "\n\n"
        "Variables: `{manga_name}`, `{chapter}`\n"
        "<i>Send new format now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_format"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_format"))

@Client.on_callback_query(filters.regex("^set_file_type_btn$"))
async def set_file_type_cb(client, callback_query):
    current = await Seishiro.get_config("file_type", "PDF")
    new = "CBZ" if current == "PDF" else "PDF"
    await Seishiro.set_config("file_type", new)
    await callback_query.answer(f"File Type switched to {new}", show_alert=True)

@Client.on_callback_query(filters.regex("^set_compress_btn$"))
async def set_compress_cb(client, callback_query):
    quality = await Seishiro.get_config("image_quality") # If None, assume 100 or original
    val_disp = f"{quality}" if quality is not None else "None"
    
    text = get_styled_text(
        f"<b>Image Compress</b>\n\n"
        f"➥ Your Value: {val_disp}"
    )
    
    buttons = []
    row = []
    for i in range(0, 101, 5):
        row.append(InlineKeyboardButton(str(i), callback_data=f"set_qual_{i}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton("| ᴅᴇʟᴇᴛᴇ |", callback_data="del_quality")])
    buttons.append([
        InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
        InlineKeyboardButton("| ᴄʟᴏsᴇ |", callback_data="stats_close")
    ])
    
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex("^set_qual_"))
async def set_quality_action(client, callback_query):
    qual = int(callback_query.data.split("_")[-1])
    await Seishiro.set_config("image_quality", qual)
    await callback_query.answer(f"Quality set to {qual}%", show_alert=True)
    await set_compress_cb(client, callback_query)

@Client.on_callback_query(filters.regex("^del_quality$"))
async def del_quality_action(client, callback_query):
    await Seishiro.set_config("image_quality", None)
    await callback_query.answer("Compression removed (Default 100%)", show_alert=True)
    await set_compress_cb(client, callback_query)

@Client.on_callback_query(filters.regex("^set_password_btn$"))
async def set_password_cb(client, callback_query):
    text = get_styled_text(
        "<b>🔐 Set PDF Password</b>\n\n"
        "Send the password to protect PDFs with.\n"
        "Send `OFF` to disable.\n"
        "<i>Send password now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_password"}
    
    buttons = [[InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_password"))

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^set_merge_size_btn$"))
async def set_merge_size_cb(client, callback_query):
    current = await Seishiro.get_config("merge_size_limit", "Unset")
    text = get_styled_text(
        f"<b>⚖️ Merge Size Limit</b>\n\n"
        f"Current: {current}MB\n\n"
        "Select a preset or choose Custom:"
    )
    buttons = [
        [
            InlineKeyboardButton("50 ᴍʙ", callback_data="set_ms_50"),
            InlineKeyboardButton("100 ᴍʙ", callback_data="set_ms_100"),
            InlineKeyboardButton("500 ᴍʙ", callback_data="set_ms_500")
        ],
        [
            InlineKeyboardButton("ᴄᴜsᴛᴏᴍ", callback_data="set_ms_custom"),
            InlineKeyboardButton("ᴅɪsᴀʙʟᴇ", callback_data="set_ms_disable")
        ],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex("^set_ms_"))
async def merge_size_action(client, callback_query):
    action = callback_query.data.split("_")[2]
    if action == "custom":
        user_states[callback_query.from_user.id] = {"state": "waiting_merge_size"}
        text = get_styled_text(
             "<i>Send size limit (MB) now...</i>\n"
             "<i>(Auto-close in 30s)</i>"
        )
        buttons = [
            [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_input")],
            [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu")]
        ]
        await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
        
        asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_merge_size"))
    elif action == "disable":
        await Seishiro.set_config("merge_size_limit", 0)
        await callback_query.answer("Merge size limit disabled!", show_alert=True)
        await set_merge_size_cb(client, callback_query) # refresh
    else:
        try:
            size = int(action)
            await Seishiro.set_config("merge_size_limit", size)
            await callback_query.answer(f"Limit set to {size}MB", show_alert=True)
            await set_merge_size_cb(client, callback_query)
        except:
            await callback_query.answer("Error", show_alert=True)

@Client.on_message(filters.command("set_format") & filters.private & admin)
async def set_format_cmd(client, message):
    if len(message.command) < 2:
        curr = await Seishiro.get_format()
        return await message.reply(f"ᴜsᴀɢᴇ: /sᴇᴛ_ꜰᴏʀᴍᴀᴛ <format>\ɴᴄᴜʀʀᴇɴᴛ: `{curr}`")
    ꜰᴍᴛ = ᴍᴇssᴀɢᴇ.ᴛᴇxᴛ.sᴘʟɪᴛ(ɴᴏɴᴇ, 1)[1]
    ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.sᴇᴛ_ꜰᴏʀᴍᴀᴛ(ꜰᴍᴛ)
    ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ(f"<blockquote><b>✅ Format Updated</b></blockquote>\n`{fmt}`", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command("view_format") & filters.private & admin)
async def view_format_cmd(client, message):
    fmt = await Seishiro.get_format()
    await message.reply(f"<b>Current Format:</b>\n`{fmt}`", parse_mode=enums.ParseMode.HTML)


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat