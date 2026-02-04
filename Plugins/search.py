# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
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
        await message.reply("❌ usage: /search <query>")
        return
    
    query = parts[1].strip()
    if len(query) < 2:
        await message.reply("❌ query too short.")
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
        await message.reply("❌ no sources available.")
        return
        
    buttons.append([InlineKeyboardButton("❌ close", callback_data="stats_close")])
    
    await message.reply(
        f"<b>🔍 search:</b> <code>{query}</code>\n\nselect a source to search in:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^search_src_"))
async def search_source_cb(client, callback_query):
    parts = callback_query.data.split("_", 3)
    source = parts[2]
    query = parts[3] # this might be truncated, but we used Message text in original. 
    
    api = get_api_class(source)
    if not api:
        await callback_query.answer("source not available", show_alert=True)
        return
        
    status_msg = await callback_query.message.edit_text(f"<i>🔍 Searching {source}...</i>", parse_mode=enums.ParseMode.HTML)
    
    async with API(Config) as api:
        results = await api.search_manga(query)
    
    if not results:
        await status_msg.edit_text(f"❌ no results found in {source}.")
        return

    buttons = []
    for m in results[:10]: # top 10
        title = m['title']
        buttons.append([InlineKeyboardButton(title, callback_data=f"view_{source}_{m['id']}")])
    
    buttons.append([InlineKeyboardButton("❌ close", callback_data="stats_close")])
    
    await status_msg.edit_text(
        f"<b>found {len(results)} results in {source}:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex("^view_"))
async def view_manga_cb(client, callback_query):
    parts = callback_query.data.split("_", 2)
    source = parts[1]
    manga_id = parts[2]
    
    api = get_api_class(source)
    if not api: return

    async with api(Config) as api:
        info = await api.get_manga_info(manga_id)
    
    if not info:
        await callback_query.answer("error fetching details", show_alert=True)
        return

    caption = (
        f"<b>📖 {info['title']}</b>\n"
        f"<b>Source:</b> {source}\n"
        f"<b>ID:</b> <code>{manga_id}</code>\n\n"
        f"Select an option:"
    )
    
    buttons = [
        [InlineKeyboardButton("⬇ download chapters", callback_data=f"chapters_{source}_{manga_id}_0")],
        [InlineKeyboardButton("⬇ custom download (range)", callback_data=f"custom_dl_{source}_{manga_id}")],
        [InlineKeyboardButton("❌ close", callback_data="stats_close")] 
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
        btn_text = f"ch {ch_num}"
        
        
        row.append(InlineKeyboardButton(btn_text, callback_data=f"dl_ask_{source}_{manga_id}_{ch['id'][:20]}")) # DANGEROUS HACK
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    
    nav = []
    if offset >= 10:
        nav.append(InlineKeyboardButton("⬅ prev", callback_data=f"chapters_{source}_{manga_id}_{offset-10}"))
    nav.append(InlineKeyboardButton("next ➡", callback_data=f"chapters_{source}_{manga_id}_{offset+10}"))
    buttons.append(nav)
    
    buttons.append([InlineKeyboardButton("⬅ back to manga", callback_data=f"view_{source}_{manga_id}")])
    
    caption_text = f"<b>select chapter to download (standard):</b>\npage: {int(offset/10)+1}\n<i>note: uploads to default channel.</i>"
    
    try:
        if callback_query.message.photo:
            await callback_query.message.edit_caption(caption=caption_text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await callback_query.message.edit_text(caption_text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.html)
    except Exception as e:
        print(f"Edit error: {e}")


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
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
        "<b>⬇ custom download mode</b>\n\n"
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
        await message.reply("❌ session expired. please search again.")
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
        await message.reply("❌ invalid format. please enter numbers like `5` or `10-20`.")
        return

    status_msg = await message.reply("<i>⏳ fetching chapter list...</i>", parse_mode=enums.ParseMode.HTML)
    
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
        await status_msg.edit_text("❌ no chapters found.")
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
        await status_msg.edit_text(f"❌ no chapters found for input: {text}")
        return

    await status_msg.edit_text(f"✅ Found {len(to_download)} chapters. Starting download...")
    
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
                await status_msg.edit_text("❌ failed to get chapter info.")
                return
            
            if meta.get('manga_title') in ['Unknown', None]:
                 m_info = await api.get_manga_info(manga_id)
                 if m_info: meta['manga_title'] = m_info['title']

            images = await api.get_chapter_images(chapter_id)
            
        if not images:
            await status_msg.edit_text(f"❌ no images in chapter {meta.get('chapter', '?')}")
            return
            
        chapter_dir = Path(Config.DOWNLOAD_DIR) / f"{source}_{manga_id}" / f"ch_{meta['chapter']}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        await status_msg.edit_text(f"<i>⬇ downloading {len(images)} pages...</i>", parse_mode=enums.ParseMode.HTML)
        
        async with Downloader(Config) as downloader:
            if not await downloader.download_images(images, chapter_dir):
                 await status_msg.edit_text("❌ download failed.")
                 return
            
            await status_msg.edit_text("<i>⚙️ processing pdf...</i>", parse_mode=enums.ParseMode.HTML)
            
            file_type = await Seishiro.get_config("file_type", "pdf")
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
                 await status_msg.edit_text("❌ failed to create file.")
                 return
            
            await status_msg.edit_text(f"<i>⬆ uploading...</i>", parse_mode=enums.ParseMode.HTML)
            caption = f"<b>{meta['manga_title']} - Ch {meta['chapter']}</b>"
            
            await client.send_document(
                chat_id=target_chat_id,
                document=final_path,
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )
            
            shutil.rmtree(chapter_dir, ignore_errors=True)
            if final_path.exists(): final_path.unlink()
            
            await status_msg.delete() # Cleanup status Message on success to avoid clutter? 

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
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat