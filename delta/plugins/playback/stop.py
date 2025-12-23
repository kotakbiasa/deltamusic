# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import enums, filters, types

from delta import anon, app, db
from delta.helpers import admin_check, not_blacklisted


@app.on_message(filters.command(["stop", "end"]) & filters.group & not_blacklisted)
@admin_check
async def stop(_, message: types.Message):
    if not await db.get_call(message.chat.id):
        return await message.reply_text(
            "❌ <b>Tidak ada streaming</b>\n\n<blockquote>Gunakan /play untuk mulai memutar musik</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    await anon.stop(message.chat.id)
    await message.reply_text(
        f"⏹ <b>Streaming Dihentikan</b>\n\n<blockquote>{message.from_user.mention} menghentikan streaming</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
