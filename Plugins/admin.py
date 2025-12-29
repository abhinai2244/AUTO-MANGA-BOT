# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from Database.database import Seishiro
from Plugins.helper import admin, check_ban, get_styled_text, user_states

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("add_admin") & filters.private & admin)
async def add_admin_handler(client, message):
    try:
        logger.info(f"Add admin command from {message.from_user.id}")
        if len(message.command) != 2:
            return await message.reply("<b>ᴜsᴀɢᴇ: /ᴀᴅᴅ_ᴀᴅᴍɪɴ <user_id></b>")
        
        user_id = int(message.command[1])
        await Seishiro.add_admin(user_id)
        await message.reply(f"<b>✅ ᴜsᴇʀ {user_id} ᴀᴅᴅᴇᴅ ᴀs ᴀᴅᴍɪɴ</b>", ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ)
        ʟᴏɢɢᴇʀ.ɪɴꜰᴏ(f"User {user_id} added as admin by {message.from_user.id}")
    except ValueError:
        await message.reply("<b>ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ</b>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        await message.reply(f"❌ ᴇʀʀᴏʀ: {str(e)}")

@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("ᴅᴇʟᴀᴅᴍɪɴ") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ ᴅᴇʟ_ᴀᴅᴍɪɴ_ʜᴀɴᴅʟᴇʀ(ᴄʟɪᴇɴᴛ, ᴍᴇssᴀɢᴇ):
    ᴛʀʏ:
        ʟᴏɢɢᴇʀ.ɪɴꜰᴏ(f"Del admin command from {message.from_user.id}")
        if len(message.command) != 2:
            return await message.reply("<b>ᴜsᴀɢᴇ: /ᴅᴇʟᴀᴅᴍɪɴ <user_id></b>")
        
        user_id = int(message.command[1])
        if user_id == Config.USER_ID:
            return await message.reply("<b>❌ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ</b>")
            
        await Seishiro.remove_admin(user_id)
        await message.reply(f"<b>✅ ᴜsᴇʀ {user_id} ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴀᴅᴍɪɴs</b>")
        ʟᴏɢɢᴇʀ.ɪɴꜰᴏ(f"User {user_id} removed from admins by {message.from_user.id}")
    except ValueError:
        await message.reply("<b>ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ</b>")
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        await message.reply(f"❌ ᴇʀʀᴏʀ: {str(e)}")

@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("ᴀᴅᴍɪɴs") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ ᴠɪᴇᴡ_ᴀᴅᴍɪɴs_ʜᴀɴᴅʟᴇʀ(ᴄʟɪᴇɴᴛ, ᴍᴇssᴀɢᴇ):
    ᴛʀʏ:
        ᴀᴅᴍɪɴs = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ᴀᴅᴍɪɴs()
        ᴛᴇxᴛ = "<b>👮‍♂️ ᴀᴅᴍɪɴ ʟɪsᴛ:</b>\ɴ\ɴ"
        ᴛᴇxᴛ += f"• {Config.USER_ID} (Owner)\n"
        for uid in admins:
            text += f"• `{uid}`\n"
        await message.reply(text)
    except Exception as e:
        logger.error(f"Error listing admins: {e}")
        await message.reply(f"❌ ᴇʀʀᴏʀ: {str(e)}")



@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("sᴇᴛ_ᴡᴀᴛᴇʀᴍᴀʀᴋ") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ sᴇᴛ_ᴡᴀᴛᴇʀᴍᴀʀᴋ_ᴍsɢ(ᴄʟɪᴇɴᴛ: ᴄʟɪᴇɴᴛ, ᴍᴇssᴀɢᴇ: ᴍᴇssᴀɢᴇ):
    ᴛʀʏ:
        
        ɪꜰ ʟᴇɴ(ᴍᴇssᴀɢᴇ.ᴄᴏᴍᴍᴀɴᴅ) < 2:
            await message.reply_text(
                "💧 **Set Watermark**\n\n"
                "**Usage:**\n"
                "`/set_watermark <text> <position> <color> <opacity> <fontsize>`\ɴ\ɴ"
                "**ᴇxᴀᴍᴘʟᴇ:**\ɴ"
                "`/sᴇᴛ_ᴡᴀᴛᴇʀᴍᴀʀᴋ {manga_name} ᴄʜ-{chapter} ᴄᴇɴᴛᴇʀ #ꜰꜰ0000 100 30`\ɴ\ɴ"
                "**ᴘᴀʀᴀᴍᴇᴛᴇʀs:**\ɴ"
                "• ᴘᴏsɪᴛɪᴏɴ: `ᴛᴏᴘ-ʟᴇꜰᴛ`, `ᴛᴏᴘ-ʀɪɢʜᴛ`, `ʙᴏᴛᴛᴏᴍ-ʟᴇꜰᴛ`, `ʙᴏᴛᴛᴏᴍ-ʀɪɢʜᴛ`, `ᴄᴇɴᴛᴇʀ` (ᴅᴇꜰᴀᴜʟᴛ: ʙᴏᴛᴛᴏᴍ-ʀɪɢʜᴛ)\ɴ"
                "• ᴄᴏʟᴏʀ: ʜᴇx ᴄᴏᴅᴇ ʟɪᴋᴇ `#ꜰꜰꜰꜰꜰꜰ` (ᴅᴇꜰᴀᴜʟᴛ: ᴡʜɪᴛᴇ)\ɴ"
                "• ᴏᴘᴀᴄɪᴛʏ: 0-255 (ᴅᴇꜰᴀᴜʟᴛ: 128)\ɴ"
                "• ꜰᴏɴᴛ sɪᴢᴇ: ɴᴜᴍʙᴇʀ (ᴅᴇꜰᴀᴜʟᴛ: 20)",
                ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ᴍᴀʀᴋᴅᴏᴡɴ
            )
            ʀᴇᴛᴜʀɴ
        
        ᴀʀɢs = ᴍᴇssᴀɢᴇ.ᴛᴇxᴛ.sᴘʟɪᴛ()
        ᴀʀɢs.ᴘᴏᴘ(0)

        ᴘᴏsɪᴛɪᴏɴ = "ʙᴏᴛᴛᴏᴍ-ʀɪɢʜᴛ"
        ᴄᴏʟᴏʀ = "#ꜰꜰꜰꜰꜰꜰ"
        ᴏᴘᴀᴄɪᴛʏ = 128
        ꜰᴏɴᴛ_sɪᴢᴇ = 20

        
        ᴠᴀʟɪᴅ_ᴘᴏsɪᴛɪᴏɴs = ["ᴛᴏᴘ-ʟᴇꜰᴛ", "ᴛᴏᴘ-ʀɪɢʜᴛ", "ʙᴏᴛᴛᴏᴍ-ʟᴇꜰᴛ", "ʙᴏᴛᴛᴏᴍ-ʀɪɢʜᴛ", "ᴄᴇɴᴛᴇʀ"]
        
        ɪꜰ ʟᴇɴ(ᴀʀɢs) > 1 ᴀɴᴅ ᴀʀɢs[-1].ɪsᴅɪɢɪᴛ():
            ᴠᴀʟ = ɪɴᴛ(ᴀʀɢs[-1])
            ɪꜰ 10 <= val <= 100:
                font_size = val
                args.pop()
        
        if len(args) > 1 ᴀɴᴅ ᴀʀɢs[-1].ɪsᴅɪɢɪᴛ():
            ᴠᴀʟ = ɪɴᴛ(ᴀʀɢs[-1])
            ɪꜰ 0 <= val <= 255:
                opacity = val
                args.pop()
        
        if len(args) > 1 ᴀɴᴅ ᴀʀɢs[-1].sᴛᴀʀᴛsᴡɪᴛʜ("#") ᴀɴᴅ ʟᴇɴ(ᴀʀɢs[-1]) == 7:
            ᴄᴏʟᴏʀ = ᴀʀɢs[-1]
            ᴀʀɢs.ᴘᴏᴘ()

        ɪꜰ ʟᴇɴ(ᴀʀɢs) > 1 ᴀɴᴅ ᴀʀɢs[-1] ɪɴ ᴠᴀʟɪᴅ_ᴘᴏsɪᴛɪᴏɴs:
            ᴘᴏsɪᴛɪᴏɴ = ᴀʀɢs[-1]
            ᴀʀɢs.ᴘᴏᴘ()

        ᴛᴇxᴛ = " ".ᴊᴏɪɴ(ᴀʀɢs)
        
        ɪꜰ ɴᴏᴛ ᴛᴇxᴛ:
             ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ_ᴛᴇxᴛ("❌ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴇxᴛ ɪs ᴍɪssɪɴɢ.")
             ʀᴇᴛᴜʀɴ
        
        sᴜᴄᴄᴇss = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.sᴇᴛ_ᴡᴀᴛᴇʀᴍᴀʀᴋ(ᴛᴇxᴛ, ᴘᴏsɪᴛɪᴏɴ, ᴄᴏʟᴏʀ, ᴏᴘᴀᴄɪᴛʏ, ꜰᴏɴᴛ_sɪᴢᴇ)
        
        ɪꜰ sᴜᴄᴄᴇss:
            ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ_ᴛᴇxᴛ(
                f"✅ Watermark set successfully!\n\n"
                f"**Text:** `{text}`\n"
                f"**Position:** `{position}`\n"
                f"**Color:** `{color}`\n"
                f"**Opacity:** `{opacity}/255` ({int((opacity/255)*100)}%)\n"
                f"**Font Size:** `{font_size}`\n\n"
                "💧 Watermark will be applied to all new chapter uploads.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logger.info(f"Watermark set by admin {message.from_user.id}: {text}")
        else:
            await message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ sᴀᴠᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ.")
            
    except ValueError as e:
        await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ꜰᴏʀᴍᴀᴛ ꜰᴏʀ ᴏᴘᴀᴄɪᴛʏ ᴏʀ ꜰᴏɴᴛ sɪᴢᴇ.")
    except Exception as e:
        logger.error(f"Error in set_watermark_msg: {e}", exc_info=True)
        await message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("ᴠɪᴇᴡ_ᴡᴀᴛᴇʀᴍᴀʀᴋ") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ ᴠɪᴇᴡ_ᴡᴀᴛᴇʀᴍᴀʀᴋ_ᴍsɢ(ᴄʟɪᴇɴᴛ: ᴄʟɪᴇɴᴛ, ᴍᴇssᴀɢᴇ: ᴍᴇssᴀɢᴇ):
    ᴛʀʏ:
        ʟᴏɢɢᴇʀ.ɪɴꜰᴏ(f"View watermark command from admin {message.from_user.id}")
        
        current_wm = await Seishiro.get_watermark()
        
        if current_wm:
            await message.reply_text(
                f"💧 **ᴄᴜʀʀᴇɴᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ:**\ɴ\ɴ"
                f"**Text:** `{current_wm['text']}`\n"
                f"**Position:** `{current_wm['position']}`\n"
                f"**Color:** `{current_wm['color']}`\n"
                f"**Opacity:** `{current_wm['opacity']}/255` ({int((current_wm['opacity']/255)*100)}%)\n"
                f"**Font Size:** `{current_wm['font_size']}`\n\n"
                "**Available Variables:**\n"
                "• `{manga_name}` - Manga name\n"
                "• `{chapter}` - Chapter number\n\n"
                "**Available Positions:**\n"
                "`top-left`, `top-right`, `bottom-left`, `bottom-right`, `center`\n\n"
                "Use /set_watermark to change or /rem_watermark to remove it.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                "❌ ɴᴏ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴄᴏɴꜰɪɢᴜʀᴇᴅ.\ɴ\ɴ"
                "Use /set_watermark to add a watermark to your chapter pages.\n\n"
                "**Example:**\n`/set_watermark @YourChannel bottom-right #FFFFFF 128 20`",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            
    except Exception as e:
        logger.error(f"Error viewing watermark: {e}", exc_info=True)
        await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ: {str(e)}")

@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("ʀᴇᴍ_ᴡᴀᴛᴇʀᴍᴀʀᴋ") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ ʀᴇᴍ_ᴡᴀᴛᴇʀᴍᴀʀᴋ_ᴍsɢ(ᴄʟɪᴇɴᴛ: ᴄʟɪᴇɴᴛ, ᴍᴇssᴀɢᴇ: ᴍᴇssᴀɢᴇ):
    ᴛʀʏ:
        ʟᴏɢɢᴇʀ.ɪɴꜰᴏ(f"Remove watermark command from admin {message.from_user.id}")
        
        current_wm = await Seishiro.get_watermark()
        
        if not current_wm:
            await message.reply_text("❌ ɴᴏ ᴡᴀᴛᴇʀᴍᴀʀᴋ ɪs ᴄᴏɴꜰɪɢᴜʀᴇᴅ.")
            return
        
        success = await Seishiro.delete_watermark()
        
        if success:
            await message.reply_text(
                "✅ ᴡᴀᴛᴇʀᴍᴀʀᴋ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!\ɴ\ɴ"
                "📖 Chapters will now be uploaded without watermark.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logger.info(f"Watermark removed by admin {message.from_user.id}")
        else:
            await message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.")
            
    except Exception as e:
        logger.error(f"Error removing watermark: {e}", exc_info=True)
        await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴡᴀᴛᴇʀᴍᴀʀᴋ: {str(e)}")


# ʀᴇxʙᴏᴛs
# ᴅᴏɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛ
# ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ @ʀᴇxʙᴏᴛs_ᴏꜰꜰɪᴄɪᴀʟ 
#sᴜᴘᴏᴏʀᴛ ɢʀᴏᴜᴘ @ʀᴇxʙᴏᴛsᴄʜᴀᴛ


@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("ʙʀᴏᴀᴅᴄᴀsᴛ") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ ʙʀᴏᴀᴅᴄᴀsᴛ_ʜᴀɴᴅʟᴇʀ(ᴄʟɪᴇɴᴛ: ᴄʟɪᴇɴᴛ, ᴍ: ᴍᴇssᴀɢᴇ):
    ᴛʀʏ:
        ɪꜰ ɴᴏᴛ ᴍ.ʀᴇᴘʟʏ_ᴛᴏ_ᴍᴇssᴀɢᴇ ᴀɴᴅ ʟᴇɴ(ᴍ.ᴄᴏᴍᴍᴀɴᴅ) < 2:
            return await m.reply("Reply to a message OR provide text to broadcast it.\nUsage: `/broadcast <message>`")
            
        ᴀʟʟ_ᴜsᴇʀs = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ᴀʟʟ_ᴜsᴇʀs()
        ᴛᴏᴛᴀʟ = ʟᴇɴ(ᴀʟʟ_ᴜsᴇʀs)
        sᴜᴄᴄᴇssꜰᴜʟ = 0
        ᴜɴsᴜᴄᴄᴇssꜰᴜʟ = 0
        
        sᴛᴀᴛᴜs = ᴀᴡᴀɪᴛ ᴍ.ʀᴇᴘʟʏ(f"🚀 Broadcasting to {total} users...")
        
        for user_id in all_users:
            try:
                if m.reply_to_message:
                    await m.reply_to_message.copy(chat_id=user_id)
                else:
                    text = m.text.split(None, 1)[1]
                    await client.send_message(user_id, text)
                successful += 1
            except Exception as e:
                unsuccessful += 1
            
            if (successful + unsuccessful) % 20 == 0:
                await status.edit(f"🚀 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ... {successful}/{total} sᴇɴᴛ.")
                
        ᴀᴡᴀɪᴛ sᴛᴀᴛᴜs.ᴇᴅɪᴛ(
            f"✅ **Broadcast Complete**\n\n"
            f"👥 Total: {total}\n"
            f"✅ Sent: {successful}\n"
            f"❌ Failed: {unsuccessful}"
        )
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        await m.reply(f"❌ ᴇʀʀᴏʀ: {str(e)}")


@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("ꜰsᴜʙ_ᴍᴏᴅᴇ") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ ꜰsᴜʙ_ᴍᴏᴅᴇ(ᴄʟɪᴇɴᴛ: ᴄʟɪᴇɴᴛ, ᴍᴇssᴀɢᴇ: ᴍᴇssᴀɢᴇ):
    ᴄʜᴀɴɴᴇʟs = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.sʜᴏᴡ_ᴄʜᴀɴɴᴇʟs()
    ʙᴜᴛᴛᴏɴs = []
    ꜰᴏʀ ᴄɪᴅ ɪɴ ᴄʜᴀɴɴᴇʟs:
        ᴛʀʏ:
            ᴄʜᴀᴛ = ᴀᴡᴀɪᴛ ᴄʟɪᴇɴᴛ.ɢᴇᴛ_ᴄʜᴀᴛ(ᴄɪᴅ)
            ᴍᴏᴅᴇ = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ᴄʜᴀɴɴᴇʟ_ᴍᴏᴅᴇ(ᴄɪᴅ)
            sᴛᴀᴛᴜs = "🟢" ɪꜰ ᴍᴏᴅᴇ == "ᴏɴ" ᴇʟsᴇ "🔴"
            ʙᴜᴛᴛᴏɴs.ᴀᴘᴘᴇɴᴅ([ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅʙᴜᴛᴛᴏɴ(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
        except Exception:
            continue
    
    if not buttons:
        buttons.append([InlineKeyboardButton("ɴᴏ ᴄʜᴀɴɴᴇʟs ꜰᴏᴜɴᴅ", callback_data="no_channels")])
        
    await message.reply_text(
        "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ꜰᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
        reply_markup=InlineKeyboardMarkup(buttons + [
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
        ])
    )

@Client.on_message(filters.command("add_fsub_chnl") & filters.private & admin)
async def add_fsub(client: Client, message: Message):
    try:
        if len(message.command) != 2:
            return await message.reply("ᴜsᴀɢᴇ: /ᴀᴅᴅ_ꜰsᴜʙ_ᴄʜɴʟ <channel_id>")
        
        cid = int(message.command[1])
        try:
            chat = await client.get_chat(cid)
        except:
            return await message.reply("❌ ʙᴏᴛ ᴄᴀɴɴᴏᴛ ᴀᴄᴄᴇss ᴛʜɪs ᴄʜᴀɴɴᴇʟ ᴏʀ ɪɴᴠᴀʟɪᴅ ɪᴅ")
            
        await Seishiro.add_fsub_channel(cid)
        await message.reply(f"✅ ᴀᴅᴅᴇᴅ {chat.title} ᴛᴏ ꜰᴏʀᴄᴇ-sᴜʙ ʟɪsᴛ")
    ᴇxᴄᴇᴘᴛ ᴇxᴄᴇᴘᴛɪᴏɴ ᴀs ᴇ:
        ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ(f"❌ Error: {e}")

@Client.on_message(filters.command("rem_fsub_chnl") & filters.private & admin)
async def rem_fsub(client: Client, message: Message):
    try:
        if len(message.command) != 2:
            return await message.reply("ᴜsᴀɢᴇ: /ʀᴇᴍ_ꜰsᴜʙ_ᴄʜɴʟ <channel_id>")
            
        cid = int(message.command[1])
        await Seishiro.remove_fsub_channel(cid)
        await message.reply("✅ ʀᴇᴍᴏᴠᴇᴅ ᴄʜᴀɴɴᴇʟ ꜰʀᴏᴍ ꜰᴏʀᴄᴇ-sᴜʙ ʟɪsᴛ")
    except Exception as e:
        await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")

@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴍᴇssᴀɢᴇ(ꜰɪʟᴛᴇʀs.ᴄᴏᴍᴍᴀɴᴅ("ꜰsᴜʙ_ᴄʜɴʟs") & ꜰɪʟᴛᴇʀs.ᴘʀɪᴠᴀᴛᴇ & ᴀᴅᴍɪɴ)
ᴀsʏɴᴄ ᴅᴇꜰ ᴠɪᴇᴡ_ꜰsᴜʙ(ᴄʟɪᴇɴᴛ: ᴄʟɪᴇɴᴛ, ᴍᴇssᴀɢᴇ: ᴍᴇssᴀɢᴇ):
    ᴄʜᴀɴɴᴇʟs = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ꜰsᴜʙ_ᴄʜᴀɴɴᴇʟs()
    ɪꜰ ɴᴏᴛ ᴄʜᴀɴɴᴇʟs:
        ʀᴇᴛᴜʀɴ ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ("ɴᴏ ꜰᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs sᴇᴛ")
        
    ᴛᴇxᴛ = "<b>📢 ꜰᴏʀᴄᴇ-sᴜʙ ᴄʜᴀɴɴᴇʟs:</b>\ɴ"
    ꜰᴏʀ ᴄɪᴅ ɪɴ ᴄʜᴀɴɴᴇʟs:
        ᴛʀʏ:
            ᴄʜᴀᴛ = ᴀᴡᴀɪᴛ ᴄʟɪᴇɴᴛ.ɢᴇᴛ_ᴄʜᴀᴛ(ᴄɪᴅ)
            ᴛᴇxᴛ += f"• {chat.title} (`{cid}`)\n"
        except:
            text += f"• `{cid}` (Inaccessible)\n"
            
    await message.reply(text)

@Client.on_callback_query(filters.regex(r"^(rfs_|fsub_back)"))
async def fsub_settings_callback(client: Client, callback_query):
    user_id = callback_query.from_user.id
    cb_data = callback_query.data

    if cb_data.startswith("rfs_ch_"):
        cid = int(cb_data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await Seishiro.get_channel_mode(cid)
            status = "ON" if mode == "on" else "OFF"
            new_mode = "off" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ForceSub Mode {'OFF' if mode == 'on' else 'ON'}",
                                      callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await callback_query.message.edit_text(
                f"ᴄʜᴀɴɴᴇʟ: {chat.title}\ɴᴄᴜʀʀᴇɴᴛ ꜰᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ: {status}",
                ʀᴇᴘʟʏ_ᴍᴀʀᴋᴜᴘ=ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅᴍᴀʀᴋᴜᴘ(ʙᴜᴛᴛᴏɴs)
            )
        ᴇxᴄᴇᴘᴛ ᴇxᴄᴇᴘᴛɪᴏɴ:
            ᴀᴡᴀɪᴛ ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴀɴsᴡᴇʀ("ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ᴄʜᴀɴɴᴇʟ ɪɴꜰᴏ", sʜᴏᴡ_ᴀʟᴇʀᴛ=ᴛʀᴜᴇ)

    ᴇʟɪꜰ ᴄʙ_ᴅᴀᴛᴀ.sᴛᴀʀᴛsᴡɪᴛʜ("ʀꜰs_ᴛᴏɢɢʟᴇ_"):
        ᴘᴀʀᴛs = ᴄʙ_ᴅᴀᴛᴀ.sᴘʟɪᴛ("_")[2:]
        ᴄɪᴅ = ɪɴᴛ(ᴘᴀʀᴛs[0])
        ᴀᴄᴛɪᴏɴ = ᴘᴀʀᴛs[1]
        ᴍᴏᴅᴇ = "ᴏɴ" ɪꜰ ᴀᴄᴛɪᴏɴ == "ᴏɴ" ᴇʟsᴇ "ᴏꜰf"

        await Seishiro.set_channel_mode(cid, mode)
        await callback_query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        chat = await client.get_chat(cid)
        status = "ON" if mode == "on" else "OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ForceSub Mode {'OFF' if mode == 'on' else 'ON'}",
                                  callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await callback_query.message.edit_text(
            f"ᴄʜᴀɴɴᴇʟ: {chat.title}\ɴᴄᴜʀʀᴇɴᴛ ꜰᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ: {status}",
            ʀᴇᴘʟʏ_ᴍᴀʀᴋᴜᴘ=ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅᴍᴀʀᴋᴜᴘ(ʙᴜᴛᴛᴏɴs)
        )

    ᴇʟɪꜰ ᴄʙ_ᴅᴀᴛᴀ == "ꜰsᴜʙ_ʙᴀᴄᴋ":
        ᴄʜᴀɴɴᴇʟs = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.sʜᴏᴡ_ᴄʜᴀɴɴᴇʟs()
        ʙᴜᴛᴛᴏɴs = []
        ꜰᴏʀ ᴄɪᴅ ɪɴ ᴄʜᴀɴɴᴇʟs:
            ᴛʀʏ:
                ᴄʜᴀᴛ = ᴀᴡᴀɪᴛ ᴄʟɪᴇɴᴛ.ɢᴇᴛ_ᴄʜᴀᴛ(ᴄɪᴅ)
                ᴍᴏᴅᴇ = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ᴄʜᴀɴɴᴇʟ_ᴍᴏᴅᴇ(ᴄɪᴅ)
                sᴛᴀᴛᴜs = "🟢" ɪꜰ ᴍᴏᴅᴇ == "ᴏɴ" ᴇʟsᴇ "🔴"
                ʙᴜᴛᴛᴏɴs.ᴀᴘᴘᴇɴᴅ([ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅʙᴜᴛᴛᴏɴ(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except Exception:
                continue

        if not buttons:
            buttons.append([InlineKeyboardButton("ɴᴏ ᴄʜᴀɴɴᴇʟs ꜰᴏᴜɴᴅ", callback_data="no_channels")])

        await callback_query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ꜰᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons + [
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )



# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat