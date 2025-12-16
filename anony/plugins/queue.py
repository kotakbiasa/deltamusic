# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db, queue
from anony.helpers import buttons


@app.on_message(filters.command(["queue", "q"]) & filters.group & ~app.bl_users)
async def _queue(_, message: types.Message):
    if not await db.get_call(message.chat.id):
        return await message.reply_text("Tidak ada streaming yang sedang diputar.")
    
    await message.reply_text("Mengambil antrian...")
    
    playing = await db.playing(message.chat.id)
    items = queue.get(message.chat.id)
    
    if not items:
        return await message.reply_text("Antrian kosong.")
    
    text = "**Antrian:**\n\n"
    for i, item in enumerate(items[:10], 1):
        text += f"{i}. {item.title}\n"
    
    if len(items) > 10:
        text += f"\n... dan {len(items) - 10} lagi"
    
    await message.reply_text(
        text,
        reply_markup=buttons.queue_markup(
            message.chat.id,
            "Sedang memutar" if playing else "Streaming dijeda",
            playing
        )
    )
