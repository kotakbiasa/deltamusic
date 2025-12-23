# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import enums, filters, types

from delta import anon, app, db
from delta.helpers import admin_check, not_blacklisted


@app.on_message(filters.command(["pause"]) & filters.group & not_blacklisted)
@admin_check
async def pause(_, message: types.Message):
    if not await db.get_call(message.chat.id):
        return await message.reply_text(
            "❌ <b>Tidak ada streaming</b>\n\n<blockquote>Gunakan /play untuk mulai memutar musik</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    if not await db.playing(message.chat.id):
        return await message.reply_text(
            "⏸ <b>Streaming sudah dijeda</b>\n\n<blockquote>Gunakan /resume untuk melanjutkan</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    await anon.pause(message.chat.id)
    await message.reply_text(
        f"⏸ <b>Streaming Dijeda</b>\n\n<blockquote>{message.from_user.mention} menjeda streaming</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
