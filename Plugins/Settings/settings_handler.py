# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
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
    buttons = [[InlineKeyboardButton("🔙 back to settings", callback_data="settings_menu")]]
    await callback_query.message.reply_text("cancelled.", reply_markup=InlineKeyboardMarkup(buttons))


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
                    InlineKeyboardButton("set / change", callback_data="set_caption_input"),
                    InlineKeyboardButton("delete", callback_data="del_caption_btn")
                ],
                [
                    InlineKeyboardButton("⬅ back", callback_data="settings_menu"),
                    InlineKeyboardButton("❄ close ❄", callback_data="stats_close")
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
                text, markup = await get_banner_menu(Client)
                await message.reply(text, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
            else:
                await message.reply("❌ please send a photo.")
                return

        elif state == "waiting_channel":
            try:
                cid = int(message.text)
                await Seishiro.set_default_channel(cid)
                await message.reply(get_styled_text(f"✅ Upload Channel Set: {cid}"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ invalid channel id. send a number like -100...")
                return

        elif state == "waiting_dump_channel":
            try:
                cid = int(message.text)
                await Seishiro.set_config("dump_channel", cid)
                await message.reply(get_styled_text(f"✅ Dump Channel Set: {cid}"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ invalid id.")
                return

        elif state == "waiting_auc_id":
            try:
                cid = int(message.text)
                try:
                    chat = await client.get_chat(cid)
                    title = chat.title
                except Exception as e:
                    await message.reply(f"❌ <b>error:</b> bot cannot access channel or invalid id.\n`{e}`", parse_mode=enums.ParseMode.HTML)
                    return
                
                # Check if already exists
                curr_list = await Seishiro.get_auto_update_channels()
                if any(c.get('_id') == cid for c in curr_list):
                     await message.reply("❌ Channel already in auto update list.")
                     return

                if await Seishiro.add_auto_update_channel(cid, title):
                    pass
                else:
                    await message.reply("❌ Failed to add channel to DB.")
                    return
                
                
                curr_list = await Seishiro.get_auto_update_channels()
                list_text = "\n".join([f"• {c.get('title', 'Unknown')} (`{c.get('_id')}`)" for c in curr_list])
                
                text = get_styled_text(
                    f"✅ Added Auto Update Channel:\n{title} ({cid})\n\n"
                    f"<b>Current List:</b>\n{list_text}"
                )
                
                buttons = [[InlineKeyboardButton("🔙 back to list", callback_data="header_auto_update_channels")]]
                await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

            except ValueError:
                await message.reply("❌ invalid id format.")
                return

        elif state == "waiting_auc_rem_id":
            try:
                cid = int(message.text)
                if await Seishiro.remove_auto_update_channel(cid):
                     
                     curr_list = await Seishiro.get_auto_update_channels()
                     list_text = "\n".join([f"• {c.get('title', 'Unknown')} (`{c.get('_id')}`)" for c in curr_list])
                     if not list_text: list_text = "None"

                     text = get_styled_text(
                        f"✅ Removed Auto Update Channel: {cid}\n\n"
                        f"<b>Current List:</b>\n{list_text}"
                     )
                     buttons = [[InlineKeyboardButton("🔙 back to list", callback_data="header_auto_update_channels")]]
                     await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
                else:
                     await message.reply("❌ Channel ID not found in list.")
            except ValueError:
                await message.reply("❌ invalid id format.")
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
                await message.reply("❌ send a number.")
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
                if not (60 <= val <= 3600):
                    await message.reply("❌ value out of range (60-3600).")
                    return

                if await Seishiro.set_check_interval(val):
                    await message.reply(get_styled_text(f"✅ Check Interval Set: {val}s"), parse_mode=enums.ParseMode.HTML)
                else:
                    await message.reply("❌ error setting interval.")
            except ValueError:
                await message.reply("❌ invalid number.")

        elif state == "waiting_fsub_id":
            try:
                cid = int(message.text)
                try:
                    await client.get_chat(cid) # Verify access
                except:
                    await message.reply("❌ bot cannot access this channel. add bot as admin first!")
                    return
                
                await Seishiro.add_fsub_channel(cid)
                await message.reply(get_styled_text(f"✅ FSub Channel Added: {cid}"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ invalid id.")

        elif state == "waiting_fsub_rem_id":
            try:
                cid = int(message.text)
                if await Seishiro.remove_fsub_channel(cid):
                     await message.reply(get_styled_text(f"✅ FSub Channel Removed: {cid}"), parse_mode=enums.ParseMode.HTML)
                else:
                     await message.reply("❌ channel not found in fsub list.")
            except ValueError:
                await message.reply("❌ invalid id.")

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
                 await message.reply("❌ invalid format. use #rrggbb (e.g. #ff0000).")
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
                await message.reply("❌ invalid number (0-255).")

        elif state == "waiting_deltimer":
            try:
                val = int(message.text)
                await Seishiro.set_del_timer(val)
                await message.reply(get_styled_text(f"✅ Delete Timer Set: {val}s"), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ invalid number.")

        elif state == "waiting_thumb":
            if message.photo:
                file_id = message.photo.file_id
                await Seishiro.set_config("custom_thumbnail", file_id)
                await message.reply(get_styled_text("✅ Custom Thumbnail Set!"), parse_mode=enums.ParseMode.HTML)
            else:
                await message.reply("❌ please send a photo.")
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
                await message.reply("❌ invalid input. please send a sticker or a valid file id string.")
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
                await message.reply("❌ invalid user id.")
            except Exception as e:
                await message.reply(f"❌ error: {e}")

        elif state == "waiting_del_admin":
            try:
                del_id = int(message.text)
                if del_id == Config.USER_ID:
                    await message.reply("❌ cannot remove owner.")
                else:
                    await Seishiro.remove_admin(del_id)
                    await message.reply(get_styled_text(f"✅ User {del_id} removed from Admins."), parse_mode=enums.ParseMode.HTML)
            except ValueError:
                await message.reply("❌ invalid user id.")
            except Exception as e:
                await message.reply(f"❌ error: {e}")

        elif state == "waiting_broadcast_msg":
             try:
                status_msg = await message.reply("🚀 preparing broadcast...")
                all_users = await Seishiro.get_all_users()
                total = len(all_users)
                successful = 0
                unsuccessful = 0
                
                for user_id in all_users:
                    try:
                        await message.copy(chat_id=user_id)
                        successful += 1
                    except Exception:
                        unsuccessful += 1
                        
                    if (successful + unsuccessful) % 20 == 0:
                        try:
                            await status_msg.edit(f"🚀 Broadcasting... {successful}/{total} sent.")
                        except:
                            pass
                
                await status_msg.edit(
                    f"✅ **broadcast complete**\n\n"
                    f"👥 Total: {total}\n"
                    f"✅ Sent: {successful}\n"
                    f"❌ Failed: {unsuccessful}"
                )
             except Exception as e:
                await message.reply(f"❌ broadcast error: {e}")

        elif state == "waiting_ban_id":
            try:
                target_id = int(message.text)
                if target_id == Config.USER_ID or target_id == message.from_user.id:
                     await message.reply("❌ cannot ban owner or self.")
                else:
                    if await Seishiro.ban_user(target_id):
                        await message.reply(get_styled_text(f"🚫 User {target_id} has been BANNED."), parse_mode=enums.ParseMode.HTML)
                    else:
                        await message.reply("❌ failed to ban user.")
            except ValueError:
                await message.reply("❌ invalid user id.")

        elif state == "waiting_unban_id":
            try:
                target_id = int(message.text)
                if await Seishiro.unban_user(target_id):
                    await message.reply(get_styled_text(f"✅ User {target_id} has been UNBANNED."), parse_mode=enums.ParseMode.HTML)
                else:
                    await message.reply("❌ failed to unban user.")
            except ValueError:
                await message.reply("❌ invalid user id.")


    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    finally:
        if user_id in user_states:
            del user_states[user_id]


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat