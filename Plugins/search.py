# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from Plugins.downloading import Downloader
from Plugins.Sites.mangadex import MangaDexAPI
from Plugins.Sites.mangaforest import MangaForestAPI
from Database.database import Seishiro
from Plugins.helper import edit_msg_with_pic, get_styled_text, user_states, user_data, WAITING_CHAPTER_INPUT
import logging
import asyncio
import shutil
from pathlib import Path
import os
import re

logger = logging.getLogger(__name__)

from Plugins.Sites.mangakakalot import MangakakalotAPI
from Plugins.Sites.allmanga import AllMangaAPI

SITES = {
    "MangaDex": MangaDexAPI,
    "MangaForest": MangaForestAPI,
    "Mangakakalot": MangakakalotAPI,
    "AllManga": AllMangaAPI,
    "WebCentral": None # Placeholder until verified or imported
}

try:
    from Plugins.Sites.webcentral import WebCentralAPI
    SITES["WebCentral"] = WebCentralAPI
except ImportError:
    pass

def get_api_class(source):
    return SITES.get(source)


@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "settings", "search"]))
async def message_handler(client, message):
    user_id = message.from_user.id
    
    if user_id in user_states:
        if user_states[user_id] == WAITING_CHAPTER_INPUT:
            await custom_dl_input_handler(client, message)
            return
        return

