# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

import motor.motor_asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional
from config import Config

logging.basicConfig(level=logging.INFO)


class Master:
    def __init__(self, DB_URL, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
        self.database = self.dbclient[DB_NAME]

        self.user_data = self.database['users']
        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.del_timer_data = self.database['del_timer']
        self.ban_data = self.database['ban_data']
        self.fsub_data = self.database['fsub']
        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        self.rename_format = self.database['rename_format']
        self.thumb_data = self.database['thumb_data']
        self.upload_data = self.database['upload_data']
        self.manga_chapters = self.database['manga_chapters']
        self.caption_format = self.database['caption_format']
        self.del_timer_data = self.database['del_timer_data']
        self.interval_time = self.database['interval_time']
        self.manga_cache = self.database['manga_cache']
        self.col = self.user_data
        
        self.ADMINS = []

    def new_user(self, id, username=None):
        return dict(
            _id=int(id),
            username=username.lower() if username else None,
            join_date=date.today().isoformat(),
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=date.max.isoformat(),
                ban_reason='',
            )
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id, u.username)
            try:
                await self.user_data.insert_one(user)
                logging.info(f"New user added: {u.id}")
            except Exception as e:
                logging.error(f"Error adding user {u.id}: {e}")
        else:
            logging.info(f"User {u.id} already exists")

    async def is_user_exist(self, id):
        try:
            user = await self.user_data.find_one({"_id": int(id)})
            return bool(user)
        except Exception as e:
            logging.error(f"Error checking user {id}: {e}")
            return False

    async def get_all_users(self):
        cursor = self.user_data.find({})
        users = await cursor.to_list(length=None)
        return [user['_id'] for user in users]

    async def total_users_count(self):
        return await self.user_data.count_documents({})

    async def delete_user(self, user_id):
        await self.user_data.delete_one({"_id": int(user_id)})

    async def is_user_banned(self, user_id):
        try:
            user = await self.ban_data.find_one({"_id": int(user_id)})
            if user:
                ban_status = user.get("ban_status", {})
                return ban_status.get("is_banned", False)
            return False
        except Exception as e:
            logging.error(f"Error checking if user {user_id} is banned: {e}")
            return False
        except Exception as e:
            logging.error(f"Error checking if user {user_id} is banned: {e}")
            return False

    async def ban_user(self, user_id: int, reason: str = None, duration: int = 0) -> bool:
        """
        Ban a user
        
        Args:
            user_id: ID of user to ban
            reason: Reason for ban
            duration: Duration in seconds (0 for permanent)
        """
        try:
            ban_status = {
                "is_banned": True,
                "ban_duration": duration,
                "banned_on": date.today().isoformat(),
                "ban_reason": reason or "No reason provided"
            }
            await self.ban_data.update_one(
                {"_id": int(user_id)},
                {"$set": {"ban_status": ban_status}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error banning user {user_id}: {e}")
            return False

    async def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        try:
            await self.ban_data.update_one(
                {"_id": int(user_id)},
                {"$set": {"ban_status": {"is_banned": False}}}
            )
            return True
        except Exception as e:
            logging.error(f"Error unbanning user {user_id}: {e}")
            return False

    async def is_admin(self, user_id: int) -> bool:
        return bool(await self.admins_data.find_one({"_id": int(user_id)}))

    async def add_admin(self, user_id: int) -> bool:
        try:
            await self.admins_data.update_one(
                {"_id": int(user_id)},
                {"$set": {"_id": int(user_id), "added_at": datetime.utcnow()}},
                upsert=True
            )
            if int(user_id) not in self.ADMINS:
                self.ADMINS.append(int(user_id))
            return True
        except Exception as e:
            logging.error(f"Error adding admin {user_id}: {e}")
            return False

    async def remove_admin(self, user_id: int) -> bool:
        result = await self.admins_data.delete_one({"_id": int(user_id)})
        if int(user_id) in self.ADMINS:
            self.ADMINS.remove(int(user_id))
        return result.deleted_count > 0

    async def list_admins(self) -> list:
        admins = await self.admins_data.find({}).to_list(None)
        self.ADMINS = [a["_id"] for a in admins]
        return self.ADMINS

    async def get_admins(self) -> list:
        """Get the cached list of admins"""
        if not self.ADMINS:
            await self.list_admins()
        return self.ADMINS
        
    async def refresh_admins(self):
        """Load admins from DB to memory"""
        await self.list_admins()


    async def add_fsub_channel(self, channel_id: int) -> bool:
        try:
            await self.fsub_data.update_one(
                {"channel_id": channel_id},
                {"$set": {"channel_id": channel_id, "created_at": datetime.utcnow(), "status": "active", "mode": "off"}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error adding FSub channel {channel_id}: {e}")
            return False

    async def remove_fsub_channel(self, channel_id: int) -> bool:
        result = await self.fsub_data.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0

    async def get_fsub_channels(self) -> List[int]:
        cursor = self.fsub_data.find({"status": "active"})
        channels = await cursor.to_list(None)
        return [ch["channel_id"] for ch in channels if "channel_id" in ch]

    async def show_channels(self) -> List[int]:
        """Alias for get_fsub_channels for backward compatibility"""
        return await self.get_fsub_channels()

    async def get_channel_mode(self, channel_id: int) -> str:
        data = await self.fsub_data.find_one({'channel_id': channel_id})
        return data.get("mode", "off") if data else "off"

    async def get_channel_mode_all(self, channel_id: int) -> str:
        """Alias for get_channel_mode for backward compatibility"""
        return await self.get_channel_mode(channel_id)

    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {'channel_id': channel_id},
            {'$set': {'mode': mode}},
            upsert=True
        )

    async def req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'channel_id': int(channel_id)},
            {'$addToSet': {'user_ids': int(user_id)}},
            upsert=True
        )

    async def del_req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'channel_id': channel_id},
            {'$pull': {'user_ids': user_id}}
        )

    async def req_user_exist(self, channel_id: int, user_id: int) -> bool:
        found = await self.rqst_fsub_Channel_data.find_one({
            'channel_id': int(channel_id),
            'user_ids': int(user_id)
        })
        return bool(found)

    async def set_del_timer(self, value: int):
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        if data:
            return data.get('value', 600)
        return 0

    async def set_check_interval(self, interval: int) -> bool:
        """
        Set the monitoring check interval in seconds
        
        Args:
            interval: Check interval in seconds (minimum 60, maximum 3600)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if interval < 60:
                interval = 60  # Minimum 1 minute
            elif interval > 3600:
                interval = 3600  # Maximum 1 hour
                
            await self.interval_time.update_one(
                {"_id": "bot_config"},
                {"$set": {"check_interval": interval}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting check interval: {e}")
            return False

    async def get_check_interval(self) -> int:
        """
        Get the current monitoring check interval
        
        Returns:
            int: Check interval in seconds (default: 300)
        """
        try:
            Config = await self.interval_time.find_one({"_id": "bot_config"})
            if Config and "check_interval" in Config:
                return Config["check_interval"]
            return 300  # Default 5 minutes
        except Exception as e:
            logging.error(f"Error getting check interval: {e}")
            return 300


    async def get_default_channel(self) -> Optional[int]:
        """Get the default upload channel ID"""
        try:
            doc = await self.channel_data.find_one({"_id": "default_channel"})
            return doc.get("channel_id") if doc else None
        except Exception as e:
            logging.error(f"Error getting default channel: {e}")
            return None

    async def set_default_channel(self, channel_id: int) -> bool:
        """Set the default upload channel"""
        try:
            if channel_id is None:
                return await self.remove_default_channel()
                
            await self.channel_data.update_one(
                {"_id": "default_channel"},
                {"$set": {"channel_id": int(channel_id), "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting default channel {channel_id}: {e}")
            return False

    async def remove_default_channel(self) -> bool:
        """Remove the default upload channel"""
        try:
            result = await self.channel_data.delete_one({"_id": "default_channel"})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error removing default channel: {e}")
            return False

    async def get_format(self) -> str:
        """Get the current filename format template"""
        try:
            doc = await self.rename_format.find_one({"_id": "filename_format"})
            return doc.get("format", "{manga_name} [Ch-{chapter}]") if doc else "{manga_name} [Ch-{chapter}]"
        except Exception as e:
            logging.error(f"Error getting format: {e}")
            return "{manga_name} [Ch-{chapter}]"

    async def set_format(self, format_str: str) -> bool:
        """Set the filename format template"""
        try:
            await self.rename_format.update_one(
                {"_id": "filename_format"},
                {"$set": {"format": format_str, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting format: {e}")
            return False

    async def get_thumbnail(self) -> Optional[str]:
        """Get the file_id of the custom thumbnail"""
        try:
            doc = await self.thumb_data.find_one({"_id": "thumbnail"})
            return doc.get("file_id") if doc else None
        except Exception as e:
            logging.error(f"Error getting thumbnail: {e}")
            return None

    async def set_thumbnail(self, file_id: str, file_unique_id: str) -> bool:
        """Save custom thumbnail file_id and unique_id"""
        try:
            await self.thumb_data.update_one(
                {"_id": "thumbnail"},
                {"$set": {
                    "file_id": file_id,
                    "file_unique_id": file_unique_id,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting thumbnail: {e}")
            return False

    async def delete_thumbnail(self) -> bool:
        """Delete the custom thumbnail"""
        try:
            result = await self.thumb_data.delete_one({"_id": "thumbnail"})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting thumbnail: {e}")
            return False

    async def get_upload_state(self) -> Optional[dict]:
        """Get current upload progress state"""
        try:
            doc = await self.upload_data.find_one({"_id": "upload_state"})
            return doc.get("state") if doc else None
        except Exception as e:
            logging.error(f"Error getting upload state: {e}")
            return None

    async def set_upload_state(self, manga_id: str, manga_title: str, current_index: int, processed: int, total: int) -> bool:
        """Save or update upload progress state"""
        try:
            state = {
                "manga_id": manga_id,
                "manga_title": manga_title,
                "current_index": current_index,
                "processed": processed,
                "total": total,
                "updated_at": datetime.utcnow()
            }
            await self.upload_data.update_one(
                {"_id": "upload_state"},
                {"$set": {"state": state}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting upload state: {e}")
            return False

    async def clear_upload_state(self) -> bool:
        """Clear the upload state after completion or cancellation"""
        try:
            result = await self.upload_data.delete_one({"_id": "upload_state"})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error clearing upload state: {e}")
            return False


    async def manga_store_data(self, chapter_id: str, manga_id: str, manga_title: str, chapter_number: str, file_id: str = None) -> bool:
        """
        Store uploaded chapter data in database to prevent duplicates
        
        Args:
            chapter_id: Unique chapter ID from MangaDex
            manga_id: Manga ID from MangaDex
            manga_title: Name of the manga
            chapter_number: Chapter number
            file_id: Telegram File ID (Optional)
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        try:
            chapter_data = {
                "_id": chapter_id,  # Use chapter_id as unique identifier
                "manga_id": manga_id,
                "manga_title": manga_title,
                "chapter_number": chapter_number,
                "file_id": file_id,
                "uploaded_at": datetime.utcnow()
            }
            
            await self.manga_chapters.update_one(
                {"_id": chapter_id},
                {"$set": chapter_data},
                upsert=True
            )
            
            logging.info(f"Stored chapter data: {manga_title} Ch {chapter_number}")
            return True
            
        except Exception as e:
            logging.error(f"Error storing chapter data {chapter_id}: {e}")
            return False

    async def is_chapter_uploaded(self, chapter_id: str) -> bool:
        """
        Check if a chapter has already been uploaded
        
        Args:
            chapter_id: Chapter ID to check
            
        Returns:
            bool: True if chapter exists in database, False otherwise
        """
        try:
            chapter = await self.manga_chapters.find_one({"_id": chapter_id})
            return bool(chapter)
        except Exception as e:
            logging.error(f"Error checking chapter {chapter_id}: {e}")
            return False

    async def get_chapter_file(self, chapter_id: str) -> Optional[str]:
        """Get file_id for a chapter"""
        try:
            chapter = await self.manga_chapters.find_one({"_id": chapter_id})
            return chapter.get("file_id") if chapter else None
        except Exception as e:
            logging.error(f"Error getting chapter file {chapter_id}: {e}")
            return None

    async def get_uploaded_chapters(self, manga_id: Optional[str] = None, limit: int = 100) -> List[dict]:
        """
        Get list of uploaded chapters, optionally filtered by manga_id
        
        Args:
            manga_id: Optional manga ID to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of chapter documents
        """
        try:
            query = {"manga_id": manga_id} if manga_id else {}
            cursor = self.manga_chapters.find(query).sort("uploaded_at", -1).limit(limit)
            chapters = await cursor.to_list(length=limit)
            return chapters
        except Exception as e:
            logging.error(f"Error getting uploaded chapters: {e}")
            return []

    async def delete_chapter_record(self, chapter_id: str) -> bool:
        """
        Delete a chapter record from database
        
        Args:
            chapter_id: Chapter ID to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            result = await self.manga_chapters.delete_one({"_id": chapter_id})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting chapter record {chapter_id}: {e}")
            return False

    async def cleanup_old_chapters(self, days: int = 30) -> int:
        """
        Delete chapter records older than specified days
        
        Args:
            days: Number of days to keep records
            
        Returns:
            int: Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await self.manga_chapters.delete_many({
                "uploaded_at": {"$lt": cutoff_date}
            })
            logging.info(f"Cleaned up {result.deleted_count} old chapter records")
            return result.deleted_count
        except Exception as e:
            logging.error(f"Error cleaning up old chapters: {e}")
            return 0

    async def get_chapter_count(self) -> int:
        """Get total count of stored chapters"""
        try:
            return await self.manga_chapters.count_documents({})
        except Exception as e:
            logging.error(f"Error getting chapter count: {e}")
            return 0

    async def cache_manga_search(self, manga_id: str, data: dict, ttl: int = 3600):
        """Cache manga search results"""
        try:
            await self.manga_cache.update_one(
                {"_id": manga_id},
                {
                    "$set": {
                        "data": data,
                        "cached_at": datetime.utcnow(),
                        "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error caching manga search: {e}")
            return False

    async def get_cached_manga(self, manga_id: str):
        """Get cached manga data if not expired"""
        try:
            result = await self.manga_cache.find_one({"_id": manga_id})
            if result and result.get("expires_at") > datetime.utcnow():
                return result.get("data")
            return None
        except Exception as e:
            logging.error(f"Error getting cached manga: {e}")
            return None


    async def get_caption(self) -> Optional[str]:
        """Get the current caption format template"""
        try:
            doc = await self.caption_format.find_one({"_id": "caption_format"})
            return doc.get("caption") if doc else None
        except Exception as e:
            logging.error(f"Error getting caption: {e}")
            return None

    async def set_caption(self, caption_str: str) -> bool:
        """Set the caption format template"""
        try:
            await self.caption_format.update_one(
                {"_id": "caption_format"},
                {"$set": {"caption": caption_str, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting caption: {e}")
            return False

    async def delete_caption(self) -> bool:
        """Delete the custom caption format"""
        try:
            result = await self.caption_format.delete_one({"_id": "caption_format"})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting caption: {e}")
            return False


    async def get_watermark(self) -> Optional[dict]:
        """Get the watermark configuration"""
        try:
            doc = await self.database['watermark_config'].find_one({"_id": "watermark"})
            if doc:
                return {
                    "text": doc.get("text"),
                    "position": doc.get("position", "bottom-right"),
                    "color": doc.get("color", "#FFFFFF"),
                    "opacity": doc.get("opacity", 128),
                    "font_size": doc.get("font_size", 20)
                }
            return None
        except Exception as e:
            logging.error(f"Error getting watermark: {e}")
            return None

    async def set_watermark(self, text: str, position: str = "bottom-right", 
                           color: str = "#FFFFFF", opacity: int = 128, 
                           font_size: int = 20) -> bool:
        """
        Set watermark configuration
        
        Args:
            text: Watermark text (supports variables: {manga_name}, {chapter})
            position: Position on image (top-left, top-right, bottom-left, bottom-right, center)
            color: Hex color code (e.g., #FFFFFF for white)
            opacity: Transparency level (0-255, where 0 is fully transparent)
            font_size: Font size for watermark text
        """
        try:
            await self.database['watermark_config'].update_one(
                {"_id": "watermark"},
                {"$set": {
                    "text": text,
                    "position": position,
                    "color": color,
                    "opacity": opacity,
                    "font_size": font_size,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            logging.info(f"Watermark set: {text} at {position}")
            return True
        except Exception as e:
            logging.error(f"Error setting watermark: {e}")
            return False

    async def delete_watermark(self) -> bool:
        """Delete the watermark configuration"""
        try:
            result = await self.database['watermark_config'].delete_one({"_id": "watermark"})
            if result.deleted_count > 0:
                logging.info("Watermark configuration deleted")
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting watermark: {e}")
            return False


    async def get_monitoring_status(self) -> bool:
        """Get monitoring status (True = Running, False = Paused)"""
        try:
            doc = await self.database['bot_settings'].find_one({"_id": "monitoring_status"})
            return doc.get("enabled", True) if doc else True
        except Exception as e:
            logging.error(f"Error getting monitoring status: {e}")
            return True

    async def set_monitoring_status(self, enabled: bool) -> bool:
        """Set monitoring status"""
        try:
            await self.database['bot_settings'].update_one(
                {"_id": "monitoring_status"},
                {"$set": {"enabled": enabled, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting monitoring status: {e}")
            return False


    async def get_config(self, key: str, default=None):
        """Generic get Config"""
        try:
            doc = await self.database['bot_config'].find_one({"_id": key})
            return doc.get("value", default) if doc else default
        except Exception as e:
            logging.error(f"Error getting Config {key}: {e}")
            return default

    async def set_config(self, key: str, value):
        """Generic set Config"""
        try:
            await self.database['bot_config'].update_one(
                {"_id": key},
                {"$set": {"value": value, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error setting Config {key}: {e}")
            return False

    
    async def get_auto_update_channels(self) -> List[dict]:
        """Get list of auto update channels"""
        try:
            cursor = self.database['auto_update_channels'].find({})
            return await cursor.to_list(None)
        except Exception as e:
            logging.error(f"Error getting auc: {e}")
            return []

    async def add_auto_update_channel(self, channel_id: int, title: str) -> bool:
        """Add channel to auto update list"""
        try:
            await self.database['auto_update_channels'].update_one(
                {"_id": channel_id},
                {"$set": {"_id": channel_id, "title": title, "added_at": datetime.utcnow()}},
                upsert=True
            )
            return True
        except Exception as e:
            logging.error(f"Error adding auc {channel_id}: {e}")
            return False

    async def remove_auto_update_channel(self, channel_id: int) -> bool:
        """Remove channel from auto update list"""
        try:
            res = await self.database['auto_update_channels'].delete_one({"_id": channel_id})
            return res.deleted_count > 0
        except Exception as e:
            logging.error(f"Error removing auc {channel_id}: {e}")
            return False

    async def clear_auto_update_channels(self) -> bool:
        """Clear all auto update channels"""
        try:
            await self.database['auto_update_channels'].delete_many({})
            return True
        except Exception as e:
            logging.error(f"Error clearing auc: {e}")
            return False


Seishiro = Master(Config.DB_URL, Config.DB_NAME)


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat