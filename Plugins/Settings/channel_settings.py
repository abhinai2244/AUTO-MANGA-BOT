# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import Seishiro
from Plugins.helper import admin, get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
import asyncio
import logging

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^header_auto_update_channels$"))
async def auc_menu(client, callback_query):
    text = get_styled_text("Your Auto Update Channel")
    
    buttons = [
        [
            InlineKeyboardButton("+ add +", callback_data="auc_add"),
            InlineKeyboardButton("- remove all -", callback_data="auc_rem_all")
        ],
        [
            InlineKeyboardButton("- remove channel -", callback_data="auc_rem_channel")
        ],
        [
            InlineKeyboardButton("refresh", callback_data="header_auto_update_channels"),
            InlineKeyboardButton("import", callback_data="auc_import")
        ],
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu"),
            InlineKeyboardButton("* close *", callback_data="stats_close")
        ]
    ]
    
    await callback_query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^auc_add$"))
async def auc_add_cb(client, callback_query):
    text = get_styled_text(
        "<b>➕ Add Auto Update Channel</b>\n\n"
        "Send the Channel ID (e.g. -100xxx) to add.\n"
        "<i>Bot must be admin in the channel to verify!</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_auc_id"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_auc_id"))

@Client.on_callback_query(filters.regex("^auc_rem_all$"))
async def auc_rem_all_cb(client, callback_query):
    await Seishiro.clear_auto_update_channels()
    await callback_query.answer("✅ All channels removed!", show_alert=True)
    await auc_menu(client, callback_query) # Refresh menu

@Client.on_callback_query(filters.regex("^auc_import$"))
async def auc_import_cb(client, callback_query):
    await callback_query.answer("Import feature coming soon!", show_alert=True)


@Client.on_callback_query(filters.regex("^auc_rem_channel$"))
async def auc_rem_channel_cb(client, callback_query):
    text = get_styled_text(
        "<b>➖ Remove Auto Update Channel</b>\n\n"
        "Send the Channel ID (e.g. -100xxx) to remove.\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_auc_rem_id"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_auc_rem_id"))


@Client.on_callback_query(filters.regex("^set_channel_btn$"))
async def set_channel_cb(client, callback_query):
    text = get_styled_text(
        "<b>📢 Set Upload Channel</b>\n\n"
        "Send the Channel ID (-100...) where manga chapters will be uploaded.\n"
        "<i>Make sure the bot is Admin there!</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_channel"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_channel"))

@Client.on_callback_query(filters.regex("^(header_dump_channel|set_dump_channel_btn)$"))
async def dump_channel_menu(client, callback_query):
    dump_id = await Seishiro.get_config("dump_channel")
    status = f"<code>{dump_id}</code>" if dump_id else "None"
    
    text = (
        f"<b>➥ Dump Channel</b>\n"
        f"<b>➥ Your Value: {status}</b>"
    )
    
    buttons = [
        [
            InlineKeyboardButton("set / change", callback_data="set_dump_input"),
            InlineKeyboardButton("delete", callback_data="rem_dump_channel")
        ],
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu"),
            InlineKeyboardButton("* close *", callback_data="stats_close")
        ]
    ]
    
    try:
        if callback_query.message.photo:
             await callback_query.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        else:
             await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    except Exception as e:
         pass

# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^set_dump_input$"))
async def set_dump_input_cb(client, callback_query):
    text = get_styled_text(
        "<b>🗑️ Set Dump Channel</b>\n\n"
        "Send the Channel ID for the Dump Channel.\n"
        "<i>Send ID now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_dump_channel"}
    
    buttons = [
        [InlineKeyboardButton("❌ cancel", callback_data="cancel_input")],
        [InlineKeyboardButton("⬅ back", callback_data="header_dump_channel")]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_dump_channel"))

@Client.on_callback_query(filters.regex("^rem_dump_channel$"))
async def rem_dump_channel_cb(client, callback_query):
    await Seishiro.set_config("dump_channel", None)
    await callback_query.answer("Dump Channel Removed!", show_alert=True)
    await dump_channel_menu(client, callback_query)


@Client.on_message(filters.command("set_chnl") & filters.private & admin)
async def set_channel_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply("usage: /set_chnl <channel_id>")
    try:
        cid = int(message.command[1])
        try:
             chat = await client.get_chat(cid)
        except:
             return await message.reply("❌ bot cannot access this channel.")
        await Seishiro.set_default_channel(cid)
        await message.reply(f"<blockquote><b>✅ upload channel set: {cid}</b></blockquote>", parse_mode=enums.ParseMode.HTML)
    except ValueError:
        await message.reply("❌ invalid id")

@Client.on_message(filters.command("view_chnl") & filters.private & admin)
async def view_channel_cmd(client, message):
    cid = await Seishiro.get_default_channel()
    await message.reply(f"<blockquote><b>📺 Upload Channel: {cid}</b></blockquote>", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command("rem_chnl") & filters.private & admin)
async def rem_channel_cmd(client, message):
    await Seishiro.set_default_channel(None)
    await message.reply(f"<blockquote><b>✅ Upload Channel Removed</b></blockquote>", parse_mode=enums.ParseMode.HTML)


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat