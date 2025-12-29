# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 

import logging
import aiohttp
import re
import asyncio
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib # Added for ID hashing

logger = logging.getLogger(__name__)

class AllMangaAPI:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://allmanga.to"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://allmanga.to/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.cookies = {}
        self.session = None
        self._semaphore = asyncio.Semaphore(5)
        self._seen_chapters = set()

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=60, connect=30, sock_read=30)
        connector = aiohttp.TCPConnector(limit=20, limit_per_host=5)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            cookies=self.cookies,
            timeout=timeout,
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            await asyncio.sleep(0.25)

    async def _make_request(self, url: str, retries: int = 3) -> Optional[str]:
        """Make HTTP request with retry logic"""
        async with self._semaphore:
            for attempt in range(retries):
                try:
                    async with self.session.get(url, ssl=False, allow_redirects=True) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        elif resp.status == 429:
                            wait_time = 2 ** attempt
                            logger.warning(f"Rate limited, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.warning(f"HTTP {resp.status} for {url}")
                            return None
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout attempt {attempt + 1}/{retries}")
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Request error: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
        return None

    async def parse_relative_time(self, time_text: str) -> Optional[datetime]:
        """Parse relative time strings like '2 hours ago'"""
        if not time_text:
            return None
        
        text = time_text.lower().strip()
        nums = re.search(r'(\d+)', text)
        if not nums:
            return None
        
        num = int(nums.group(1))
        now = datetime.now()
        
        if 'minute' in text or 'min' in text:
            return now - timedelta(minutes=num)
        elif 'hour' in text or 'hr' in text:
            return now - timedelta(hours=num)
        elif 'day' in text:
            return now - timedelta(days=num)
        elif 'week' in text:
            return now - timedelta(weeks=num)
        elif 'month' in text:
            return now - timedelta(days=num * 30)
        elif 'year' in text:
            return now - timedelta(days=num * 365)
        
        return None

    async def get_latest_chapters(self, limit: int = 50) -> List[Dict]:
        """Get latest manga chapters (last 24 hours only)"""
        all_chapters = []
        self._seen_chapters.clear()
        
        logger.info(f"Fetching latest chapters from AllManga (last 24 hours)")
        
        try:
            url = f"{self.base_url}/manga?cty=LATEST"
            logger.info(f"Fetching from {url}")
            
            html = await self._make_request(url)
            
            if not html:
                logger.error("Failed to fetch page")
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            
            manga_links = soup.find_all('a', href=re.compile(r'/manga/[a-zA-Z0-9]+$'))
            
            logger.info(f"Found {len(manga_links)} manga items on page")
            
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for manga_link in manga_links:
                if len(all_chapters) >= limit:
                    break
                
                try:
                    manga_url = urljoin(self.base_url, manga_link.get('href'))
                    manga_title = manga_link.get_text(strip=True)
                    
                    container = manga_link.find_parent()
                    if not container:
                        continue
                    
                    time_text = None
                    for sibling in container.find_all_next(string=re.compile(r'(ago|hour|minute|day)', re.I), limit=5):
                        if sibling:
                            time_text = sibling.strip()
                            break
                    
                    if not time_text:
                        all_text = container.get_text()
                        time_match = re.search(r'(\d+\s+(?:hour|minute|day)s?\s+ago)', all_text, re.I)
                        if time_match:
                            time_text = time_match.group(1)
                    
                    chapter_time = None
                    if time_text:
                        chapter_time = await self.parse_relative_time(time_text)
                        
                        if chapter_time and chapter_time < cutoff_time:
                            logger.debug(f"Skipping {manga_title} - older than 24h ({time_text})")
                            continue
                        
                        logger.info(f"✓ {manga_title} - {time_text}")
                    
                    chapter_link = None
                    for link in container.find_all_next('a', href=re.compile(r'/chapter-|chapter-\d+|-sub'), limit=3):
                        if link:
                            chapter_link = link
                            break
                    
                    if chapter_link:
                        chapter_url = urljoin(self.base_url, chapter_link.get('href'))
                        chapter_text = chapter_link.get_text(strip=True)
                        
                        chapter_num = '0'
                        patterns = [
                            r'chapter[\s-]+(\d+(?:\.\d+)?)',
                            r'ch[\s.-]+(\d+(?:\.\d+)?)',
                            r'(\d+(?:\.\d+)?)'
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, chapter_text, re.I)
                            if match:
                                chapter_num = match.group(1)
                                break
                        
                                break
                        
                        chap_id_hash = hashlib.md5(chapter_url.encode()).hexdigest()

                        chapter_data = {
                            'id': chap_id_hash,
                            'manga_id': manga_url, # Manga ID is usually URL
                            'manga_title': manga_title,
                            'chapter': chapter_num,
                            'title': '',
                            'group': 'AllManga',
                            'url': chapter_url,
                            'timestamp': chapter_time
                        }
                        
                        if chap_id_hash not in self._seen_chapters:
                            self._seen_chapters.add(chap_id_hash)
                            all_chapters.append(chapter_data)
                            logger.info(f"✓ Added: {manga_title} Chapter {chapter_num}")
                
                except Exception as e:
                    logger.error(f"Error parsing manga item: {e}", exc_info=True)
                    continue
            
        except Exception as e:
            logger.error(f"AllManga get_latest_chapters failed: {e}", exc_info=True)
        
        logger.info(f"Returning {len(all_chapters)} chapters from last 24 hours")
        return all_chapters[:limit]

    async def get_chapter_images(self, chapter_url: str) -> Optional[List[str]]:
        """Get all image URLs from a chapter"""
        html = await self._make_request(chapter_url)
        if not html:
            return None
        
        images = []
        soup = BeautifulSoup(html, 'html.parser')
        
        img_selectors = [
            '.chapter-image img',
            '.reader img',
            'img.page-image',
            '.page-image img',
            '#chapter-reader img',
            '.reader-content img',
            '#viewer img',
            '.viewer img',
            '.reading-content img',
            '.manga-page img',
            'img[data-src]',
            'img[data-lazy-src]',
            '.img-container img',
            '#reader img',
            '.chapter-img img',
            '.read-img img',
            'div.reading-content img'
        ]
        
        imgs = []
        for selector in img_selectors:
            found = soup.select(selector)
            if found:
                logger.info(f"Found {len(found)} images using selector: {selector}")
                imgs = found
                break
        
        if not imgs:
            logger.info(f"No specific selector matched. Fallback: scanning all {len(soup.find_all('img'))} <img> tags")
            imgs = soup.find_all('img')
        
        seen = set()
        for img in imgs:
            src = (img.get('data-src') or img.get('data-lazy-src') or 
                   img.get('data-original') or img.get('data-url') or 
                   img.get('data-image') or img.get('data-full') or
                   img.get('src'))
            
            if not src:
                continue
            
            src = src.strip()
            
            if src.startswith('//'):
                full_src = 'https:' + src
            elif src.startswith('http'):
                full_src = src
            else:
                full_src = urljoin(chapter_url, src)
            
            if not self._is_valid_image_url(full_src):
                logger.debug(f"Skipped non-image URL: {full_src}")
                continue
            
            if full_src not in seen:
                seen.add(full_src)
                images.append(full_src)
                logger.debug(f"Added image: {full_src}")
        
        logger.info(f"Extracted {len(images)} valid image URLs")
        if not images:
            logger.warning("No valid chapter images found. Site may use heavy JavaScript loading.")
        
        return images if images else None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Strict validation: must be a direct image URL with valid extension"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        if any(char in url for char in [' ', '\n', '\t']):
            return False
        
        return bool(re.search(r'\.(jpg|jpeg|png|gif|webp|avif|bmp)(\?.*)?$', url, re.IGNORECASE))

    async def get_manga_info(self, manga_id: str) -> Optional[Dict]:
        """Get manga information"""
        html = await self._make_request(manga_id)
        if not html:
            return {'id': manga_id, 'title': 'Unknown', 'cover_url': None}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        title = "Unknown"
        title_elem = (soup.select_one('.manga-title h1') or 
                     soup.select_one('h1.title') or 
                     soup.select_one('.title h1') or
                     soup.find('h1'))
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        cover_url = None
        cover_selectors = ['.manga-cover img', '.cover img', 'img.cover', 
                          '.thumbnail img', '.poster img', 'img[alt*="cover"]']
        
        for selector in cover_selectors:
            cover_elem = soup.select_one(selector)
            if cover_elem:
                src = (cover_elem.get('src') or cover_elem.get('data-src') or
                      cover_elem.get('data-lazy-src'))
                if src:
                    if src.startswith('//'):
                        cover_url = 'https:' + src
                    elif src.startswith('http'):
                        cover_url = src
                    else:
                        cover_url = urljoin(self.base_url, src)
                    
                    if self._is_valid_image_url(cover_url):
                        break
                    else:
                        cover_url = None
        
        return {'id': manga_id, 'title': title, 'cover_url': cover_url}

    async def get_chapter_info(self, chapter_id: str) -> Optional[Dict]:
        """Get chapter information"""
        html = await self._make_request(chapter_id)
        if not html:
            return {
                'id': chapter_id,
                'chapter': '0',
                'title': '',
                'manga_title': 'Unknown',
                'manga_id': chapter_id
            }
        
        soup = BeautifulSoup(html, 'html.parser')
        
        manga_title = "Unknown"
        manga_id = chapter_id
        
        series_link = (soup.select_one('a.series-link') or 
                      soup.select_one('.breadcrumb a[href*="/manga/"]') or
                      soup.find('a', href=re.compile(r'/manga/[a-zA-Z0-9]+$')))
        
        if series_link:
            manga_title = series_link.get_text(strip=True)
            manga_id = urljoin(self.base_url, series_link.get('href'))
        
        chapter_num = "0"
        patterns = [
            r'chapter[-_/](\d+(?:\.\d+)?)',
            r'/c(\d+(?:\.\d+)?)',
            r'ch(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, chapter_id, re.I)
            if match:
                chapter_num = match.group(1)
                break
        
        return {
            'id': chapter_id,
            'chapter': chapter_num,
            'title': '',
            'manga_title': manga_title,
            'manga_id': manga_id
        }

    async def search_manga(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for manga by query"""
        results = []
        search_url = f"{self.base_url}/search?q={quote(query)}"
        
        html = await self._make_request(search_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.manga-item, .search-item, .series-item')
        
        for item in items[:limit]:
            title_elem = item.select_one('.manga-title, .title')
            link_elem = item.select_one('a')
            
            if title_elem and link_elem:
                cover_elem = item.select_one('img')
                cover_url = None
                
                if cover_elem:
                    src = (cover_elem.get('src') or cover_elem.get('data-src') or
                          cover_elem.get('data-lazy-src'))
                    
                    if src:
                        if src.startswith('//'):
                            cover_url = 'https:' + src
                        elif src.startswith('http'):
                            cover_url = src
                        else:
                            cover_url = urljoin(self.base_url, src)
                        
                        if not self._is_valid_image_url(cover_url):
                            cover_url = None
                
                results.append({
                    'id': urljoin(self.base_url, link_elem.get('href')),
                    'title': title_elem.get_text(strip=True),
                    'description': 'AllManga',
                    'cover_url': cover_url
                })
        
        return results

# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
