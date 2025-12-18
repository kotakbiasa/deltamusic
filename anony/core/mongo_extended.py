# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

"""
Enhanced MongoDB with daily tracking for dashboard
"""

from datetime import datetime
from anony.core.mongo import MongoDB as OriginalMongoDB


class MongoDB(OriginalMongoDB):
    """Extended MongoDB with daily stats tracking"""
    
    def __init__(self):
        super().__init__()
        self.daily_statsdb = self.db.daily_stats
    
    async def add_stats(self, track_id: str, title: str, duration: str, user_id: int, chat_id: int) -> None:
        """Add or update play statistics with daily tracking"""
        # Call parent method
        await super().add_stats(track_id, title, duration, user_id, chat_id)
        
        # Add daily tracking
        today = datetime.now().strftime("%Y-%m-%d")
        await self.daily_statsdb.update_one(
            {"_id": today},
            {
                "$inc": {
                    "total_plays": 1,
                    f"tracks.{track_id}": 1,
                    f"users.{user_id}": 1,
                    f"chats.{chat_id}": 1
                }
            },
            upsert=True
        )
    
    async def get_daily_play_count(self, days: int = 7) -> list[dict]:
        """Get play count for the last N days"""
        from datetime import timedelta
        
        result = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            date_str = date.strftime("%Y-%m-%d")
            
            doc = await self.daily_statsdb.find_one({"_id": date_str})
            play_count = doc.get("total_plays", 0) if doc else 0
            
            result.append({
                "date": date_str,
                "play_count": play_count
            })
        
        return result
    
    async def get_hourly_stats(self, date: str = None) -> dict:
        """Get hourly breakdown for a specific date"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # This requires more granular tracking
        # Placeholder for future implementation
        return {}
