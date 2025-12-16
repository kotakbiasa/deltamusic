# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import anon, app, db, queue
from anony.helpers import admin_check


@app.on_message(filters.command(["seek"]) & filters.group & ~app.bl_users)
@admin_check
async def seek(_, message: types.Message):
    if not await db.get_call(message.chat.id):
        return await message.reply_text("Tidak ada streaming yang sedang diputar.")
    
    if len(message.command) < 2:
        return await message.reply_text("**Penggunaan:**\n\n/seek [detik]")
    
    try:
        seconds = int(message.command[1])
    except ValueError:
        return await message.reply_text("Masukkan angka yang valid.")
    
    media = queue.get_current(message.chat.id)
    if not media:
        return await message.reply_text("Tidak ada media yang sedang diputar.")
    
    m = await message.reply_text("Seeking...")
    await anon.play_media(message.chat.id, m, media, seek_time=seconds)
    await m.edit_text(f"Seek ke {seconds} detik.")
