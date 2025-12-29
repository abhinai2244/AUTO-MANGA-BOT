# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from Database.database import Seishiro
from Database.database import Seishiro
from Plugins.helper import get_styled_text, admin, edit_msg_with_pic

@Client.on_callback_query(filters.regex("^settings_menu$|^settings_menu_1$"))
async def settings_main_menu(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        if user_id != Config.USER_ID and not await Seishiro.is_admin(user_id):
            await callback_query.answer("❌ You are not authorized to use settings.", show_alert=True)
            return

        buttons = [
            [InlineKeyboardButton("ᴀᴜᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟs", callback_data="header_auto_update_channels")],
            
            [
                InlineKeyboardButton("ʙᴀɴɴᴇʀ", callback_data="set_banner_btn"),
                InlineKeyboardButton("ᴄᴀᴘᴛɪᴏɴ", callback_data="set_caption_btn")
            ],
            [
                InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ sᴛɪᴄᴋᴇʀs", callback_data="set_channel_stickers_btn"),
                InlineKeyboardButton("ᴄᴏᴍᴘʀᴇss", callback_data="set_compress_btn")
            ],
            [
                InlineKeyboardButton("ꜰɪʟᴇ ɴᴀᴍᴇ", callback_data="set_format_btn"),
                InlineKeyboardButton("ꜰɪʟᴇ ᴛʏᴘᴇ", callback_data="set_file_type_btn")
            ],

            [InlineKeyboardButton("ʀᴇxʙᴏᴛs ᴏꜰꜰɪᴄᴀʟ", callback_data="header_watermark")],

            [
                InlineKeyboardButton("ʜʏᴘᴇʀ ʟɪɴᴋ", callback_data="set_hyperlink_btn"),
                InlineKeyboardButton("ᴍᴇʀɢᴇ sɪᴢᴇ", callback_data="set_merge_size_btn")
            ],
            [
                InlineKeyboardButton("ᴘᴀssᴡᴏʀᴅ", callback_data="set_password_btn"),
                InlineKeyboardButton("ʀᴇɢᴇx", callback_data="set_regex_btn")
            ],
            [
                InlineKeyboardButton("ᴛʜᴜᴍʙɴᴀɪʟ", callback_data="set_thumb_btn"), 
                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", callback_data="set_channel_btn")
            ],

            [
                InlineKeyboardButton("✨ ʜᴏᴍᴇ ✨", callback_data="start_menu"),
                InlineKeyboardButton("➡️ ɴᴇxᴛ ➡️", callback_data="settings_menu_2")
            ]
        ]
        
        text = (
            "<blockquote><b>⚙️ Settings Menu (Page 1/2)</b></blockquote>\n\n"
            "<blockquote>Select an option below to configure the bot. "
            "All changes are saved instantly to the database.</blockquote>"
        )

        await edit_msg_with_pic(
            message=callback_query.message,
            text=text,
            buttons=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer("Error opening settings")

@Client.on_callback_query(filters.regex("^settings_menu_2$"))
async def settings_main_menu_2(client, callback_query):
    try:
        buttons = [
            [InlineKeyboardButton("ᴅᴜᴍᴘ ᴄʜᴀɴɴᴇʟ", callback_data="header_dump_channel")],

            [
                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴛᴇxᴛ", callback_data="set_update_text_btn"),
            ],

            [InlineKeyboardButton("ᴍᴏɴɪᴛᴏʀ & ꜰsᴜʙ", callback_data="header_new_items")],

            [
                InlineKeyboardButton(f"Monitor: {'✅ ON' if await Seishiro.get_monitoring_status() else '❌ OFF'}", callback_data="toggle_monitor"),
                InlineKeyboardButton("ᴠɪᴇᴡ ᴘʀᴏɢʀᴇss 📊", callback_data="view_progress")
            ],

            [
                InlineKeyboardButton("sᴇᴛ ɪɴᴛᴇʀᴠᴀʟ", callback_data="set_interval_btn"),
                InlineKeyboardButton("ꜰsᴜʙ ᴍᴏᴅᴇ", callback_data="set_fsub_btn")
            ],
            [
                InlineKeyboardButton("ᴡᴀᴛᴇʀᴍᴀʀᴋ", callback_data="set_watermark_btn"),
                InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ", callback_data="set_deltimer_btn")
            ],

            [InlineKeyboardButton("ᴍᴀɴɢᴀ sᴏᴜʀᴄᴇ", callback_data="header_source")],

            [
                InlineKeyboardButton(f"📡 Source: {await Seishiro.get_config('manga_source', 'mangadex')}", callback_data="set_source_btn")
            ],

            [InlineKeyboardButton("ᴀᴅᴍɪɴ ᴄᴏɴᴛʀᴏʟs", callback_data="header_admins")],
            
            [
                InlineKeyboardButton("ᴀᴅᴍɪɴs 👮‍♂️", callback_data="admin_menu_btn")
            ],

            [
                InlineKeyboardButton("⬅️ ʙᴀᴄᴋ ⬅️", callback_data="settings_menu_1"),
                InlineKeyboardButton("❄️ ᴄʟᴏsᴇ ❄️", callback_data="stats_close")
            ]
        ]
        
        dump_ch = await Seishiro.get_config("dump_channel")
        update_ch = await Seishiro.get_default_channel()
        
        text = (
            "<blockquote><b>⚙️ Settings Menu (Page 2/2)</b></blockquote>\n\n"
            f"<b>Current Channels:</b>\n"
            f"🗑️ Dump: `{dump_ch if dump_ch else 'Not Set'}`\n"
            f"📢 Update: `{update_ch if update_ch else 'Not Set'}`\n\n"
            "<blockquote>Use arrows to navigate between pages.</blockquote>"
        )

        await edit_msg_with_pic(
            message=callback_query.message,
            text=text,
            buttons=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer("Error opening settings page 2")

@Client.on_callback_query(filters.regex("^header_(?!dump_channel|source|auto_update_channels|auto_upload_channels|new_items)"))
async def header_callback(client, callback_query):
    await callback_query.answer("Values in this section:", show_alert=False)

@Client.on_callback_query(filters.regex("^stats_close$"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()

@Client.on_callback_query(filters.regex("^start_menu$"))
async def start_menu_cb(client, callback_query):
    caption = (
        f"<b>👋 Hello {callback_query.from_user.first_name}!</b>\n\n"
        f"<blockquote>I am an advanced Manga Downloader & Uploader Bot.</blockquote>\n\n"
        f"<i>Click the buttons below to control me!</i>"
    )
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_menu"),
            InlineKeyboardButton("📚 ʜᴇʟᴘ", callback_data="help_menu")
        ],
        [
            InlineKeyboardButton("📢 ᴏꜰꜰɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ", url="https://t.me/akaza7902"),
            InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/akaza7902")
        ]
    ])
    await edit_msg_with_pic(callback_query.message, caption, buttons)


@Client.on_callback_query(filters.regex("^set_source_btn$"))
async def set_source_menu(client, callback_query):
    try:
        current = await Seishiro.get_config('manga_source', 'mangadex')
        text = (
            "<b>📡 Select Manga Source</b>\n\n"
            "<blockquote>Choose which source the bot should use for automatic updates and searching.</blockquote>\n\n"
            f"<b>Current:</b> <code>{current}</code>"
        )
        
        buttons = [
            [
                InlineKeyboardButton(f"{'✅ ' if current == 'mangadex' else ''}MangaDex", callback_data="set_source_mangadex"),
                InlineKeyboardButton(f"{'✅ ' if current == 'webcentral' else ''}WebCentral", callback_data="set_source_webcentral")
            ],
            [
                InlineKeyboardButton(f"{'✅ ' if current == 'mangaforest' else ''}MangaForest", callback_data="set_source_mangaforest"),
                InlineKeyboardButton(f"{'✅ ' if current == 'mangakakalot' else ''}Mangakakalot", callback_data="set_source_mangakakalot")
            ],
            [
                InlineKeyboardButton(f"{'✅ ' if current == 'allmanga' else ''}AllManga", callback_data="set_source_allmanga")
            ],
            [
                InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu")
            ]
        ]
        
        await edit_msg_with_pic(
            message=callback_query.message,
            text=text,
            buttons=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await callback_query.answer("Error opening source menu")

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^set_source_(.+)$"))
async def set_source_callback(client, callback_query):
    new_source = callback_query.matches[0].group(1)
    await Seishiro.set_config('manga_source', new_source)
    await callback_query.answer(f"Source set to: {new_source}", show_alert=True)
    await set_source_menu(client, callback_query)


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat