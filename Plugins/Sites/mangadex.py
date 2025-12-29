# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class MangaDexAPI:
    def __init__(self, config):
        self.config = config
        self.rate_limit_delay = 0.5
        self.session = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=60, connect=30)
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            await asyncio.sleep(0.25)

    async def api_request(self, endpoint: str, params: dict = None, retries: int = 3) -> Optional[dict]:
        if not self.session:
             self.session = aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'})
             
        for attempt in range(retries):
            try:
                await asyncio.sleep(self.rate_limit_delay)
                url = f"{self.config.API_BASE}{endpoint}"
                async with self.session.get(url, params=params) as response:
                    if response.status == 429:
                        wait = int(response.headers.get('Retry-After', 5))
                        logger.warning(f"Rate limited, waiting {wait}s")
                        await asyncio.sleep(wait)
                        continue
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.error(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
        return None

    async def get_manga_info(self, manga_id: str) -> Optional[Dict]:
        try:
            params = {'includes[]': ['cover_art']}
            data = await self.api_request(f'/manga/{manga_id}', params)
            if not data or data.get('result') != 'ok':
                return None
            manga = data['data']
            attrs = manga['attributes']
            title_obj = attrs.get('title', {})
            title = title_obj.get('en', next(iter(title_obj.values())) if title_obj else 'Unknown')
            cover_url = None
            for rel in manga.get('relationships', []):
                if rel['type'] == 'cover_art':
                    cover_file = rel.get('attributes', {}).get('fileName')
                    if cover_file:
                        cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_file}.256.jpg"
                    break
            return {'id': manga_id, 'title': title, 'cover_url': cover_url}
        except Exception as e:
            logger.error(f"Failed to get manga info: {e}")
            return None

    async def get_latest_chapters(self, offset: int = 0) -> List[Dict]:
        """
        Fetches latest chapters from the last 24 hours (or configured lookback).
        """
        try:
            lookback = getattr(self.config, 'LOOKBACK_HOURS', 24)
            time_threshold = datetime.utcnow() - timedelta(hours=lookback)
            time_str = time_threshold.strftime('%Y-%m-%dT%H:%M:%S')

            params = {
                "translatedLanguage[]": ["en"],
                "order[publishAt]": "asc",
                "limit": 50,
                "offset": offset,
                "includes[]": ["manga", "scanlation_group"],
                "contentRating[]": ["safe", "suggestive"],
                "publishAtSince": time_str
            }

            data = await self.api_request('/chapter', params)
            if not data or not data.get('data'):
                return []

            chapters = []
            for item in data['data']:
                attrs = item['attributes']
                if attrs.get('externalUrl'):
                    continue

                manga_id = None
                manga_title = "Unknown"
                for rel in item.get('relationships', []):
                    if rel['type'] == 'manga':
                        manga_id = rel['id']
                        title_obj = rel.get('attributes', {}).get('title', {})
                        manga_title = title_obj.get('en', next(iter(title_obj.values())) if title_obj else 'Unknown')
                        break
                if not manga_id:
                    continue

                group_name = "Unknown"
                for rel in item.get('relationships', []):
                    if rel['type'] == 'scanlation_group':
                        group_name = rel.get('attributes', {}).get('name', 'Unknown')
                        break

                chapters.append({
                    'id': item['id'],
                    'manga_id': manga_id,
                    'manga_title': manga_title,
                    'number': attrs.get('chapter', '0'),
                    'title': attrs.get('title', ''),
                    'group': group_name,
                    'publishAt': attrs.get('publishAt', '')
                })

            return chapters
        except Exception as e:
            logger.error(f"Failed to get chapters: {e}")
            return []

    async def get_chapter_images(self, chapter_id: str) -> Optional[List[str]]:
        try:
            data = await self.api_request(f'/at-home/server/{chapter_id}')
            if not data or data.get('result') != 'ok':
                return None
            base_url = data['baseUrl']
            chapter_hash = data['chapter']['hash']
            filenames = data['chapter']['data']
            return [f"{base_url}/data/{chapter_hash}/{fname}" for fname in filenames]
        except Exception as e:
            logger.error(f"Failed to get images: {e}")
            return None


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat