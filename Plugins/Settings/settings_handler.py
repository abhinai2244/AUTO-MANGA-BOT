# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


from pyrogram import Client, filters, enums
from Database.database import Seishiro
from Plugins.helper import user_states, get_styled_text
from config import Config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_callback_query(filters.regex("^cancel_input$"))
async def cancel_input_cb(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    await callback_query.message.edit_text(
        get_styled_text("❌ Input Cancelled."),
        parse_mode=enums.ParseMode.HTML
    )
    buttons = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ sᴇᴛᴛɪɴɢs", callback_data="settings_menu")]]
    await callback_query.message.reply_text("ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & ~filters.command(["start", "help", "admin"]))
async def settings_input_listener(client, message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return

    state_info = user_states[user_id]
    state = state_info.get("state")
    
    try:
        if state == "waiting_caption":
            await Seishiro.set_caption(message.text)
            await message.reply(get_styled_text("✅ Caption Updated Successfully!"), parse_mode=enums.ParseMode.HTML)
            
            from Plugins.Settings.media_settings import set_caption_cb
            curr = await Seishiro.get_caption()
            curr_disp = "Set" if curr else "None"
            text = get_styled_text(
                "<b>Caption</b>\n\n"
                "<b>Format:</b>\n"
                "➥ {manga_title}: Manga Name\n"
                "➥ {chapter_num}: Chapter Number\n"
                "➥ {file_name}: File Name\n\n"
                f"➥ Your Value: {curr_disp}"
            )
            buttons = [
                [
                    InlineKeyboardButton("sᴇᴛ / ᴄʜᴀɴɢᴇ", callback_data="set_caption_input"),
                    InlineKeyboardButton("ᴅᴇʟᴇᴛᴇ", callback_data="del_caption_btn")
                ],
                [
                    InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="settings_menu"),
                    InlineKeyboardButton("❄ ᴄʟᴏsᴇ ❄", callback_data="stats_close")
                ]
            ]
            await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

        elif state == "waiting_format":
            await Seishiro.set_format(message.text)
            await message.reply(get_styled_text("✅ File Name Format Updated!"), parse_mode=enums.ParseMode.HTML)

        elif state.startswith("waiting_banner_"):
            num = state.split("_")[-1]
            if message.photo:
                await Seishiro.set_config(f"banner_image_{num}", message.photo.file_id)
                
                from Plugins.Settings.media_settings import get_banner_menu
                text, markup = await get_banner_menu(client)
                await message.reply(text, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
            else:
                await message.reply("❌ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ.")
                return

        elif state == "waiting_channel":
            try:
                cid = int(message.text)
                await Seishiro.set_default_channel(cid)
                await message.reply(get_styled_text(f"✅ Upload Channel Set: {cid}"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ. sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ ʟɪᴋᴇ -100...")
                return

        elif state == "waiting_dump_channel":
            try:
                cid = int(message.text)
                await Seishiro.set_config("dump_channel", cid)
                await message.reply(get_styled_text(f"✅ Dump Channel Set: {cid}"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ.")
                return

        elif state == "waiting_auc_id":
            try:
                cid = int(message.text)
                try:
                    chat = await client.get_chat(cid)
                    title = chat.title
                except Exception as e:
                    await message.reply(f"❌ <b>ᴇʀʀᴏʀ:</b> ʙᴏᴛ ᴄᴀɴɴᴏᴛ ᴀᴄᴄᴇss ᴄʜᴀɴɴᴇʟ ᴏʀ ɪɴᴠᴀʟɪᴅ ɪᴅ.\ɴ`{e}`", ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ)
                    ʀᴇᴛᴜʀɴ
                
                ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ᴀᴅᴅ_ᴀᴜᴛᴏ_ᴜᴘᴅᴀᴛᴇ_ᴄʜᴀɴɴᴇʟ(ᴄɪᴅ, ᴛɪᴛʟᴇ)
                
                
                ᴄᴜʀʀ_ʟɪsᴛ = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ᴀᴜᴛᴏ_ᴜᴘᴅᴀᴛᴇ_ᴄʜᴀɴɴᴇʟs()
                ʟɪsᴛ_ᴛᴇxᴛ = "\ɴ".ᴊᴏɪɴ([f"• {c.get('title', 'Unknown')} (`{c.get('_id')}`)" for c in curr_list])
                
                text = get_styled_text(
                    f"✅ Added Auto Update Channel:\n{title} ({cid})\n\n"
                    f"<b>Current List:</b>\n{list_text}"
                )
                
                buttons = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ʟɪsᴛ", callback_data="header_auto_update_channels")]]
                await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ ꜰᴏʀᴍᴀᴛ.")
                return
        
        elif state == "waiting_password":
            if message.text.upper() == "OFF":
                await Seishiro.set_config("pdf_password", None)
                await message.reply(get_styled_text("✅ Password Protection Disabled."), parse_mode=enums.ParseMode.HTML)
            else:
                await Seishiro.set_config("pdf_password", message.text)
                await message.reply(get_styled_text(f"✅ Password Set: {message.text}"), parse_mode=enums.ParseMode.HTML)

        elif state == "waiting_merge_size":
            try:
                size = int(message.text)
                await Seishiro.set_config("merge_size_limit", size)
                await message.reply(get_styled_text(f"✅ Merge Size Limit: {size}MB"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ.")
                return

        elif state == "waiting_regex":
            await Seishiro.set_config("filename_regex", message.text)
            await message.reply(get_styled_text("✅ Regex Pattern Saved."), parse_mode=enums.ParseMode.HTML)

        elif state == "waiting_update_text":
            await Seishiro.set_config("update_text", message.text)
            await message.reply(get_styled_text("✅ Update Text Saved."), parse_mode=enums.ParseMode.HTML)
            
        elif state == "waiting_interval":
            try:
                val = int(message.text)
                if await Seishiro.set_check_interval(val):
                    await message.reply(get_styled_text(f"✅ Check Interval Set: {val}s"), parse_mode=enums.ParseMode.HTML)
                else:
                    await message.reply("❌ ᴠᴀʟᴜᴇ ᴏᴜᴛ ᴏꜰ ʀᴀɴɢᴇ (60-3600).")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")

        elif state == "waiting_fsub_id":
            try:
                cid = int(message.text)
                try:
                    await client.get_chat(cid) # Verify access
                except:
                    await message.reply("❌ ʙᴏᴛ ᴄᴀɴɴᴏᴛ ᴀᴄᴄᴇss ᴛʜɪs ᴄʜᴀɴɴᴇʟ. ᴀᴅᴅ ʙᴏᴛ ᴀs ᴀᴅᴍɪɴ ꜰɪʀsᴛ!")
                    return
                
                await Seishiro.add_fsub_channel(cid)
                await message.reply(get_styled_text(f"✅ FSub Channel Added: {cid}"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ.")

        elif state == "waiting_fsub_rem_id":
            try:
                cid = int(message.text)
                if await Seishiro.remove_fsub_channel(cid):
                     await message.reply(get_styled_text(f"✅ FSub Channel Removed: {cid}"), parse_mode=enums.ParseMode.HTML)
                else:
                     await message.reply("❌ ᴄʜᴀɴɴᴇʟ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ꜰsᴜʙ ʟɪsᴛ.")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ.")

        elif state == "waiting_wm_text":
            wm = await Seishiro.get_watermark() or {}
            await Seishiro.set_watermark(
                text=message.text,
                position=wm.get("position", "bottom-right"),
                color=wm.get("color", "#FFFFFF"),
                opacity=wm.get("opacity", 128),
                font_size=wm.get("font_size", 20)
            )
            await message.reply(get_styled_text("✅ Watermark Text Updated!"), parse_mode=enums.ParseMode.HTML)

        elif state == "waiting_wm_color":
            color = message.text
            if not color.startswith("#") or len(color) not in [4, 7]:
                 await message.reply("❌ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ. ᴜsᴇ #ʀʀɢɢʙʙ (ᴇ.ɢ. #ꜰꜰ0000).")
                 return
            
            wm = await Seishiro.get_watermark() or {}
            await Seishiro.set_watermark(
                text=wm.get("text", "Default"),
                position=wm.get("position", "bottom-right"),
                color=color,
                opacity=wm.get("opacity", 128),
                font_size=wm.get("font_size", 20)
            )
            await message.reply(get_styled_text(f"✅ Color Set: {color}"), parse_mode=enums.ParseMode.HTML)

        elif state == "waiting_wm_opacity":
            try:
                op = int(message.text)
                if not (0 <= op <= 255): raise ValueError
                
                wm = await Seishiro.get_watermark() or {}
                await Seishiro.set_watermark(
                    text=wm.get("text", "Default"),
                    position=wm.get("position", "bottom-right"),
                    color=wm.get("color", "#FFFFFF"),
                    opacity=op,
                    font_size=wm.get("font_size", 20)
                )
                await message.reply(get_styled_text(f"✅ Opacity Set: {op}"), parse_mode=enums.ParseMode.HTML)
            except:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ (0-255).")

        elif state == "waiting_deltimer":
            try:
                val = int(message.text)
                await Seishiro.set_del_timer(val)
                await message.reply(get_styled_text(f"✅ Delete Timer Set: {val}s"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")

        elif state == "waiting_thumb":
            if message.photo:
                file_id = message.photo.file_id
                await Seishiro.set_config("custom_thumbnail", file_id)
                await message.reply(get_styled_text("✅ Custom Thumbnail Set!"), parse_mode=enums.ParseMode.HTML)
            else:
                await message.reply("❌ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ.")
                return

        elif state in ["waiting_channel_stickers", "waiting_update_sticker"]:
            val = None
            if message.sticker:
                val = message.sticker.file_id
            elif message.text:
                txt = message.text.strip()
                if len(txt) > 10: 
                    val = txt
            
            if not val:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ sᴛɪᴄᴋᴇʀ ᴏʀ ᴀ ᴠᴀʟɪᴅ ꜰɪʟᴇ ɪᴅ sᴛʀɪɴɢ.")
                return

            key = state.replace("waiting_", "")
            await Seishiro.set_config(key, val)
            await message.reply(get_styled_text(f"✅ {key.replace('_', ' ').title()} Saved.\nID: `{val}`"), parse_mode=enums.ParseMode.HTML)

        elif state == "waiting_add_admin":
            try:
                new_admin_id = int(message.text)
                await Seishiro.add_admin(new_admin_id)
                await message.reply(get_styled_text(f"✅ User {new_admin_id} added as Admin."), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
            except Exception as e:
                await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")

        ᴇʟɪꜰ sᴛᴀᴛᴇ == "ᴡᴀɪᴛɪɴɢ_ᴅᴇʟ_ᴀᴅᴍɪɴ":
            ᴛʀʏ:
                ᴅᴇʟ_ɪᴅ = ɪɴᴛ(ᴍᴇssᴀɢᴇ.ᴛᴇxᴛ)
                ɪꜰ ᴅᴇʟ_ɪᴅ == ᴄᴏɴꜰɪɢ.ᴜsᴇʀ_ɪᴅ:
                    ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ("❌ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ.")
                ᴇʟsᴇ:
                    ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ʀᴇᴍᴏᴠᴇ_ᴀᴅᴍɪɴ(ᴅᴇʟ_ɪᴅ)
                    ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ(ɢᴇᴛ_sᴛʏʟᴇᴅ_ᴛᴇxᴛ(f"✅ User {del_id} removed from Admins."), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")
            except Exception as e:
                await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")

        ᴇʟɪꜰ sᴛᴀᴛᴇ == "ᴡᴀɪᴛɪɴɢ_ʙʀᴏᴀᴅᴄᴀsᴛ_ᴍsɢ":
             ᴛʀʏ:
                sᴛᴀᴛᴜs_ᴍsɢ = ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ("🚀 ᴘʀᴇᴘᴀʀɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ...")
                ᴀʟʟ_ᴜsᴇʀs = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ᴀʟʟ_ᴜsᴇʀs()
                ᴛᴏᴛᴀʟ = ʟᴇɴ(ᴀʟʟ_ᴜsᴇʀs)
                sᴜᴄᴄᴇssꜰᴜʟ = 0
                ᴜɴsᴜᴄᴄᴇssꜰᴜʟ = 0
                
                ꜰᴏʀ ᴜsᴇʀ_ɪᴅ ɪɴ ᴀʟʟ_ᴜsᴇʀs:
                    ᴛʀʏ:
                        ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ᴄᴏᴘʏ(ᴄʜᴀᴛ_ɪᴅ=ᴜsᴇʀ_ɪᴅ)
                        sᴜᴄᴄᴇssꜰᴜʟ += 1
                    ᴇxᴄᴇᴘᴛ ᴇxᴄᴇᴘᴛɪᴏɴ:
                        ᴜɴsᴜᴄᴄᴇssꜰᴜʟ += 1
                        
                    ɪꜰ (sᴜᴄᴄᴇssꜰᴜʟ + ᴜɴsᴜᴄᴄᴇssꜰᴜʟ) % 20 == 0:
                        ᴛʀʏ:
                            ᴀᴡᴀɪᴛ sᴛᴀᴛᴜs_ᴍsɢ.ᴇᴅɪᴛ(f"🚀 Broadcasting... {successful}/{total} sent.")
                        except:
                            pass
                
                await status_msg.edit(
                    f"✅ **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ**\ɴ\ɴ"
                    f"👥 Total: {total}\n"
                    f"✅ Sent: {successful}\n"
                    f"❌ Failed: {unsuccessful}"
                )
             except Exception as e:
                await message.reply(f"❌ ʙʀᴏᴀᴅᴄᴀsᴛ ᴇʀʀᴏʀ: {e}")

        ᴇʟɪꜰ sᴛᴀᴛᴇ == "ᴡᴀɪᴛɪɴɢ_ʙᴀɴ_ɪᴅ":
            ᴛʀʏ:
                ᴛᴀʀɢᴇᴛ_ɪᴅ = ɪɴᴛ(ᴍᴇssᴀɢᴇ.ᴛᴇxᴛ)
                ɪꜰ ᴛᴀʀɢᴇᴛ_ɪᴅ == ᴄᴏɴꜰɪɢ.ᴜsᴇʀ_ɪᴅ ᴏʀ ᴛᴀʀɢᴇᴛ_ɪᴅ == ᴍᴇssᴀɢᴇ.ꜰʀᴏᴍ_ᴜsᴇʀ.ɪᴅ:
                     ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ("❌ ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴏᴡɴᴇʀ ᴏʀ sᴇʟꜰ.")
                ᴇʟsᴇ:
                    ɪꜰ ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ʙᴀɴ_ᴜsᴇʀ(ᴛᴀʀɢᴇᴛ_ɪᴅ):
                        ᴀᴡᴀɪᴛ ᴍᴇssᴀɢᴇ.ʀᴇᴘʟʏ(ɢᴇᴛ_sᴛʏʟᴇᴅ_ᴛᴇxᴛ(f"🚫 User {target_id} has been BANNED."), parse_mode=enums.ParseMode.HTML)
                    else:
                        await message.reply("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ʙᴀɴ ᴜsᴇʀ.")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")

        elif state == "waiting_unban_id":
            try:
                target_id = int(message.text)
                if await Seishiro.unban_user(target_id):
                    await message.reply(get_styled_text(f"✅ User {target_id} has been UNBANNED."), parse_mode=enums.ParseMode.HTML)
                else:
                    await message.reply("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜɴʙᴀɴ ᴜsᴇʀ.")
            except ValueError:
                await message.reply("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")


    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    finally:
        if user_id in user_states:
            del user_states[user_id]


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat