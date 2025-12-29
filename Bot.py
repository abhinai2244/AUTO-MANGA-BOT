# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat


import sys
import os
import json
import asyncio
import shutil
import logging
import gc
from pathlib import Path
from datetime import datetime

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pyrogram import enums, idle
import aiofiles
from aiohttp import web
from Plugins.web_server import web_server

from config import Config
from Plugins.downloading import Downloader
from Plugins.Sites.mangadex import MangaDexAPI
from Plugins.Sites.webcentral import WebCentralAPI
from Plugins.Sites.mangaforest import MangaForestAPI
from Plugins.Sites.mangakakalot import MangakakalotAPI
from Plugins.Sites.allmanga import AllMangaAPI
from Plugins.uploading import PyrogramHandler
from Database.database import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class MangaDexBot:
    def __init__(self, config):
        self.config = config
        self.download_dir = Path(config.DOWNLOAD_DIR)
        self.state_file = Path(config.STATE_FILE)
        self.cache_file = Path(config.CACHE_FILE)
        self.download_dir.mkdir(exist_ok=True)
        self.state = {"uploaded_chapters": []}
        self.manga_cache = {}
        self.db_master = Seishiro
        
        work_dir = Path(__file__).parent
        os.chdir(work_dir)
        self.plugins = {"root": "Plugins"}

        self.upload_channel_id = None # Logic: This is the MAIN CHANNEL (Update/Auto)
        self.dump_channel_id = None # Logic: This is the DUMP CHANNEL (File Storage)
        self.filename_format = config.DEFAULT_FILENAME_FORMAT
        self.has_custom_thumbnail = False  # Flag if DB has custom thumb

        self.telegram = PyrogramHandler(
            config.API_ID, config.API_HASH, config.BOT_TOKEN,
            self.upload_channel_id, config.USER_ID,
            plugins=self.plugins,
            bot_instance=self
        )
        self.processing = False

    async def resolve_dynamic_config(self):
        """Load channel, format, and thumbnail settings from DB with fallbacks"""
        if not self.config.USE_DATABASE:
            logger.info("Database disabled — using defaults")
            return

        try:
            db_channel = await self.db_master.get_default_channel()
            if db_channel:
                logger.info(f"Using DB upload channel (Main): {db_channel}")
                self.upload_channel_id = int(db_channel)
            else:
                logger.warning(f"No DB channel found. Please set 'Upload Channel' in Settings.")
                self.upload_channel_id = None
        except Exception as e:
            logger.error(f"Channel load error: {e}")

        try:
            dump_channel = await self.db_master.get_config("dump_channel")
            if dump_channel:
                 logger.info(f"Using DB Dump Channel: {dump_channel}")
                 self.dump_channel_id = int(dump_channel)
            else:
                 logger.warning("No Dump Channel set. PDF will go to Update Channel if possible.")
                 self.dump_channel_id = self.upload_channel_id
        except Exception as e:
             logger.error(f"Dump Channel load error: {e}")

        try:
            db_format = await self.db_master.get_format()
            if db_format and db_format.strip():
                logger.info(f"Using DB filename format: {db_format}")
                self.filename_format = db_format
            else:
                logger.info("No DB format → using default")
        except Exception as e:
            logger.error(f"Format load error: {e}")
            self.filename_format = self.config.DEFAULT_FILENAME_FORMAT

        try:
            thumb = await self.db_master.get_thumbnail()
            self.has_custom_thumbnail = bool(thumb)
            logger.info(f"Custom thumbnail in DB: {'Yes' if self.has_custom_thumbnail else 'No (using cover)'}")
        except Exception as e:
            logger.error(f"Thumbnail check error: {e}")
            self.has_custom_thumbnail = False

    async def load_state(self) -> dict:
        if self.state_file.exists():
            try:
                async with aiofiles.open(self.state_file, 'r') as f:
                    state = json.loads(await f.read())
                    return state if "uploaded_chapters" in state else {"uploaded_chapters": []}
            except Exception as e:
                logger.error(f"State load failed: {e}")
        return {"uploaded_chapters": []}

    async def save_state(self):
        try:
            async with aiofiles.open(self.state_file, 'w') as f:
                await f.write(json.dumps(self.state, indent=2))
        except Exception as e:
            logger.error(f"State save failed: {e}")

    async def load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                async with aiofiles.open(self.cache_file, 'r') as f:
                    return json.loads(await f.read())
            except Exception as e:
                logger.error(f"Cache load failed: {e}")
        return {}

    async def save_cache(self):
        try:
            async with aiofiles.open(self.cache_file, 'w') as f:
                await f.write(json.dumps(self.manga_cache, indent=2))
        except Exception as e:
            logger.error(f"Cache save failed: {e}")

    async def is_chapter_uploaded(self, chapter_id: str) -> bool:
        if self.config.USE_DATABASE:
            try:
                return await self.db_master.is_chapter_uploaded(chapter_id)
            except Exception as e:
                logger.error(f"DB check failed → fallback: {e}")
        return chapter_id in self.state["uploaded_chapters"]

    async def mark_chapter_uploaded(self, chapter_id: str, manga_id: str, manga_title: str, chapter_num: str, file_id: str = None):
        if self.config.USE_DATABASE:
            try:
                await self.db_master.manga_store_data(chapter_id, manga_id, manga_title, chapter_num, file_id)
            except Exception as e:
                logger.error(f"DB store failed → fallback: {e}")
        if chapter_id not in self.state["uploaded_chapters"]:
            self.state["uploaded_chapters"].append(chapter_id)

    def cleanup_old_records(self):
        if len(self.state["uploaded_chapters"]) > 500:
            self.state["uploaded_chapters"] = self.state["uploaded_chapters"][-500:]
            logger.info("Cleaned old JSON records")

    async def cleanup_downloads(self):
        try:
            if self.download_dir.exists():
                await asyncio.to_thread(shutil.rmtree, self.download_dir, ignore_errors=True)
                self.download_dir.mkdir(exist_ok=True)
                gc.collect()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def _safe_cleanup(self, chapter_dir, file_path, thumb_path):
        """Synchronous cleanup for use with asyncio.to_thread"""
        try:
            if chapter_dir and chapter_dir.exists():
                shutil.rmtree(chapter_dir, ignore_errors=True)
            if file_path and file_path.exists():
                file_path.unlink(missing_ok=True)
            if thumb_path and thumb_path.exists():
                thumb_path.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Safe cleanup failed: {e}")

    def get_api_instance(self, source: str):
        if source.lower() == "webcentral":
            return WebCentralAPI(self.config)
        elif source.lower() == "mangaforest":
             return MangaForestAPI(self.config)
        elif source.lower() == "mangakakalot":
             return MangakakalotAPI(self.config)
        elif source.lower() == "allmanga":
             return AllMangaAPI(self.config)
        else:
             return MangaDexAPI(self.config)

    async def _get_api_context(self):
         """Helper to get the correct API context manager based on current config"""
         source = await self.db_master.get_config('manga_source', 'mangadex')
         return self.get_api_instance(source)


    async def process_chapter(self, chapter: dict) -> bool:
        chapter_dir = None
        file_path = None
        thumb_path = None

        try:
            manga_id = chapter['manga_id']
            manga_title = chapter['manga_title']
            chapter_id = chapter['id']
            chapter_url = chapter.get('url', chapter['id']) # Fallback to ID if no URL (legacy)
            
            chapter_num = chapter.get('number') or chapter.get('chapter') or '0'
            chapter_title = chapter.get('title') or ''

            logger.info(f"\n{'='*60}\nProcessing: {manga_title} - Ch {chapter_num}\n{'='*60}")
            
            last_update_time = 0
            async def progress_hook(current, total, action="Processing"):
                nonlocal last_update_time
                import time
                
                is_complete = (current == total)
                
                if not is_complete and time.time() - last_update_time < 3: 
                    return
                
                last_update_time = time.time()
                
                idx = 1 if action == "Uploading" else 0
                display_title = f"[{action}] {manga_title} - Ch {chapter_num}"
                
                await self.db_master.set_upload_state(
                    manga_id, display_title, idx, current, total
                )

            if await self.is_chapter_uploaded(chapter_id):
                logger.info("Already uploaded")
                return False

            source = await self.db_master.get_config('manga_source', 'mangadex')
            
            
            
            cover_url = None
            if manga_id not in self.manga_cache:
                api_instance = self.get_api_instance(source)
                try:
                    if hasattr(api_instance, '__aenter__'):
                         async with api_instance as api:
                             info = await api.get_manga_info(manga_id)
                    else:
                         info = await api_instance.get_manga_info(manga_id)
                         
                    if info:
                        self.manga_cache[manga_id] = info
                        await self.save_cache()
                except Exception as e:
                    logger.warning(f"Failed to fetch manga info: {e}")

            manga_info = self.manga_cache.get(manga_id, {'cover_url': None})
            cover_url = manga_info.get('cover_url')

            api_instance = self.get_api_instance(source)
            images = []
            if hasattr(api_instance, '__aenter__'):
                async with api_instance as api:
                     images = await api.get_chapter_images(chapter_url) # Use URL for fetching
            else:
                 images = await api_instance.get_chapter_images(chapter_url)

            if not images or len(images) > 200:
                logger.error("Invalid chapter images")
                return False

            safe_manga_id = str(manga_id).replace('/', '_').replace(':', '_')[-20:]
            chapter_dir = self.download_dir / safe_manga_id / f"ch_{chapter_num}"

            source_headers = getattr(api_instance, 'headers', None)

            async with Downloader(self.config) as downloader:
                async def dl_progress(curr, tot):
                    await progress_hook(curr, tot, "Downloading")

                if not await downloader.download_images(images, chapter_dir, dl_progress, headers=source_headers):
                    return False

                cover_url = manga_info.get('cover_url')
                cover_path = chapter_dir.parent / "cover.jpg" if cover_url else None
                if cover_url:
                    await downloader.download_cover(cover_url, cover_path, headers=source_headers)

                file_type = await self.db_master.get_config("file_type", "pdf")
                quality = await self.db_master.get_config("image_quality") # returns None or int
                pdf_password = await self.db_master.get_config("pdf_password") # Get Password
                
                banner_1_id = await self.db_master.get_config("banner_image_1")
                banner_2_id = await self.db_master.get_config("banner_image_2")
                
                intro_path = None
                outro_path = None
                
                if banner_1_id:
                    intro_path = chapter_dir.parent / "intro_banner.jpg"
                    try:
                        await self.telegram.app.download_media(banner_1_id, file_name=str(intro_path))
                    except Exception as e:
                        logger.error(f"Failed to download intro banner: {e}")
                        intro_path = None

                if banner_2_id:
                    outro_path = chapter_dir.parent / "outro_banner.jpg"
                    try:
                        await self.telegram.app.download_media(banner_2_id, file_name=str(outro_path))
                    except Exception as e:
                         logger.error(f"Failed to download outro banner: {e}")
                         outro_path = None
                
                watermark = await self.db_master.get_watermark()

                base_file = await asyncio.to_thread(
                    downloader.create_chapter_file, 
                    chapter_dir, 
                    manga_title, 
                    chapter_num, 
                    chapter_title,
                    file_type,
                    intro_path,
                    outro_path,
                    quality,
                    watermark,
                    password=pdf_password # Pass Password
                )
                
                if intro_path and intro_path.exists(): intro_path.unlink()
                if outro_path and outro_path.exists(): outro_path.unlink()
                
                if not base_file:
                    return False

                safe_manga = "".join(c for c in manga_title if c.isalnum() or c in " -_[]")
                safe_chap = chapter_num.replace('.', '-')
                try:
                    final_name = self.filename_format.format(
                        manga_name=safe_manga,
                        chapter=safe_chap,
                        chapter_title=chapter_title.strip()
                    )
                except KeyError:
                    final_name = f"{safe_manga} [Ch-{safe_chap}]"

                final_name = "".join(c for c in final_name if c.isalnum() or c in " -_[]()")[:150].strip()
                
                ext = ".cbz" if file_type.lower() == "cbz" else ".pdf"
                if not final_name.lower().endswith(ext):
                    final_name += ext
                    
                file_path = chapter_dir.parent / final_name

                if base_file != file_path:
                    base_file.rename(file_path)

                if self.has_custom_thumbnail:
                    thumb_path = cover_path if cover_path and cover_path.exists() else None
                    logger.info("Custom thumbnail enabled → using manga cover as thumb")
                else:
                    thumb_path = cover_path if cover_path and cover_path.exists() else None


                channel_sticker = await self.db_master.get_config("channel_stickers")
                update_sticker = await self.db_master.get_config("update_sticker")

                if channel_sticker:
                    try:
                        await self.telegram.app.send_sticker(self.upload_channel_id, channel_sticker)
                    except Exception as e:
                         logger.error(f"Failed to send Channel Sticker: {e}")

                if update_sticker:
                    try:
                         await self.telegram.app.send_sticker(self.upload_channel_id, update_sticker)
                    except Exception as e:
                         logger.error(f"Failed to send Update Sticker: {e}")

                storage_caption = f"{final_name}\n{manga_title} - Ch {chapter_num}"
                
                target_dump = self.dump_channel_id if self.dump_channel_id else self.upload_channel_id
                
                if not target_dump:
                     logger.error("No Dump or Upload Channel configured for file storage!")
                     return False
                     
                
                original_cid = self.telegram.channel_id
                self.telegram.channel_id = target_dump

                async def ul_progress(curr, tot):
                     await progress_hook(curr, tot, "Uploading")
                
                file_id = await self.telegram.upload_chapter(file_path, storage_caption, thumb_path, ul_progress)
                
                self.telegram.channel_id = original_cid # Restore just in case
                
                if not file_id:
                    logger.error("Failed to upload to storage")
                    return False

                await self.mark_chapter_uploaded(chapter_id, manga_id, manga_title, chapter_num, file_id)
                await self.save_state()

                try:
                    bot_username = self.telegram.app.me.username if self.telegram.app.me else "Bot"
                except:
                    bot_username = "Bot"

                deep_link = f"https://t.me/{bot_username}?start=dl_{chapter_id}"

                import html
                clean_title = html.escape(manga_title)
                clean_chapter = html.escape(f"Ch {chapter_num}")
                clean_chap_title = html.escape(chapter_title) if chapter_title else ""
                clean_group = html.escape(chapter['group'])

                caption = (
                    f"<blockquote><b>{clean_title}</b></blockquote>\n\n"
                    f"<blockquote><i>{clean_chapter}</i>"
                )
                if clean_chap_title:
                    caption += f"\n{clean_chap_title}"
                caption += (
                    f"\n{clean_group}\n"
                    f"English</blockquote>\n\n"
                    f"@seishiro_atanime"
                )

                post_photo = str(thumb_path) if thumb_path else None
                
                channel_link = "https://t.me/about_zani/195"

                
                success = False
                if self.upload_channel_id:
                     success = await self.telegram.send_post(
                        chat_id=self.upload_channel_id,
                        caption=caption,
                        photo_path=post_photo,
                        button_url=deep_link,
                        channel_link=channel_link
                    )
                
                try:
                     auto_channels = await self.db_master.get_auto_update_channels() # Returns list of dicts {'id':..., 'name':...} or similar
                     if auto_channels:
                         for ch in auto_channels:
                             cid = ch.get('id')
                             if cid and cid != self.upload_channel_id:
                                  try:
                                      await self.telegram.send_post(
                                            chat_id=cid,
                                            caption=caption,
                                            photo_path=post_photo,
                                            button_url=deep_link,
                                            channel_link=channel_link
                                      )
                                  except Exception as e:
                                       logger.warning(f"Failed to post to Auto Channel {cid}: {e}")
                except Exception as e:
                     logger.error(f"Auto Update broadcast error: {e}")

                if not success and not self.upload_channel_id:
                    logger.info("No Main Update Channel set, but Dump upload successful.")
                    return True
                
                if not success:
                    pass # We already logged in send_post probably

                if not success:
                    return False

                logger.info("Chapter posted successfully!")
                await self.telegram.send_notification(f"Posted: {manga_title} - Ch {chapter_num}")
                return True

        except Exception as e:
            logger.error(f"Processing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return False
        finally:
            await self.db_master.clear_upload_state()
            try:
                await asyncio.to_thread(self._safe_cleanup, chapter_dir, file_path, thumb_path)
            except Exception as e:
                logger.error(f"Final cleanup error: {e}")

        if thumb_path and thumb_path.exists():
            thumb_path.unlink(missing_ok=True)
        gc.collect()

    async def check_updates(self):
        if self.processing:
            return
        self.processing = True
        try:
            logger.info(f"\nChecking for new chapters — {datetime.now().strftime('%H:%M:%S')}")
            
            await self.resolve_dynamic_config()

            source = await self.db_master.get_config('manga_source', 'mangadex')
            logger.info(f"Using source: {source}")
            
            api_instance = self.get_api_instance(source)
            chapters = []
            
            if hasattr(api_instance, '__aenter__'):
                async with api_instance as api:
                    chapters = await api.get_latest_chapters()
            else:
                chapters = await api_instance.get_latest_chapters()

            if not chapters:
                logger.info("No new chapters found")
                return

            new_chapters = [ch for ch in chapters if not await self.is_chapter_uploaded(ch['id'])]
            logger.info(f"Found {len(new_chapters)} new chapters")

            count = 0
            for i, chapter in enumerate(new_chapters[:self.config.MAX_CHAPTERS_PER_CHECK], 1):
                if not await self.db_master.get_monitoring_status():
                    logger.info("Monitoring disabled by user - Stopping current batch.")
                    break

                logger.info(f"[{i}/{len(new_chapters)}] Processing...")
                if await self.process_chapter(chapter):
                    count += 1
                    await asyncio.sleep(5)
                await self.cleanup_downloads()

            logger.info(f"Uploaded {count} chapters this cycle")
            self.cleanup_old_records()
            await self.save_state()

        finally:
            self.processing = False

    async def monitor_loop(self):
        logger.info("Starting monitoring loop...")
        while True:
            try:
                if await self.db_master.get_monitoring_status():
                    await self.check_updates()
                else:
                    logger.info("Monitoring paused...")
                
                interval = await self.db_master.get_check_interval()
                if not interval: interval = 300
                
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)

    async def run(self):
        logger.info("\n" + "="*60)
        logger.info("MANGADEX BOT STARTED — FULL DYNAMIC CONFIG")
        logger.info("="*60)

        self.state = await self.load_state()
        self.manga_cache = await self.load_cache()

        await self.telegram.initialize()
        
        try:
            await self.db_master.refresh_admins()
            logger.info(f"Loaded {len(self.db_master.ADMINS)} admins from DB")
        except Exception as e:
            logger.error(f"Failed to load admins: {e}")

        await self.resolve_dynamic_config()
        
        if self.upload_channel_id:
            try:
                db_channel = await self.telegram.app.get_chat(self.upload_channel_id)
                self.db_channel = db_channel
                logger.info(f"Connected to DB Channel: {db_channel.title}")
            except Exception as e:
                logger.warning(f"DB Channel Check Failed on {self.upload_channel_id}: {e}")
        else:
            logger.warning("No Upload/Dump Channel Configured!")
        
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", self.config.PORT).start()
            logger.info(f"Web Server started on port {self.config.PORT}")
        except Exception as e:
            logger.error(f"Web Server failed to start: {e}")

        try:
            await self.telegram.send_notification("<b><blockquote>🤖 Bot Restarted</blockquote></b>")
        except:
            pass

        await self.db_master.set_monitoring_status(False)
        logger.info("Initial Monitoring Status: PAUSED (as requested)")

        logger.info(f"Upload Channel: {self.upload_channel_id}")
        logger.info(f"Filename Format: {self.filename_format}")
        logger.info(f"Custom Thumbnail: {'Enabled' if self.has_custom_thumbnail else 'Enabled'}")
        logger.info("="*60 + "\n")

        monitor_task = asyncio.create_task(self.monitor_loop())
        
        try:
            await idle()
        except KeyboardInterrupt:
            logger.info("\nStopped by user")
        finally:
            monitor_task.cancel()
            await self.telegram.stop()
            await self.save_state()
            await self.save_cache()
            await self.cleanup_downloads()
            logger.info("Bot stopped cleanly")

async def main():
    bot = MangaDexBot(Config)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat