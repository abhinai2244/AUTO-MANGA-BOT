# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
# Supoort group @rexbotschat

import logging
import aiohttp
import re
import asyncio
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString

logger = logging.getLogger(__name__)

class MangakakalotAPI:
    def __init__(self, config=None):
        self.config = config
        self.base_url = "https://www.mangakakalot.gg"
        self.latest_url = "https://www.mangakakalot.gg/?/latest"  # Confirmed working as of Dec 29, 2025
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://www.mangakakalot.gg/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    async def aenter(self):
        return self

    async def aexit(self, exc_type, exc_val, exc_tb):
        pass

    def parse_upload_hours_ago(self, time_text: str) -> Optional[float]:
        """Parse time like '*17 minute ago*', '*14 hour ago*', '*Just now*', or date '*12-14 07:32*'"""
        if not time_text:
            return None
        time_text = time_text.strip().lower().replace('*', ' ').strip()

        if 'just now' in time_text:
            return 0.0

        minute_match = re.search(r'(\d+)\s*minute', time_text)
        if minute_match:
            mins = int(minute_match.group(1))
            return mins / 60.0

        hour_match = re.search(r'(\d+)\s*hour', time_text)
        if hour_match:
            hours = int(hour_match.group(1))
            return float(hours)

        day_match = re.search(r'(\d+)\s*day', time_text)
        if day_match:
            days = int(day_match.group(1))
            return days * 24.0

        # Date format like '12-14 07:32' → older than 24h
        if re.search(r'\d{1,2}-\d{1,2}', time_text):
            return None

        return None

    async def get_latest_chapters(self, limit: int = 50) -> List[Dict]:
        chapters = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(self.latest_url, timeout=60) as resp:
                    if resp.status != 200:
                        logger.error(f"Mangakakalot latest page fetch failed: {resp.status}")
                        return []
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                # Find all <a> tags that are manga titles (long text, no 'chapter' in href)
                # Fixed regex: remove leading ^ to support absolute URLs
                manga_a_tags = soup.find_all('a', href=re.compile(r'/manga/[^/]+$'))

                for manga_a in manga_a_tags:
                    if len(chapters) >= limit:
                        break
                    manga_url = urljoin(self.base_url, manga_a['href'])
                    manga_title = manga_a.get_text(strip=True)

                    # Find the parent container (usually div or direct parent) to get following chapters
                    parent = manga_a.parent

                    # Look for <ul> or direct <li> with chapter links after the title
                    chapter_container = parent.find_next_sibling('ul') or parent

                    # Find all chapter <a> in the vicinity
                    chapter_as = chapter_container.find_all('a', href=re.compile(r'/chapter/'), limit=10)  # limit per manga

                    for chapter_a in chapter_as:
                        if len(chapters) >= limit:
                            break
                        chapter_url = urljoin(self.base_url, chapter_a['href'])
                        chapter_title = chapter_a.get_text(strip=True)
                        # Extract time: text after the <a> tag (NavigableString)
                        time_text = ""
                        next_sib = chapter_a.next_sibling
                        while next_sib:
                            if isinstance(next_sib, NavigableString):
                                candidate = next_sib.strip()
                                if candidate.startswith('*') or 'ago' in candidate or '-' in candidate:
                                    time_text = candidate
                                    break
                            elif hasattr(next_sib, 'next_sibling'):
                                next_sib = next_sib.next_sibling
                            else:
                                break

                        # Fallback: check parent <li> tail or strings
                        if not time_text and chapter_a.parent:
                            tail = chapter_a.parent.get_text()
                            after = tail.split(chapter_title, 1)[-1] if chapter_title in tail else ""
                            time_match = re.search(r'\*([^ *]+(?:minute|hour|day|ago|now|\d{1,2}-\d{1,2}).*?)\*', after, re.I)
                            if time_match:
                                time_text = '*' + time_match.group(1) + '*'

                        hours_ago = self.parse_upload_hours_ago(time_text)


                        if hours_ago is None or hours_ago > 24:
                            break  # Older chapters come after, stop for this manga

                        num_match = re.search(r'Chapter\s*(\d+(?:\.\d+)?)', chapter_title, re.I)
                        chapter_num = num_match.group(1) if num_match else "0"

                        chapters.append({
                            'id': chapter_url,
                            'manga_id': manga_url,
                            'manga_title': manga_title,
                            'chapter': chapter_num,
                            'title': chapter_title,
                            'group': 'Mangakakalot',
                            'url': chapter_url,
                            'hours_ago': round(hours_ago, 2) if hours_ago is not None else None
                        })

                if not chapters:
                    logger.info("No new chapters found: mangakakalot (none uploaded within the last 24 hours)")

            except Exception as e:
                logger.error(f"Mangakakalot get_latest_chapters failed: {e}")

        # Sort newest first
        chapters.sort(key=lambda x: x.get('hours_ago') or 999)

        return chapters[:limit]

    async def get_chapter_images(self, chapter_url: str) -> Optional[List[str]]:
        images = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(chapter_url, timeout=60) as resp:
                    if resp.status != 200:
                        return None
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    container = soup.find('div', class_='container-chapter-reader') or \
                                soup.find('div', class_='reading-content') or \
                                soup.find('div', class_='read-content')

                    if not container:
                        return None

                    img_tags = container.find_all('img')
                    for img in img_tags:
                        src = img.get('src') or img.get('data-src') or img.get('content')
                        if src and not src.lower().endswith('.gif') and 'logo' not in src.lower():
                            if not src.startswith('http'):
                                src = 'https:' + src if src.startswith('//') else urljoin(chapter_url, src)
                            images.append(src.strip())

            except Exception as e:
                logger.error(f"Mangakakalot get_chapter_images failed: {e}")

        return images if images else None

    async def get_manga_info(self, manga_id: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(manga_id, timeout=60) as resp:
                    if resp.status != 200:
                        return {'id': manga_id, 'title': 'Unknown', 'cover_url': None}
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    title_elem = soup.find('h1') or soup.find('h2')
                    title = title_elem.get_text(strip=True) if title_elem else 'Unknown'

                    cover_img = soup.find('div', class_='manga-info-pic')
                    cover_url = cover_img.find('img')['src'] if cover_img and cover_img.find('img') else None

                    return {'id': manga_id, 'title': title, 'cover_url': cover_url}
        except Exception as e:
            logger.error(f"Mangakakalot get_manga_info failed: {e}")
            return None

    async def get_chapter_info(self, chapter_id: str) -> Optional[Dict]:
        try:
            manga_id = '/'.join(chapter_id.split('/')[:-2]) + '/'

            chapter_num = "0"
            num_match = re.search(r'chapter[-/](\d+(?:\.\d+)?)', chapter_id, re.I)
            if num_match:
                chapter_num = num_match.group(1)

            return {
                'id': chapter_id,
                'chapter': chapter_num,
                'title': '',
                'manga_title': 'Unknown',
                'manga_id': manga_id
            }
        except Exception:
            return None

    async def search_manga(self, query: str, limit: int = 10) -> List[Dict]:
        results = []
        search_url = f"{self.base_url}/search/{query.replace(' ', '_')}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(search_url, timeout=60) as resp:
                    if resp.status != 200:
                        return []
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    items = soup.find_all('div', class_='story_item')[:limit]
                    for item in items:
                        a_tag = item.find('a')
                        if not a_tag:
                            continue
                        title = a_tag.get('title') or a_tag.get_text(strip=True)
                        href = a_tag['href']
                        img = item.find('img')
                        cover = img['src'] if img and img.get('src') else None

                        results.append({
                            'id': urljoin(self.base_url, href),
                            'title': title,
                            'description': f"Mangakakalot: {title}",
                            'cover_url': cover
                        })
            except Exception as e:
                logger.error(f"Mangakakalot search failed: {e}")

        return results

async def start_mangakakalot_polling(upload_handler, check_interval_minutes: int = 5):
    api = MangakakalotAPI()
    logger.info(f"Mangakakalot polling started - checking every {check_interval_minutes} minutes for new chapters within 24 hours.")
    while True:
        try:
            logger.info("Starting check for new Mangakakalot chapters...")
            chapters = await api.get_latest_chapters(limit=50)
            if chapters:
                logger.info(f"Found {len(chapters)} new chapters uploaded within the last 24 hours!")
                await upload_handler(chapters)
            else:
                logger.info("No new chapters uploaded within the last 24 hours.")
        except Exception as e:
            logger.error(f"Error during Mangakakalot polling: {e}")
        await asyncio.sleep(check_interval_minutes * 60)

