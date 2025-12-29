# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

import logging
import asyncio
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

logger = logging.getLogger(__name__)

class PyrogramHandler:
    def __init__(self, api_id: int, api_hash: str, bot_token: str, channel_id: int, user_id: int, plugins: dict = None, bot_instance=None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.user_id = user_id
        self.plugins = plugins
        self.bot_instance = bot_instance
        self.app = None
        self.flood_wait_until = None

    async def initialize(self):
        try:
            logger.info(f"Initializing Pyrogram with plugins: {self.plugins}")
            self.app = Client(
                "mangadex_bot_session",
                api_id=self.api_id,
                api_hash=self.api_hash,
                bot_token=self.bot_token,
                workdir=".",
                in_memory=False,
                no_updates=False,
                plugins=self.plugins
            )
            if self.bot_instance:
                self.app.bot_instance = self.bot_instance
            
            await self.app.start()
            logger.info("Pyrogram client started")
        except Exception as e:
            logger.error(f"Failed to start Pyrogram: {e}")
            raise

    async def stop(self):
        if self.app:
            await self.app.stop()
            logger.info("Pyrogram stopped")

    def is_flood_waiting(self) -> tuple[bool, int]:
        if self.flood_wait_until:
            remaining = (self.flood_wait_until - datetime.now()).total_seconds()
            if remaining > 0:
                return True, int(remaining)
            self.flood_wait_until = None
        return False, 0

    async def send_notification(self, message: str) -> bool:
        try:
            if not self.user_id or not self.app:
                return False
            await self.app.send_message(self.user_id, message)
            return True
        except FloodWait as e:
            self.flood_wait_until = datetime.now() + timedelta(seconds=e.value + 5)
            logger.warning(f"Flood wait: {e.value}s")
            return False
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return False

    async def upload_chapter(self, file_path: Path, caption: str, thumbnail_path: Optional[Path] = None, progress_callback=None) -> bool:
        for attempt in range(3):
            try:
                is_waiting, remaining = self.is_flood_waiting()
                if is_waiting:
                    logger.warning(f"Flood wait: {remaining}s")
                    return False

                if not file_path.exists():
                    logger.error(f"File not found: {file_path}")
                    return False

                file_size = file_path.stat().st_size
                if file_size > 50 * 1024 * 1024:
                    logger.error(f"File too large: {file_size / (1024*1024):.1f}MB")
                    return False

                thumb = str(thumbnail_path) if thumbnail_path and thumbnail_path.exists() else None

                logger.info(f"Uploading to {self.channel_id} → {file_path.name} ({file_size/(1024*1024):.1f}MB)")

                msg = await self.app.send_document(
                    chat_id=self.channel_id,
                    document=str(file_path),
                    caption=caption,
                    thumb=thumb,
                    file_name=file_path.name,
                    parse_mode=enums.ParseMode.HTML,
                    progress=progress_callback
                )
                logger.info("Upload successful")
                return msg.document.file_id

            except FloodWait as e:
                self.flood_wait_until = datetime.now() + timedelta(seconds=e.value + 5)
                logger.warning(f"Flood wait: {e.value + 5}s")
                return None
            except Exception as e:
                logger.error(f"Upload failed (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    await asyncio.sleep(10 * (attempt + 1))

        return None

    async def send_post(self, chat_id: int, caption: str, photo_path: Optional[str] = None, button_url: str = None, channel_link: str = None) -> bool:
        try:
            buttons = []
            if button_url:
                buttons.append(InlineKeyboardButton("📥 ʀᴇᴀᴅ ᴍᴀɴɢᴀ", url=button_url))
            if channel_link:
                buttons.append(InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/about_zani/195"))
                
            markup = InlineKeyboardMarkup([buttons]) if buttons else None
            
            if photo_path and os.path.exists(photo_path):
                await self.app.send_photo(
                    chat_id=chat_id,
                    photo=photo_path,
                    caption=caption,
                    reply_markup=markup,
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await self.app.send_message(
                    chat_id=chat_id,
                    text=caption,
                    reply_markup=markup,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True
                )
            return True
        except Exception as e:
            logger.error(f"Post sending failed: {e}")
            return False


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat