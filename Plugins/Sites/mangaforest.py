# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

import logging
import asyncio
import aiohttp
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MangaForestAPI:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://mangaforest.me"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://mangaforest.me/'
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get_latest_chapters(self, limit: int = 50) -> List[Dict]:
        chapters = []
        url = self.base_url 
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=30) as resp:
                    if resp.status != 200: return []
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    
                    chapter_headers = soup.find_all("h4")
                    for ch_head in chapter_headers:
                        ch_link = ch_head.find("a")
                        if not ch_link: continue
                        
                        chapter_url = ch_link.get("href")
                        chapter_title = ch_link.get_text(strip=True) # e.g. "Chapter 41"
                        
                        manga_head = ch_head.find_previous("h3")
                        if not manga_head: continue
                        
                        manga_link = manga_head.find("a")
                        if not manga_link: continue
                        
                        manga_url = manga_link.get("href")
                        manga_title = manga_link.get_text(strip=True)
                        
                        chapter_url = urljoin(self.base_url, chapter_url)
                        manga_url = urljoin(self.base_url, manga_url)
                        
                        chapter_id = chapter_url
                        
                        try:
                            num = re.search(r"Chapter\s*(\d+(?:\.\d+)?)", chapter_title, re.I)
                            chapter_num = num.group(1) if num else "0"
                        except:
                            chapter_num = "0"

                        chapters.append({
                            'id': chapter_id,
                            'manga_id': manga_url,
                            'manga_title': manga_title,
                            'chapter': chapter_num,
                            'title': chapter_title,
                            'group': 'MangaForest',
                            'url': chapter_url
                        })
                        
                        if len(chapters) >= limit:
                            break
            except Exception as e:
                logger.error(f"MangaForest get_latest failed: {e}")
        
        return chapters

    async def get_chapter_images(self, chapter_url: str) -> Optional[List[str]]:
        images = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
             try:
                async with session.get(chapter_url, timeout=30) as resp:
                    if resp.status != 200: return None
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    divs = soup.find_all('div', class_='chapter-image')
                    img_elements = []
                    for div in divs:
                        img = div.find('img')
                        if img:
                            img_elements.append(img)
                    
                    if not img_elements:
                         img_elements = soup.find_all('img', attrs={'data-src': True})
                    
                    for img in img_elements:
                        src = img.get('data-src') or img.get('src')
                        if src and "http" in src:
                            images.append(src)
                        elif src:
                            images.append(urljoin(self.base_url, src))
             except Exception as e:
                 logger.error(f"MangaForest DL failed: {e}")
                 return None
        return images
    
    async def search_manga(self, query: str, limit: int = 10) -> List[Dict]:
        return []
    async def get_manga_chapters(self, manga_id: str, limit: int = 20, offset: int = 0, languages: list = ['en']) -> List[Dict]:
        return []
    async def get_manga_info(self, manga_id: str) -> Optional[Dict]:
        try:
             async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(manga_id, timeout=30) as resp:
                    if resp.status != 200: return None
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    title = "Unknown"
                    h1 = soup.find("h1")
                    if h1: title = h1.get_text(strip=True)
                    
                    cover_url = None
                    og_img = soup.find("meta", property="og:image")
                    if og_img:
                        cover_url = og_img.get("content")
                    
                    return {'id': manga_id, 'title': title, 'cover_url': cover_url}
        except Exception as e:
            logger.error(f"MangaForest get_manga_info failed: {e}")
            return None

    async def get_chapter_info(self, chapter_id: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(chapter_id, timeout=30) as resp:
                    if resp.status != 200: return None
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    
                    manga_title = None
                    chapter_num = "0"
                    title = ""
                    
                    crumbs = soup.select(".breadcrumb li a")
                    if len(crumbs) >= 2:
                        for cr in crumbs:
                            if "/manga/" in cr.get("href", ""):
                                manga_title = cr.get_text(strip=True)
                                break
                    
                    if not manga_title:
                        h1 = soup.find("h1")
                        if h1:
                            full_text = h1.get_text(strip=True)
                            if "Chapter" in full_text:
                                parts = full_text.split("Chapter")
                                manga_title = parts[0].strip()
                            else:
                                manga_title = full_text # Fallback
                    
                    match = re.search(r"chapter-(\d+(?:\.\d+)?)", chapter_id)
                    if match:
                        chapter_num = match.group(1)
                    else:
                        match = re.search(r"Chapter\s+(\d+(?:\.\d+)?)", soup.title.string if soup.title else "", re.I)
                        if match:
                            chapter_num = match.group(1)
                            
                    return {
                        'id': chapter_id,
                        'chapter': chapter_num,
                        'title': '', # Chapter title usually empty unless "Episode X"
                        'manga_title': manga_title or "Unknown",
                        'manga_id': chapter_id # Fallback
                    }
        except Exception as e:
            logger.error(f"MangaForest get_chapter_info failed: {e}")
            return None


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat