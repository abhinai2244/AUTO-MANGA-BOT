# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat

import logging
import asyncio
import aiohttp
import aiofiles
import gc
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont, ImageColor
import zipfile
import zipfile
import re
import pypdf # Added for PDF password protection

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, Config):
        self.Config = Config

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=120, connect=30)
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://mangadex.org/'},
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            await asyncio.sleep(0.25)

    async def download_image(self, url: str, output_path: Path, max_retries: int = 3, headers: dict = None) -> bool:
        for attempt in range(max_retries):
            try:
                request_headers = headers if headers else self.session.headers
                async with self.session.get(url, headers=request_headers) as response:
                    if response.status == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()

                    size = 0
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            size += len(chunk)
                            if size > self.Config.MAX_IMAGE_SIZE:
                                logger.error(f"Image too large: {size} bytes")
                                return False
                            await f.write(chunk)
                    return True
            except Exception as e:
                logger.error(f"Download failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        return False

    async def download_images(self, urls: List[str], output_dir: Path, progress_callback=None, headers: dict = None) -> bool:
        output_dir.mkdir(parents=True, exist_ok=True)
        batch_size = 10
        successful = 0

        for i in range(0, len(urls), batch_size):
            tasks = []
            for j, url in enumerate(urls[i:i + batch_size], i + 1):
                output_path = output_dir / f"{j:03d}.jpg"
                tasks.append(self.download_image(url, output_path, headers=headers))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful += sum(1 for r in results if r is True)
            
            if progress_callback:
                try:
                    await progress_callback(successful, len(urls))
                except Exception:
                    pass
                    
            gc.collect()
            await asyncio.sleep(0.5)

        success_rate = successful / len(urls)
        logger.info(f"Downloaded {successful}/{len(urls)} images ({success_rate:.1%})")
        return success_rate >= 0.8

    def create_pdf(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str) -> Optional[Path]:
        try:
            base_name = f"{manga_title} - Ch {chapter_num}"
            if chapter_title:
                base_name += f" - {chapter_title}"
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))[:100]
            pdf_path = chapter_dir.parent / f"{safe_name}.pdf"

            img_files = sorted(chapter_dir.glob("*.jpg"))
            if not img_files:
                return None

            images_to_save = []
            first_image = None

            for i, img_path in enumerate(img_files):
                img = Image.open(img_path)
                if img.width > 2000 or img.height > 2000:
                    ratio = min(2000 / img.width, 2000 / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                if i == 0:
                    first_image = img
                else:
                    images_to_save.append(img)

                if i % 20 == 0:
                    gc.collect()

            if not first_image:
                return None

            first_image.save(
                pdf_path, "PDF", resolution=72.0, save_all=True,
                append_images=images_to_save, optimize=True
            )

            if pdf_path.stat().st_size > self.Config.MAX_PDF_SIZE:
                logger.error(f"PDF too large: {pdf_path.stat().st_size} bytes")
                pdf_path.unlink()
                return None

            for img in images_to_save:
                img.close()
            first_image.close()
            gc.collect()

            return pdf_path
        except Exception as e:
            logger.error(f"PDF creation failed: {e}")
            return None

            return pdf_path
        except Exception as e:
            logger.error(f"PDF creation failed: {e}")
            return None

    def create_cbz(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str, intro: Path = None, outro: Path = None, quality: int = None) -> Optional[Path]:
        try:
            base_name = f"{manga_title} - Ch {chapter_num}"
            if chapter_title:
                base_name += f" - {chapter_title}"
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))[:100]
            cbz_path = chapter_dir.parent / f"{safe_name}.cbz"

            img_files = sorted(chapter_dir.glob("*.jpg"))
            if not img_files:
                return None
            
            final_images = []
            if intro and intro.exists(): final_images.append(intro)
            final_images.extend(img_files)
            if outro and outro.exists(): final_images.append(outro)

            with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
                for idx, img_path in enumerate(final_images):
                    if quality is not None:
                         try:
                             with Image.open(img_path) as img:
                                 if img.mode != 'RGB': img = img.convert('RGB')
                                 with cbz.open(f"{idx:04d}.jpg", "w") as zf:
                                     img.save(zf, "JPEG", quality=quality, optimize=True)
                         except:
                             cbz.write(img_path, arcname=f"{idx:04d}.jpg")
                    else:
                        cbz.write(img_path, arcname=f"{idx:04d}.jpg")
            
            return cbz_path
        except Exception as e:
            logger.error(f"CBZ creation failed: {e}")
            return None

    def create_chapter_file(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str, file_type: str = "pdf", intro: Path = None, outro: Path = None, quality: int = None, watermark: dict = None, password: str = None) -> Optional[Path]:
        """Dispatcher for creating chapter file based on type"""
        if file_type.lower() == "cbz":
            return self.create_cbz(chapter_dir, manga_title, chapter_num, chapter_title, intro, outro, quality)
        else:
            return self.create_pdf_v2(chapter_dir, manga_title, chapter_num, chapter_title, intro, outro, quality, watermark, password=password)

    def apply_watermark(self, img: Image.Image, watermark: dict) -> Image.Image:
        if not watermark or not watermark.get("text"):
            return img
        
        try:
            draw = ImageDraw.Draw(img, "RGBA")
            text = watermark["text"]
            position = watermark.get("position", "bottom-right")
            color_hex = watermark.get("color", "#FFFFFF")
            opacity = int(watermark.get("opacity", 128))
            font_size = int(watermark.get("font_size", 30))
            
            try:
                rgb = ImageColor.getrgb(color_hex)
            except:
                rgb = (255, 255, 255)
            
            fill_color = (*rgb, opacity)
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            width, height = img.size
            padding = 20
            
            x, y = 0, 0
            if position == "top-left":
                x, y = padding, padding
            elif position == "top-right":
                x, y = width - text_width - padding, padding
            elif position == "bottom-left":
                x, y = padding, height - text_height - padding
            elif position == "bottom-right":
                x, y = width - text_width - padding, height - text_height - padding
            elif position == "center":
                x, y = (width - text_width) // 2, (height - text_height) // 2
                
            draw.text((x, y), text, font=font, fill=fill_color)
            return img
        except Exception as e:
            logger.error(f"Watermark apply failed: {e}")
            return img

    def apply_password(self, pdf_path: Path, password: str) -> bool:
        """Apply password protection to PDF"""
        if not password: return True
        try:
            reader = pypdf.PdfReader(pdf_path)
            writer = pypdf.PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            temp_path = pdf_path.with_suffix('.temp.pdf')
            with open(temp_path, "wb") as f:
                writer.write(f)
            
            pdf_path.unlink() # Delete unprotected
            temp_path.rename(pdf_path) # Move protected
            return True
        except Exception as e:
            logger.error(f"Password protection failed: {e}")
            return False

    def create_pdf_v2(self, chapter_dir: Path, manga_title: str, chapter_num: str, chapter_title: str, intro: Path = None, outro: Path = None, quality: int = None, watermark: dict = None, password: str = None) -> Optional[Path]:
         try:
            clean_title = re.sub(r'\[Ch-.*?\]', '', manga_title, flags=re.IGNORECASE)
            clean_title = re.sub(r'\s*-\s*Chapter\s*\d+', '', clean_title, flags=re.IGNORECASE)
            clean_title = clean_title.strip()
            
            base_name = f"{clean_title} - Ch {chapter_num}"
            if chapter_title:
                base_name += f" - {chapter_title}"
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))[:100]
            pdf_path = chapter_dir.parent / f"{safe_name}.pdf"

            img_files = sorted(chapter_dir.glob("*.jpg"))
            if not img_files:
                return None

            final_images = []
            if intro and intro.exists(): final_images.append(intro)
            final_images.extend(img_files)
            if outro and outro.exists(): final_images.append(outro)

            images_to_save = []
            first_image = None
            
            q = quality if quality is not None else 85
            
            for i, img_path in enumerate(final_images):
                img = Image.open(img_path)
                if img.width > 2000 or img.height > 2000:
                    ratio = min(2000 / img.width, 2000 / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                if watermark:
                    img = self.apply_watermark(img, watermark)

                if i == 0:
                    first_image = img
                else:
                    images_to_save.append(img)

                if i % 20 == 0:
                    gc.collect()

            if not first_image:
                return None

            first_image.save(
                pdf_path, "PDF", resolution=72.0, save_all=True,
                append_images=images_to_save, optimize=True, quality=q
            )
            
            for img in images_to_save: img.close()
            first_image.close()
            gc.collect()
            
            for img in images_to_save: img.close()
            first_image.close()
            gc.collect()
            
            if password:
                self.apply_password(pdf_path, password)
            
            return pdf_path
         except Exception as e:
             logger.error(f"PDF v2 failed: {e}")
             return None

    async def download_cover(self, cover_url: str, output_path: Path, headers: dict = None) -> bool:
        if not cover_url:
            return False
        return await self.download_image(cover_url, output_path, headers=headers)


# Rexbots
# Don't Remove Credit
# Telegram Channel @CantarellaBots
#Supoort group @rexbotschat