@Client.on_message(filters.command("search") & filters.private)
async def search_command_handler(client, message):
    """Handle /search command for manga queries"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❌ ᴜsᴀɢᴇ: /sᴇᴀʀᴄʜ <query>")
        return
    
    query = parts[1].strip()
    if len(query) < 2:
        await message.reply("❌ ǫᴜᴇʀʏ ᴛᴏᴏ sʜᴏʀᴛ.")
        return
    
    buttons = []
    row = []
    for source in SITES.keys():
        if SITES[source] is not None:
            row.append(InlineKeyboardButton(source, callback_data=f"search_src_{source}_{query[:30]}"))
            if len(row) == 2:  # 2 buttons per row
                buttons.append(row)
                row = []
    
    if row:
        buttons.append(row)
    
    if not buttons:
        await message.reply("❌ ɴᴏ sᴏᴜʀᴄᴇs ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return
        
    buttons.append([InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="stats_close")])
    
    await message.reply(
        f"<b>🔍 sᴇᴀʀᴄʜ:</b> <code>{query}</code>\ɴ\ɴsᴇʟᴇᴄᴛ ᴀ sᴏᴜʀᴄᴇ ᴛᴏ sᴇᴀʀᴄʜ ɪɴ:",
        ʀᴇᴘʟʏ_ᴍᴀʀᴋᴜᴘ=ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅᴍᴀʀᴋᴜᴘ(ʙᴜᴛᴛᴏɴs),
        ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ
    )


@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ(ꜰɪʟᴛᴇʀs.ʀᴇɢᴇx("^sᴇᴀʀᴄʜ_sʀᴄ_"))
ᴀsʏɴᴄ ᴅᴇꜰ sᴇᴀʀᴄʜ_sᴏᴜʀᴄᴇ_ᴄʙ(ᴄʟɪᴇɴᴛ, ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ):
    ᴘᴀʀᴛs = ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴅᴀᴛᴀ.sᴘʟɪᴛ("_", 3)
    sᴏᴜʀᴄᴇ = ᴘᴀʀᴛs[2]
    ǫᴜᴇʀʏ = ᴘᴀʀᴛs[3] # ᴛʜɪs ᴍɪɢʜᴛ ʙᴇ ᴛʀᴜɴᴄᴀᴛᴇᴅ, ʙᴜᴛ ᴡᴇ ᴜsᴇᴅ ᴍᴇssᴀɢᴇ ᴛᴇxᴛ ɪɴ ᴏʀɪɢɪɴᴀʟ. 
    
    ᴀᴘɪ = ɢᴇᴛ_ᴀᴘɪ_ᴄʟᴀss(sᴏᴜʀᴄᴇ)
    ɪꜰ ɴᴏᴛ ᴀᴘɪ:
        ᴀᴡᴀɪᴛ ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴀɴsᴡᴇʀ("sᴏᴜʀᴄᴇ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ", sʜᴏᴡ_ᴀʟᴇʀᴛ=ᴛʀᴜᴇ)
        ʀᴇᴛᴜʀɴ
        
    sᴛᴀᴛᴜs_ᴍsɢ = ᴀᴡᴀɪᴛ ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴍᴇssᴀɢᴇ.ᴇᴅɪᴛ_ᴛᴇxᴛ(f"<i>🔍 Searching {source}...</i>", parse_mode=enums.ParseMode.HTML)
    
    async with API(Config) as api:
        results = await api.search_manga(query)
    
    if not results:
        await status_msg.edit_text(f"❌ ɴᴏ ʀᴇsᴜʟᴛs ꜰᴏᴜɴᴅ ɪɴ {source}.")
        ʀᴇᴛᴜʀɴ

    ʙᴜᴛᴛᴏɴs = []
    ꜰᴏʀ ᴍ ɪɴ ʀᴇsᴜʟᴛs[:10]: # ᴛᴏᴘ 10
        ᴛɪᴛʟᴇ = ᴍ['ᴛɪᴛʟᴇ']
        ʙᴜᴛᴛᴏɴs.ᴀᴘᴘᴇɴᴅ([ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅʙᴜᴛᴛᴏɴ(ᴛɪᴛʟᴇ, ᴄᴀʟʟʙᴀᴄᴋ_ᴅᴀᴛᴀ=f"view_{source}_{m['id']}")])
    
    buttons.append([InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="stats_close")])
    
    await status_msg.edit_text(
        f"<b>ꜰᴏᴜɴᴅ {len(results)} ʀᴇsᴜʟᴛs ɪɴ {source}:</b>",
        ʀᴇᴘʟʏ_ᴍᴀʀᴋᴜᴘ=ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅᴍᴀʀᴋᴜᴘ(ʙᴜᴛᴛᴏɴs),
        ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ
    )


@ᴄʟɪᴇɴᴛ.ᴏɴ_ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ(ꜰɪʟᴛᴇʀs.ʀᴇɢᴇx("^ᴠɪᴇᴡ_"))
ᴀsʏɴᴄ ᴅᴇꜰ ᴠɪᴇᴡ_ᴍᴀɴɢᴀ_ᴄʙ(ᴄʟɪᴇɴᴛ, ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ):
    ᴘᴀʀᴛs = ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴅᴀᴛᴀ.sᴘʟɪᴛ("_", 2)
    sᴏᴜʀᴄᴇ = ᴘᴀʀᴛs[1]
    ᴍᴀɴɢᴀ_ɪᴅ = ᴘᴀʀᴛs[2]
    
    ᴀᴘɪ = ɢᴇᴛ_ᴀᴘɪ_ᴄʟᴀss(sᴏᴜʀᴄᴇ)
    ɪꜰ ɴᴏᴛ ᴀᴘɪ: ʀᴇᴛᴜʀɴ

    ᴀsʏɴᴄ ᴡɪᴛʜ ᴀᴘɪ(ᴄᴏɴꜰɪɢ) ᴀs ᴀᴘɪ:
        ɪɴꜰᴏ = ᴀᴡᴀɪᴛ ᴀᴘɪ.ɢᴇᴛ_ᴍᴀɴɢᴀ_ɪɴꜰᴏ(ᴍᴀɴɢᴀ_ɪᴅ)
    
    ɪꜰ ɴᴏᴛ ɪɴꜰᴏ:
        ᴀᴡᴀɪᴛ ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴀɴsᴡᴇʀ("ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴅᴇᴛᴀɪʟs", sʜᴏᴡ_ᴀʟᴇʀᴛ=ᴛʀᴜᴇ)
        ʀᴇᴛᴜʀɴ

    ᴄᴀᴘᴛɪᴏɴ = (
        f"<b>📖 {info['title']}</b>\n"
        f"<b>Source:</b> {source}\n"
        f"<b>ID:</b> <code>{manga_id}</code>\n\n"
        f"Select an option:"
    )
    
    buttons = [
        [InlineKeyboardButton("⬇ ᴅᴏᴡɴʟᴏᴀᴅ ᴄʜᴀᴘᴛᴇʀs", callback_data=f"chapters_{source}_{manga_id}_0")],
        [InlineKeyboardButton("⬇ ᴄᴜsᴛᴏᴍ ᴅᴏᴡɴʟᴏᴀᴅ (ʀᴀɴɢᴇ)", callback_data=f"custom_dl_{source}_{manga_id}")],
        [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="stats_close")] 
    ]
    
    msg = callback_query.message
    await edit_msg_with_pic(msg, caption, InlineKeyboardMarkup(buttons))



@Client.on_callback_query(filters.regex("^chapters_"))
async def chapters_list_cb(client, callback_query):
    parts = callback_query.data.split("_")
    if len(parts) < 4:
        await callback_query.answer("❌ Invalid callback data", show_alert=True)
        return
    
    source = parts[1]
    offset = int(parts[-1])  # Last part is always offset
    manga_id = "_".join(parts[2:-1])  # Everything between source and offset
    
    API = get_api_class(source)
    async with API(Config) as api:
        chapters = await api.get_manga_chapters(manga_id, limit=10, offset=offset)
    
    if not chapters and offset == 0:
        await callback_query.answer("No chapters found.", show_alert=True)
        return
    elif not chapters:
        await callback_query.answer("No more chapters.", show_alert=True)
        return

    buttons = []
    row = []
    for ch in chapters:
        ch_num = ch['chapter']
        btn_text = f"ᴄʜ {ch_num}"
        
        
        ʀᴏᴡ.ᴀᴘᴘᴇɴᴅ(ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅʙᴜᴛᴛᴏɴ(ʙᴛɴ_ᴛᴇxᴛ, ᴄᴀʟʟʙᴀᴄᴋ_ᴅᴀᴛᴀ=f"dl_ask_{source}_{manga_id}_{ch['id'][:20]}")) # DANGEROUS HACK
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    
    nav = []
    if offset >= 10:
        nav.append(InlineKeyboardButton("⬅ ᴘʀᴇᴠ", callback_data=f"chapters_{source}_{manga_id}_{offset-10}"))
    nav.append(InlineKeyboardButton("ɴᴇxᴛ ➡", callback_data=f"chapters_{source}_{manga_id}_{offset+10}"))
    buttons.append(nav)
    
    buttons.append([InlineKeyboardButton("⬅ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɴɢᴀ", callback_data=f"view_{source}_{manga_id}")])
    
    caption_text = f"<b>sᴇʟᴇᴄᴛ ᴄʜᴀᴘᴛᴇʀ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ (sᴛᴀɴᴅᴀʀᴅ):</b>\ɴᴘᴀɢᴇ: {int(offset/10)+1}\ɴ<i>ɴᴏᴛᴇ: ᴜᴘʟᴏᴀᴅs ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ ᴄʜᴀɴɴᴇʟ.</i>"
    
    ᴛʀʏ:
        ɪꜰ ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴍᴇssᴀɢᴇ.ᴘʜᴏᴛᴏ:
            ᴀᴡᴀɪᴛ ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴍᴇssᴀɢᴇ.ᴇᴅɪᴛ_ᴄᴀᴘᴛɪᴏɴ(ᴄᴀᴘᴛɪᴏɴ=ᴄᴀᴘᴛɪᴏɴ_ᴛᴇxᴛ, ʀᴇᴘʟʏ_ᴍᴀʀᴋᴜᴘ=ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅᴍᴀʀᴋᴜᴘ(ʙᴜᴛᴛᴏɴs))
        ᴇʟsᴇ:
            ᴀᴡᴀɪᴛ ᴄᴀʟʟʙᴀᴄᴋ_ǫᴜᴇʀʏ.ᴍᴇssᴀɢᴇ.ᴇᴅɪᴛ_ᴛᴇxᴛ(ᴄᴀᴘᴛɪᴏɴ_ᴛᴇxᴛ, ʀᴇᴘʟʏ_ᴍᴀʀᴋᴜᴘ=ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅᴍᴀʀᴋᴜᴘ(ʙᴜᴛᴛᴏɴs), ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ)
    ᴇxᴄᴇᴘᴛ ᴇxᴄᴇᴘᴛɪᴏɴ ᴀs ᴇ:
        ᴘʀɪɴᴛ(f"Edit error: {e}")


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


@Client.on_callback_query(filters.regex("^custom_dl_"))
async def custom_dl_start_cb(client, callback_query):
    parts = callback_query.data.split("_")
    source = parts[2]
    manga_id = "_".join(parts[3:])
    
    user_id = callback_query.from_user.id
    
    user_states[user_id] = WAITING_CHAPTER_INPUT
    user_data[user_id] = {
        'source': source,
        'manga_id': manga_id
    }
    
    await callback_query.message.reply_text(
        "<b>⬇ ᴄᴜsᴛᴏᴍ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴏᴅᴇ</b>\ɴ\ɴ"
        "Please enter the Chapter Number you want to download.\n"
        "You can download a single chapter or a range.\n\n"
        "<b>Examples:</b>\n"
        "<code>5</code> (Download Chapter 5)\n"
        "<code>10-20</code> (Download Chapters 10 to 20)\n\n"
        "<i>Downloads will be sent to your Private Chat.</i>",
        parse_mode=enums.ParseMode.HTML
    )
    await callback_query.answer()

async def custom_dl_input_handler(client, message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id in user_states:
        del user_states[user_id]
        
    data = user_data.get(user_id)
    if not data:
        await message.reply("❌ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ sᴇᴀʀᴄʜ ᴀɢᴀɪɴ.")
        return
        
    source = data['source']
    manga_id = data['manga_id']
    
    target_chapters = [] # List of floats/strings numbers
    is_range = False
    
    try:
        if "-" in text:
            is_range = True
            start, end = map(float, text.split("-"))
            range_min = min(start, end)
            range_max = max(start, end)
        else:
            target_chapters.append(float(text))
    except ValueError:
        await message.reply("❌ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ɴᴜᴍʙᴇʀs ʟɪᴋᴇ `5` ᴏʀ `10-20`.")
        return

    status_msg = await message.reply("<i>⏳ ꜰᴇᴛᴄʜɪɴɢ ᴄʜᴀᴘᴛᴇʀ ʟɪsᴛ...</i>", parse_mode=enums.ParseMode.HTML)
    
    API = get_api_class(source)
    all_chapters = []
    
    
    async with API(Config) as api:
        offset = 0
        while True:
            batch = await api.get_manga_chapters(manga_id, limit=100, offset=offset)
            if not batch: break
            all_chapters.extend(batch)
            if len(batch) < 100: break
            offset += 100
            if len(all_chapters) > 2000: break # Safety Break
            
    if not all_chapters:
        await status_msg.edit_text("❌ ɴᴏ ᴄʜᴀᴘᴛᴇʀs ꜰᴏᴜɴᴅ.")
        return

    to_download = []
    for ch in all_chapters:
        try:
            ch_num = float(ch['chapter'])
            if is_range:
                if range_min <= ch_num <= range_max:
                    to_download.append(ch)
            else:
                if ch_num in target_chapters:
                     to_download.append(ch)
        except:
             pass # Skip non-numeric chapters
             
    if not to_download:
        await status_msg.edit_text(f"❌ ɴᴏ ᴄʜᴀᴘᴛᴇʀs ꜰᴏᴜɴᴅ ꜰᴏʀ ɪɴᴘᴜᴛ: {text}")
        ʀᴇᴛᴜʀɴ

    ᴀᴡᴀɪᴛ sᴛᴀᴛᴜs_ᴍsɢ.ᴇᴅɪᴛ_ᴛᴇxᴛ(f"✅ Found {len(to_download)} chapters. Starting download...")
    
    to_download.sort(key=lambda x: float(x['chapter']))
    
    for ch in to_download:
        await execute_download(client, message.chat.id, source, manga_id, ch['id'], user_id) ## Use user_id as upload target?


async def execute_download(client, target_chat_id, source, manga_id, chapter_id, status_chat_id=None):
    """
    Downloads and uploads a chapter.
    status_chat_id: Where to send updates (if different from target).
    """
    if not status_chat_id: status_chat_id = target_chat_id
    
    status_msg = await client.send_message(status_chat_id, "<i>⏳ Initializing download...</i>", parse_mode=enums.ParseMode.HTML)
    
    try:
        API = get_api_class(source)
        async with API(Config) as api:
            meta = await api.get_chapter_info(chapter_id)
            if not meta:
                await status_msg.edit_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇᴛ ᴄʜᴀᴘᴛᴇʀ ɪɴꜰᴏ.")
                return
            
            if meta.get('manga_title') in ['Unknown', None]:
                 m_info = await api.get_manga_info(manga_id)
                 if m_info: meta['manga_title'] = m_info['title']

            images = await api.get_chapter_images(chapter_id)
            
        if not images:
            await status_msg.edit_text(f"❌ ɴᴏ ɪᴍᴀɢᴇs ɪɴ ᴄʜᴀᴘᴛᴇʀ {meta.get('chapter', '?')}")
            ʀᴇᴛᴜʀɴ
            
        ᴄʜᴀᴘᴛᴇʀ_ᴅɪʀ = ᴘᴀᴛʜ(ᴄᴏɴꜰɪɢ.ᴅᴏᴡɴʟᴏᴀᴅ_ᴅɪʀ) / f"{source}_{manga_id}" / f"ch_{meta['chapter']}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        await status_msg.edit_text(f"<i>⬇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ {len(images)} ᴘᴀɢᴇs...</i>", ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ)
        
        ᴀsʏɴᴄ ᴡɪᴛʜ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ(ᴄᴏɴꜰɪɢ) ᴀs ᴅᴏᴡɴʟᴏᴀᴅᴇʀ:
            ɪꜰ ɴᴏᴛ ᴀᴡᴀɪᴛ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ.ᴅᴏᴡɴʟᴏᴀᴅ_ɪᴍᴀɢᴇs(ɪᴍᴀɢᴇs, ᴄʜᴀᴘᴛᴇʀ_ᴅɪʀ):
                 ᴀᴡᴀɪᴛ sᴛᴀᴛᴜs_ᴍsɢ.ᴇᴅɪᴛ_ᴛᴇxᴛ("❌ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ.")
                 ʀᴇᴛᴜʀɴ
            
            ᴀᴡᴀɪᴛ sᴛᴀᴛᴜs_ᴍsɢ.ᴇᴅɪᴛ_ᴛᴇxᴛ("<i>⚙️ ᴘʀᴏᴄᴇssɪɴɢ ᴘᴅꜰ...</i>", ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ)
            
            ꜰɪʟᴇ_ᴛʏᴘᴇ = ᴀᴡᴀɪᴛ sᴇɪsʜɪʀᴏ.ɢᴇᴛ_ᴄᴏɴꜰɪɢ("ꜰɪʟᴇ_ᴛʏᴘᴇ", "ᴘᴅf")
            quality = await Seishiro.get_config("image_quality")
            
            banner_1 = await Seishiro.get_config("banner_image_1")
            banner_2 = await Seishiro.get_config("banner_image_2")
            
            intro_p = None; outro_p = None
            if banner_1:
                 intro_p = chapter_dir.parent / "intro.jpg"
                 try: await client.download_media(banner_1, file_name=str(intro_p))
                 except: intro_p = None
            if banner_2:
                 outro_p = chapter_dir.parent / "outro.jpg"
                 try: await client.download_media(banner_2, file_name=str(outro_p))
                 except: outro_p = None

            final_path = await asyncio.to_thread(
                 downloader.create_chapter_file,
                 chapter_dir, meta['manga_title'], meta['chapter'], meta['title'],
                 file_type, intro_p, outro_p, quality
            )
            
            if intro_p and intro_p.exists(): intro_p.unlink()
            if outro_p and outro_p.exists(): outro_p.unlink()
            
            if not final_path:
                 await status_msg.edit_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ ꜰɪʟᴇ.")
                 return
            
            await status_msg.edit_text(f"<i>⬆ ᴜᴘʟᴏᴀᴅɪɴɢ...</i>", ᴘᴀʀsᴇ_ᴍᴏᴅᴇ=ᴇɴᴜᴍs.ᴘᴀʀsᴇᴍᴏᴅᴇ.ʜᴛᴍʟ)
            ᴄᴀᴘᴛɪᴏɴ = f"<b>{meta['manga_title']} - Ch {meta['chapter']}</b>"
            
            await client.send_document(
                chat_id=target_chat_id,
                document=final_path,
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
            
            shutil.rmtree(chapter_dir, ignore_errors=True)
            if final_path.exists(): final_path.unlink()
            
            await status_msg.delete() # Cleanup status message on success to avoid clutter? 

    except Exception as e:
        logger.error(f"DL Error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Error: {e}")


@Client.on_callback_query(filters.regex("^dl_ask_"))
async def dl_ask_cb(client, callback_query):
    data = callback_query.data.split("_")
    source = data[2]
    manga_id = data[3]
    chapter_id = "_".join(data[4:])
    
    
    db_channel = await Seishiro.get_default_channel()
    channel_id = int(db_channel) if db_channel else Config.CHANNEL_ID
    
    await callback_query.answer("Starting download...", show_alert=False)
    await execute_download(client, channel_id, source, manga_id, chapter_id, callback_query.message.chat.id)



# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat