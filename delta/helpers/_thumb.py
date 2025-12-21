# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
import aiohttp
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from delta import logger


class ThumbGenerator:
    def __init__(self):
        self.cache_dir = Path("cache/thumbs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Default colors (gradient purple to pink)
        self.gradient_start = (147, 51, 234)  # Purple
        self.gradient_end = (236, 72, 153)    # Pink
        
        # Thumbnail size
        self.width = 1280
        self.height = 720
        
    def _create_gradient_background(self):
        """Create vertical gradient background."""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for i in range(self.height):
            # Calculate gradient color
            ratio = i / self.height
            r = int(self.gradient_start[0] + (self.gradient_end[0] - self.gradient_start[0]) * ratio)
            g = int(self.gradient_start[1] + (self.gradient_end[1] - self.gradient_start[1]) * ratio)
            b = int(self.gradient_start[2] + (self.gradient_end[2] - self.gradient_start[2]) * ratio)
            
            draw.line([(0, i), (self.width, i)], fill=(r, g, b))
        
        return img
    
    def _round_corners(self, img, radius=30):
        """Add rounded corners to image."""
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
        
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        return output
    
    def _add_glow(self, img, glow_size=20):
        """Add glow effect around image."""
        # Create larger canvas
        glow_img = Image.new('RGBA', 
                            (img.width + glow_size * 2, img.height + glow_size * 2),
                            (0, 0, 0, 0))
        
        # Paste original image
        glow_img.paste(img, (glow_size, glow_size), img)
        
        # Apply blur for glow effect
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=glow_size // 2))
        
        return glow_img
    
    async def _download_image(self, url):
        """Download image from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return Image.open(BytesIO(data)).convert('RGB')
        except Exception as e:
            logger.error(f"Failed to download thumbnail: {e}")
        return None
    
    async def generate(self, track) -> str:
        """Generate thumbnail for a track."""
        try:
            # Check cache first
            cache_file = self.cache_dir / f"{track.id}.jpg"
            if cache_file.exists():
                return str(cache_file)
            
            # Create gradient background
            base = self._create_gradient_background()
            
            # Download and process album art
            if track.thumbnail:
                album_art = await self._download_image(track.thumbnail)
                if album_art:
                    # Resize album art (square)
                    art_size = 400
                    album_art = album_art.resize((art_size, art_size), Image.Resampling.LANCZOS)
                    
                    # Round corners
                    album_art = self._round_corners(album_art, radius=40)
                    
                    # Add glow
                    album_art_glow = self._add_glow(album_art, glow_size=25)
                    
                    # Paste on background (centered vertically, left aligned)
                    x_pos = 100
                    y_pos = (self.height - album_art_glow.height) // 2
                    base.paste(album_art_glow, (x_pos, y_pos), album_art_glow)
            
            # Add text overlays
            draw = ImageDraw.Draw(base)
            
            # Load fonts (try to use custom, fallback to default)
            try:
                title_font = ImageFont.truetype("arial.ttf", 60)
                artist_font = ImageFont.truetype("arial.ttf", 40)
                duration_font = ImageFont.truetype("arial.ttf", 35)
            except:
                title_font = ImageFont.load_default()
                artist_font = ImageFont.load_default()
                duration_font = ImageFont.load_default()
            
            # Text position
            text_x = 600
            title_y = 200
            
            # Song title (with shadow)
            title = track.title[:40] + "..." if len(track.title) > 40 else track.title
            # Shadow
            draw.text((text_x + 3, title_y + 3), title, font=title_font, fill=(0, 0, 0, 128))
            # Main text
            draw.text((text_x, title_y), title, font=title_font, fill=(255, 255, 255))
            
            # Artist name
            artist = track.channel_name[:35] + "..." if len(track.channel_name) > 35 else track.channel_name
            artist_y = title_y + 80
            draw.text((text_x + 2, artist_y + 2), f"🎤 {artist}", font=artist_font, fill=(0, 0, 0, 100))
            draw.text((text_x, artist_y), f"🎤 {artist}", font=artist_font, fill=(255, 255, 255, 230))
            
            # Duration
            duration_y = artist_y + 60
            draw.text((text_x + 2, duration_y + 2), f"⏱️ {track.duration}", font=duration_font, fill=(0, 0, 0, 100))
            draw.text((text_x, duration_y), f"⏱️ {track.duration}", font=duration_font, fill=(255, 255, 255, 200))
            
            # Add play icon/badge
            badge_y = duration_y + 80
            draw.rounded_rectangle(
                [(text_x, badge_y), (text_x + 150, badge_y + 60)],
                radius=30,
                fill=(255, 255, 255, 50),
                outline=(255, 255, 255, 100),
                width=2
            )
            draw.text((text_x + 30, badge_y + 10), "▶️ PLAY", font=duration_font, fill=(255, 255, 255))
            
            # Save to cache
            base = base.convert('RGB')
            base.save(cache_file, 'JPEG', quality=95)
            logger.info(f"Generated thumbnail: {cache_file}")
            
            return str(cache_file)
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return None


# Global instance
thumb = ThumbGenerator()
