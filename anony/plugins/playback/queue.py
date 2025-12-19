# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import enums, filters, types

from anony import app, db, queue
from anony.helpers import buttons


@app.on_message(filters.command(["queue", "q"]) & filters.group & ~app.bl_users)
async def _queue(_, message: types.Message):
    from anony import config
    from anony.helpers import utils
    
    # Auto-delete command if enabled
    if config.AUTO_DELETE_COMMANDS:
        await utils.auto_delete(message)
    
    if not await db.get_call(message.chat.id):
        sent = await message.reply_text(
            "❌ <b>Tidak ada streaming</b>\n\n<blockquote>Gunakan /play untuk mulai memutar musik</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await utils.auto_delete(sent)
        return
    
    sent = await message.reply_text("🔄 <b>Mengambil Antrian...</b>", parse_mode=enums.ParseMode.HTML)
    
    playing = await db.playing(message.chat.id)
    items = queue.get_queue(message.chat.id)
    
    if not items:
        await sent.edit_text(
            "❌ <b>Antrian Kosong</b>\n\n<blockquote>Tidak ada lagu yang sedang menunggu</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await utils.auto_delete(sent)
        return
    
    # Pagination logic
    page = 0
    page_size = 20
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    start_idx = page * page_size
    end_idx = start_idx + page_size
    current_items = items[start_idx:end_idx]
    
    # Calculate total duration
    total_seconds = sum(item.duration_sec for item in items if hasattr(item, 'duration_sec'))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours > 0:
        total_duration = f"{hours}:{minutes:02d}:00"
    else:
        total_duration = f"{minutes}:00"
    
    # Build queue text
    text = f"📋 <b>Antrian Musik</b>\n\n"
    text += f"<b>Total:</b> {total_items} lagu • ⏱ {total_duration}\n\n"
    text += "<blockquote>"
    
    # Emoji numbers for first 10 items
    emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, item in enumerate(current_items, start=start_idx + 1):
        # Media type indicator
        media_icon = "🎬" if item.video else "🎵"
        
        # Use emoji number if available (only for 1-10), otherwise use regular number
        if i <= 10:
            num = emoji_numbers[i-1]
        else:
            num = f"{i}."
            
        text += f"{num} {media_icon} {item.title}\n"
    
    text += "</blockquote>"
    
    # Show remaining count if not on last page
    remaining = total_items - end_idx
    if remaining > 0:
        text += f"\n\n➕ <i>... dan {remaining} lagu lagi</i>"
    
    await sent.edit_text(
        text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=buttons.queue_markup(
            message.chat.id,
            "Sedang memutar" if playing else "Streaming dijeda",
            playing,
            page,
            total_pages
        )
    )
    await utils.auto_delete(sent)
