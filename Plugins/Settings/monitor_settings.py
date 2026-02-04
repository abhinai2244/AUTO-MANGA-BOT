# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Database.database import Seishiro
from Plugins.helper import get_styled_text, user_states, edit_msg_with_pic
from Plugins.Settings.input_helper import timeout_handler
from Plugins.Settings.main_settings import settings_main_menu_2
import asyncio
import logging

logger = logging.getLogger(__name__)


@Client.on_callback_query(filters.regex("^set_interval_btn$"))
async def set_interval_menu(client, callback_query):
    current = await Seishiro.get_check_interval()
    
    text = get_styled_text(
        "<b>⏱ Set Check Interval</b>\n\n"
        "Wait time between checking for new chapters.\n"
        "Minimum: 60s (1 min), Maximum: 3600s (1 hour)\n\n"
        f"<b>Current:</b> {current}s"
    )
    
    buttons = [
        [
            InlineKeyboardButton("5 min", callback_data="set_int_300"),
            InlineKeyboardButton("10 min", callback_data="set_int_600"),
            InlineKeyboardButton("30 min", callback_data="set_int_1800")
        ],
        [
            InlineKeyboardButton("1 hour", callback_data="set_int_3600"),
            InlineKeyboardButton("custom", callback_data="set_int_custom")
        ],
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu_2")
        ]
    ]
    
    await edit_msg_with_pic(
        message=callback_query.message,
        text=text,
        buttons=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^set_int_(\\d+)$"))
async def set_int_preset_cb(client, callback_query):
    seconds = int(callback_query.matches[0].group(1))
    success = await Seishiro.set_check_interval(seconds)
    if success:
        await callback_query.answer(f"✅ Interval set to {seconds}s", show_alert=True)
    else:
        await callback_query.answer("❌ Error setting interval", show_alert=True)
    await set_interval_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^set_int_custom$"))
async def set_int_custom_cb(client, callback_query):
    text = get_styled_text(
        "<b>⏱ Set Custom Interval</b>\n\n"
        "Send the interval in seconds (60-3600).\n"
        "<i>Send number now...</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_interval"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_interval"))



@Client.on_callback_query(filters.regex("^set_fsub_btn$"))
async def fsub_main_menu(client, callback_query):
    channels = await Seishiro.get_fsub_channels()
    
    text = get_styled_text(
        "<b>🛡 FSub Mode Settings</b>\n\n"
        f"<b>Active FSub Channels:</b> {len(channels)}"
    )
    
    buttons = [
        [
            InlineKeyboardButton("➕ add channel", callback_data="fsub_add"),
            InlineKeyboardButton("➖ remove channel", callback_data="fsub_remove")
        ],
        [
            InlineKeyboardButton("📋 list channels", callback_data="fsub_list")
        ],
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu_2")
        ]
    ]
    
    await edit_msg_with_pic(
        Message=callback_query.message,
        text=text,
        buttons=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^fsub_add$"))
async def fsub_add_cb(client, callback_query):
    text = get_styled_text(
        "<b>➕ Add FSub Channel</b>\n\n"
        "Send Channel ID (-100...).\n"
        "<i>Bot must be Admin!</i>\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_fsub_id"}
    
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_fsub_id"))

@Client.on_callback_query(filters.regex("^fsub_list$"))
async def fsub_list_cb(client, callback_query):
    channels = await Seishiro.get_fsub_channels()
    if not channels:
        await callback_query.answer("No FSub channels set.", show_alert=True)
        return
        
    msg = "<b>📋 FSub Channels:</b>\n\n"
    for ch in channels:
        mode = await Seishiro.get_channel_mode(ch)
        msg += f"• <code>{ch}</code> | Mode: {mode}\n"
        
    buttons = [[InlineKeyboardButton("⬅ back", callback_data="set_fsub_btn")]]
    await edit_msg_with_pic(callback_query.message, get_styled_text(msg), InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^fsub_remove$"))
async def fsub_remove_cb(client, callback_query):
    text = get_styled_text(
        "<b>➖ Remove FSub Channel</b>\n\n"
        "Send Channel ID to remove.\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_fsub_rem_id"}
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_fsub_rem_id"))


@Client.on_callback_query(filters.regex("^set_watermark_btn$"))
async def watermark_menu(client, callback_query):
    wm = await Seishiro.get_watermark()
    status = "Set" if wm else "None"
    
    text = get_styled_text(
        "<b>💧 Watermark Settings</b>\n\n"
        "Add branding to your images.\n"
        f"<b>Status:</b> {status}\n\n"
        "Variables: `{manga_name}`, `{chapter}`"
    )
    
    buttons = [
        [
            InlineKeyboardButton("set text", callback_data="wm_set_text"),
            InlineKeyboardButton("set position", callback_data="wm_set_pos")
        ],
        [
            InlineKeyboardButton("set color", callback_data="wm_set_color"),
            InlineKeyboardButton("set opacity", callback_data="wm_set_opacity")
        ],
        [
            InlineKeyboardButton("delete watermark", callback_data="wm_delete")
        ],
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu_2")
        ]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^wm_set_text$"))
async def wm_set_text_cb(client, callback_query):
    text = get_styled_text(
        "<b>💧 Set Watermark Text</b>\n"
        "Send the text you want to use.\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_wm_text"}
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_wm_text"))

# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^wm_delete$"))
async def wm_delete_cb(client, callback_query):
    await Seishiro.delete_watermark()
    await callback_query.answer("Watermark deleted!", show_alert=True)
    await watermark_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^wm_set_pos$"))
async def wm_set_pos_cb(client, callback_query):
    text = get_styled_text("<b>📍 Select Watermark Position</b>")
    buttons = [
        [
            InlineKeyboardButton("top left", callback_data="wm_pos_top-left"),
            InlineKeyboardButton("top right", callback_data="wm_pos_top-right")
        ],
        [
            InlineKeyboardButton("bottom left", callback_data="wm_pos_bottom-left"),
            InlineKeyboardButton("bottom right", callback_data="wm_pos_bottom-right")
        ],
        [
            InlineKeyboardButton("center", callback_data="wm_pos_center")
        ],
        [InlineKeyboardButton("⬅ back", callback_data="set_watermark_btn")]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^wm_pos_(.+)$"))
async def wm_pos_set_cb(client, callback_query):
    pos = callback_query.data.split("wm_pos_")[1]
    wm = await Seishiro.get_watermark() or {}
    await Seishiro.set_watermark(
        text=wm.get("text", "Default Watermark"),
        position=pos,
        color=wm.get("color", "#FFFFFF"),
        opacity=wm.get("opacity", 128),
        font_size=wm.get("font_size", 20)
    )
    await callback_query.answer(f"Position set to {pos}", show_alert=True)
    await watermark_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^wm_set_color$"))
async def wm_set_color_cb(client, callback_query):
    text = get_styled_text(
        "<b>🎨 Set Watermark Color</b>\n"
        "Send Hex Color Code (e.g. #FF0000 for Red).\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_wm_color"}
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_wm_color"))

@Client.on_callback_query(filters.regex("^wm_set_opacity$"))
async def wm_set_opacity_cb(client, callback_query):
    text = get_styled_text(
        "<b>👻 Set Watermark Opacity</b>\n"
        "Send a number between 0 (Transparent) and 255 (Opaque).\n"
        "<i>(Auto-close in 30s)</i>"
    )
    user_states[callback_query.from_user.id] = {"state": "waiting_wm_opacity"}
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_wm_opacity"))


@Client.on_callback_query(filters.regex("^set_deltimer_btn$"))
async def deltimer_menu(client, callback_query):
    current = await Seishiro.get_del_timer()
    text = get_styled_text(
        "<b>⏲ Auto-Delete Timer</b>\n\n"
        "Set how long to keep files in Dump Channel before deleting (if enabled).\n"
        f"<b>Current:</b> {current}s"
    )
    
    buttons = [
        [
            InlineKeyboardButton("10 min", callback_data="set_dt_600"),
            InlineKeyboardButton("30 min", callback_data="set_dt_1800"),
            InlineKeyboardButton("1 hour", callback_data="set_dt_3600")
        ],
        [
            InlineKeyboardButton("custom", callback_data="set_dt_custom"),
            InlineKeyboardButton("disable (0)", callback_data="set_dt_0")
        ],
        [
            InlineKeyboardButton("⬅ back", callback_data="settings_menu_2")
        ]
    ]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^set_dt_(\\d+)$"))
async def set_dt_preset(client, callback_query):
    val = int(callback_query.matches[0].group(1))
    await Seishiro.set_del_timer(val)
    await callback_query.answer(f"Timer set to {val}s", show_alert=True)
    await deltimer_menu(client, callback_query)

@Client.on_callback_query(filters.regex("^set_dt_custom$"))
async def set_dt_custom(client, callback_query):
    text = get_styled_text("<i>Send timer value in seconds...</i>")
    user_states[callback_query.from_user.id] = {"state": "waiting_deltimer"}
    buttons = [[InlineKeyboardButton("❌ cancel", callback_data="cancel_input")]]
    await edit_msg_with_pic(callback_query.message, text, InlineKeyboardMarkup(buttons))
    asyncio.create_task(timeout_handler(client, callback_query.message, callback_query.from_user.id, "waiting_deltimer"))


@Client.on_callback_query(filters.regex("^toggle_monitor$"))
async def toggle_monitor_cb(client, callback_query):
    current = await Seishiro.get_monitoring_status()
    new_status = not current
    await Seishiro.set_monitoring_status(new_status)
    
    status_text = "enabled" if new_status else "Disabled"
    await callback_query.answer(f"Monitoring {status_text}!", show_alert=True)
    
    if new_status:
        try:
            if hasattr(client, 'bot_instance'):
                asyncio.create_task(client.bot_instance.check_updates())
            else:
                logger.warning("bot_instance not attached to Client!")
        except Exception as e:
            logger.error(f"Failed to trigger immediate check: {e}")

    await settings_main_menu_2(client, callback_query)

@Client.on_callback_query(filters.regex("^view_progress$"))
async def view_progress_cb(client, callback_query):
    state = await Seishiro.get_upload_state()
    
    if not state:
        text = get_styled_text(
            "<b>📊 Bot Progress</b>\n\n"
            "➥ Idle (No active tasks)"
        )
    else:
        title = state.get('manga_title', 'Unknown Task')
        curr = state.get('processed', 0)
        total = state.get('total', 1)
        
        if total == 0: total = 1
        percent = (curr / total) * 100
        
        filled_len = int(10 * curr // total)
        bar = "█" * filled_len + "░" * (10 - filled_len)
        
        text = get_styled_text(
            f"<b>📊 Bot Progress</b>\n\n"
            f"<b>Task:</b> {title}\n"
            f"<b>Progress:</b> [{bar}] {percent:.1f}%\n"
            f"<b>Count:</b> {curr}/{total}"
        )
    
    buttons = [
        [InlineKeyboardButton("🔄 refresh", callback_data="view_progress")],
        [InlineKeyboardButton("⬅ back", callback_data="settings_menu_2")]
    ]
    
    try:
        if callback_query.message.photo:
            await callback_query.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        else:
            await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    except Exception:
        pass # Ignore Message not modified errors


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat